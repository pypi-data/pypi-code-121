import logging
import sys
import threading
import traceback

try:
    import Queue as queue
except ImportError: 
    import queue

import ciocore

logger = logging.getLogger("{}.worker".format(ciocore.common.CONDUCTOR_LOGGER_NAME))

# This is used to signal to workers if work should continue or not
WORKING = True

class Reporter():
    def __init__(self, metric_store=None):
        self.metric_store = metric_store
        self.api_helper = ciocore.api_client.ApiClient()
        self.thread = None
        self.terminate = False

    def kill(self, block=False):
        self.terminate = True
        if block:
            logger.debug('joining reporter thread...')
            self.thread.join()
            logger.debug('reporter_thread exited')

    @staticmethod
    def working():
        return WORKING

    def target(self):
        raise NotImplementedError

    def start(self):
        if self.thread:
            logger.error('threads already started. will not start more')
            return self.thread

        logger.debug('starting reporter thread')
        thd = threading.Thread(target=self.target, name=self.__class__.__name__)
        thd.daemon = True
        thd.start()
        self.thread = thd
        return self.thread
    
    
class ThreadWorker(object):
    '''
    Abstract worker class.

    The class defines the basic function and data structures that all workers need.

    TODO: move this into it's own lib
    '''
    
    def __init__(self, **kwargs):

        # the in_queue provides work for us to do
        self.in_queue = kwargs['in_queue']

        # results of work are put into the out_queue
        self.out_queue = kwargs['out_queue']

        # exceptions will be put here if provided
        self.error_queue = kwargs['error_queue']

        # set the thread count (default: 1)
        self.thread_count = int(kwargs.get('thread_count', 1))

        # an optional metric store to share counters between threads
        self.metric_store = kwargs['metric_store']

        # create a list to hold the threads that we create
        self.threads = []
        
        self.thread_complete_counter = Counter()
        self._worker_started = Marker()
        self._job_counter = Counter()

    def do_work(self, job):
        '''
        This needs to be implemented for each worker type. The work task from the in_queue is passed
        as the job argument.

        Returns the result to be passed to the out_queue
        '''

        raise NotImplementedError

    @staticmethod
    def PoisonPill():
        return 'PoisonPill'

    def check_for_poison_pill(self, job):
        if job == self.PoisonPill():
            self.mark_done()
            exit()

    def kill(self, block=False):
        logger.debug('killing workers %s (%s threads)', self.__class__.__name__, len(self.threads))
        for _ in self.threads:
            self.in_queue.put(self.PoisonPill())

        if block:
            for index, thd in enumerate(self.threads):
                logger.debug('waiting for thread %s (%s)', index, self)
                thd.join(0.1)
                logger.debug('thread %s (%s) joined', index, self)

        return True

    def join(self):
        logger.debug("Waiting for in_queue to join. ({}-{}). {} items left.".format(self.__class__.__name__, self, self.in_queue.qsize()))
        
        while True:
            try:
                logger.debug("Getting remaining task from in_queue ({}-{}). {} items left.".format(self.__class__.__name__, self, self.in_queue.qsize()))
                job = self.in_queue.get(block=False)
                logger.debug("Dropping task {} from in_queue ({}-{}). {} items left.".format(job, self.__class__.__name__, self, self.in_queue.qsize()))
                self.in_queue.task_done()
            except queue.Empty:
                logger.debug("in_queue is empty ({}-{}). {} items left.".format(self.__class__.__name__, self, self.in_queue.qsize()))
                break

        self.kill(True)

    # Basic thread target loop.
    @ciocore.common.dec_catch_exception(raise_=True)
    def target(self, thread_int):

        while not ciocore.common.SIGINT_EXIT:
            try:
                
                job = None

                try:
                    logger.debug("Worker querying for job")
                    job = self.in_queue.get(timeout=2)
                    queue_size = self.in_queue.qsize()                     

                except queue.Empty:
                    
                    if self._job_counter.value > 0:
                        logger.debug("Worker has completed all of its tasks.".format(job))
                        self.thread_complete_counter.decrement()
                        break
                    
                    else:
                        logger.debug("Worker waiting for first job")
                        continue
                    
                logger.debug("Worker got job {}".format(job))
                self._job_counter.increment()
                logger.debug("Processing Job '{}' #{} on {}. {} tasks remaining in queue".format( job, 
                                                                                                  self._job_counter.value, 
                                                                                                  self, 
                                                                                                  queue_size))
                
                # exit if we were passed 'PoisonPill'
                self.check_for_poison_pill(job)

                # start working on job
                try:
                    output = None
                    output = self.do_work(job, thread_int)
                except Exception as exception:
                    logger.exception('CAUGHT EXCEPTION on job "{}" [{}]":\n'.format(job, self))

                    # if there is no error queue to dump data into, then simply raise the exception
                    if not self.error_queue:
                        raise

                    # Otherwise put the exception in the error queue
                    self.mark_done()
                    self.error_queue.put(sys.exc_info())
                    # exit the while loop to stop the thread
                    break

                # put result in out_queue
                self.put_job(output)

                # signal that we are done with this task (needed for the Queue.join() operation to
                # work.
                self.mark_done()

            except Exception:
                logger.error('[thread %s]+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=', thread_int)
                logger.error(traceback.print_exc())
                logger.error(traceback.format_exc())
                raise
        
        logger.info("Worker {} completed".format(self))

    def start(self):
        '''
        Start number_of_threads threads.
        '''
        if self.threads:
            logger.error('threads already started. will not start more')
            return self.threads

        for thread_int in range(self.thread_count):
            name = "%s-%s" % (self.__class__.__name__, thread_int)
            logger.debug('starting thread %s', name)
            
            # thread will begin execution on self.target()
            thd = threading.Thread(target=self.target, args=(thread_int,), name=name)

            # make sure threads don't stop the program from exiting
            thd.daemon = True

            # start thread
            thd.start()
            self.threads.append(thd)
            
        self.thread_complete_counter.value = self.thread_count

        return self.threads

    def mark_done(self):
        try:
            self.in_queue.task_done()
            
        except ValueError:
            # this will happen if we are draining queues
            logger.debug('WORKING: %s', WORKING)
            
            if WORKING:
                logger.error('error hit when marking task_done')
                # this should not happen if we are still working
                raise
        return

    def put_job(self, job):
        # don't to anything if we were not provided an out_queue
        logger.debug("Attempting to put job to out_queue ({} -> {})".format(job,self, self.out_queue))
        
        if not self.out_queue:
            return

        # if were not supposed to be working, don't create new jobs
        if not WORKING:
            return
        
        logger.debug("Adding job to out_queue ({} -> {})".format(job,self, self.out_queue))
        
        # add item to job
        self.out_queue.put(job)
        return True
    
    def is_complete(self):        
        return self.thread_complete_counter.value == 0
            

class MetricStore():
    '''
    This provides a thread-safe integer store that can be used by workers to share atomic counters.

    Note: writes are eventually consistent
    '''

    def __init__(self):
        self.metric_store = {}
        self.update_queue = queue.Queue()
        self.thread = None
        self.started = False

    def join(self):
        self.update_queue.join()
        self.thread.join()
        return True

    def start(self):
        '''
        needs to be single-threaded for atomic updates
        '''
        if self.started:
            logger.debug('metric_store already started')
            return None
        
        logger.debug('starting metric_store')
        
        self.stop = False
        self.thread = threading.Thread(target=self.target, name=self.__class__.__name__)
        self.thread.daemon = True
        self.thread.start()
        self.started = True
        
        return self.thread

    def set(self, key, value):
        self.metric_store[key] = value

    def get(self, variable):
        return self.metric_store.get(variable, 0)

    def increment(self, variable, step_size=1, filename=""):
        self.update_queue.put(('increment', variable, step_size, filename))

    def do_increment(self, *args):
        variable, step_size, filename = args

        # initialize variable to 0 if not set
        if not variable in self.metric_store:
            self.metric_store[variable] = 0

        # increment variable by step_size
        self.metric_store[variable] += step_size

        if filename:
            if 'files' not in self.metric_store:
                self.metric_store['files'] = {}
            
            if filename not in self.metric_store['files']:
                self.metric_store['files'][filename] = {'bytes_to_upload': 0, 'bytes_uploaded': 0, 'already_uploaded': False}
            
            if variable == 'bytes_uploaded':
                self.metric_store['files'][filename]['bytes_uploaded'] += step_size
            
            elif variable == 'bytes_to_upload':
                self.metric_store['files'][filename]['bytes_to_upload'] = step_size
                
            elif variable == 'already_uploaded':
                self.metric_store['files'][filename]['already_uploaded'] = step_size # True/False            
                

    def set_dict(self, dict_name, key, value):
        self.update_queue.put(('set_dict', dict_name, key, value))

    def do_set_dict(self, *args):
        dict_name, key, value = args

        if not dict_name in self.metric_store:
            self.metric_store[dict_name] = {}

        self.metric_store[dict_name][key] = value

    def get_dict(self, dict_name, key=None):
        # if dict_name does not exist, return an empty dict
        if not dict_name in self.metric_store:
            return {}

        # if key was not provided, return full dict
        if not key:
            return self.metric_store[dict_name]

        # return value of key
        return self.metric_store[dict_name].get(key)

    def append(self, list_name, value):
        self.update_queue.put(('append', list_name, value))

    def do_append(self, *args):
        list_name, value = args

        # initialize to empty list if not yet created
        if not list_name in self.metric_store:
            self.metric_store[list_name] = []

        # append value to list
        self.metric_store[list_name] = value

    def get_list(self, list_name):
        return self.metric_store.get(list_name, [])

    @ciocore.common.dec_catch_exception(raise_=True)
    def target(self):
        logger.debug('created metric_store target thread')
        
        while not self.stop:
            
            logger.debug("Metric store self.stop={}".format(self.stop))
            
            try:
                # block until update given
                update_tuple = self.update_queue.get(True, 2)
                
            except queue.Empty:
                continue                

            method = update_tuple[0]
            method_args = update_tuple[1:]
            # check to see what action is to be carried out
            if method == 'increment':
                self.do_increment(*method_args)
            elif method == 'append':
                self.do_append(*method_args)
            elif method == 'set_dict':
                self.do_set_dict(*method_args)
            else:
                raise "method '%s' not valid" % method

            # mark task done
            self.update_queue.task_done()


class JobManager():

    def __init__(self, job_description, reporter_description=None):
        self.error = []
        self.workers = []
        self.reporters = []
        self.error_queue = queue.Queue()
        self.metric_store = MetricStore()
        self.work_queues = [queue.Queue()]
        self.job_description = job_description
        self.reporter_description = reporter_description
        self._queue_started = False
        self.error_handler_stop = False
        self.error_handler_thread = None

    def drain_queues(self):
        logger.error('draining queues')
        # http://stackoverflow.com/questions/6517953/clear-all-items-from-the-queue
        for the_queue in self.work_queues:
            the_queue.mutex.acquire()
            the_queue.queue.clear()
            the_queue.mutex.release()
        return True

    def mark_all_tasks_complete(self):
        logger.error('clearing out all tasks')
        # http://stackoverflow.com/questions/6517953/clear-all-items-from-the-queue
        for the_queue in self.work_queues:
            the_queue.mutex.acquire()
            the_queue.all_tasks_done.notify_all()
            the_queue.unfinished_tasks = 0
            the_queue.mutex.release()
        return True

    def kill_workers(self):
        global WORKING
        WORKING = False
        for worker in self.workers:
            logger.debug("Killing worker: %s", worker)
            worker.kill(block=True) # Wait to ensure the worker was killed

    def kill_reporters(self):
        for reporter in self.reporters:
            logger.debug('killing reporter %s', reporter)
            reporter.kill()

    def stop_work(self, force=False):
        
        global WORKING
        
        if WORKING:
            
            logger.info("Stopping Worker Manager")
            
            WORKING = False  # stop any new jobs from being created
            self.drain_queues()  # clear out any jobs in queue
            self.kill_workers()  # kill all threads
            self.kill_reporters()
            self.mark_all_tasks_complete()  # reset task counts
            
            self.metric_store.stop = True
            self.metric_store.join()
            
            self.error_handler_stop = True
            self.error_handler_thread.join()
            
        else:
            logger.info("Worker Manager has already been stopped.")
        
        return self.error

    @ciocore.common.dec_catch_exception(raise_=True)
    def error_handler_target(self):

        while not self.error_handler_stop:
            
            try:
                error = self.error_queue.get(True, 2)
                
            except queue.Empty:
                continue
            
            logger.error('Got something from the error queue: {}'.format(error))
            self.error.append(error)
            try:
                self.error_queue.task_done()
            except ValueError:
                pass

    def start_error_handler(self):
        
        logger.debug('Creating error handler thread')
        self.error_handler_thread = threading.Thread(target=self.error_handler_target, name="ErrorThread")
        self.error_handler_thread.daemon = True
        self.error_handler_thread.start()
        
        return None

    def add_task(self, task):
        
        # This allows us to keep track of the difference between an empty queue
        # because no tasks have been added or an empty queue because all the tasks
        # have been completed
        if not self._queue_started:            
            self._queue_started = True
        
        self.work_queues[0].put(task)
        
        return True

    def start(self):
        global WORKING
        WORKING = True

        # start shared metric store
        self.metric_store.start()

        # create error handler
        self.start_error_handler()

        # create worker pools based on job_description
        next_queue = None
        last_queue = self.work_queues[0]
        last_worker = next(reversed(self.job_description))

        for worker_description in self.job_description:
            worker_class = worker_description[0]
            args = []
            kwargs = {}

            if len(worker_description) > 1:
                args = worker_description[1]

            if len(worker_description) > 2:
                kwargs = worker_description[2]

            kwargs['in_queue'] = last_queue

            if last_worker == worker_class:
                # the last worker does not need an output queue
                kwargs['out_queue'] = None
            else:
                next_queue = queue.Queue()
                self.work_queues.append(next_queue)
                kwargs['out_queue'] = next_queue

            kwargs['error_queue'] = self.error_queue
            kwargs['metric_store'] = self.metric_store

            worker = worker_class(*args, **kwargs)

            logger.debug('starting worker %s', worker_class.__name__)
            worker.start()
            self.workers.append(worker)
            last_queue = next_queue

        # start reporters
        if self.reporter_description:
            for reporter_class, download_id in self.reporter_description:
                reporter = reporter_class(self.metric_store)
                logger.debug('starting reporter %s', reporter_class.__name__)
                reporter.start(download_id)
                self.reporters.append(reporter)

        return True

    def join(self):
        ''' Block until all work is complete '''

        for _, worker in enumerate(self.workers):
            worker_class_name = worker.__class__.__name__
            logger.debug('waiting for %s workers to finish', worker_class_name)
            worker.join()
        logger.debug('all workers finished')
        self.metric_store.stop = True
        self.metric_store.join()
        logger.debug('metric store in sync')
        
        self.error_handler_stop = True
        self.error_handler_thread.join()
        
        if self.error:
            return self.error
        
        self.kill_workers()
        self.kill_reporters()
        
        return None

    def worker_queue_status_text(self):
        msg = '\n' + '#' * 80 + '\n'
        for index, worker_info in enumerate(self.job_description):
            worker_class = worker_info[0]
            q_size = self.work_queues[index].qsize()
            worker_threads = self.workers[index].threads

            # thread.isAlive() was renamed to is_alive() in Python 3.9 
            try:
                num_active_threads = len([thd for thd in worker_threads if thd.isAlive()])
            except AttributeError:
                num_active_threads = len([thd for thd in worker_threads if thd.is_alive()])

            msg += '%s \titems in queue: %s' % (q_size, worker_class.__name__)
            msg += '\t\t%s threads' % num_active_threads
            msg += '\n'
        return msg
    
    def is_complete(self):

        is_complete = True
        
        # Manager has completed if all workers have completed
        for worker in self.workers:
            logger.debug("Worker {} is complete: {}".format(worker.__class__.__name__, worker.is_complete()))
            is_complete &= worker.is_complete()
            
        logger.debug("All Workers have completed: {}".format(is_complete))
            
        return is_complete
    
class Counter(object):
    
    def __init__(self):
        self.value = 0
        self._lock = threading.Lock()
        
    def increment(self):
        with self._lock:
            self.value += 1
            
    def decrement(self):
        with self._lock:
            self.value -= 1            
            
class Marker(object):
    
    def __init__(self):
        self.marker = False
        self._lock = threading.Lock()
        
    def mark(self):
        
        with self._lock:
            
            logger.debug("Lock aquired (marker={})".format(self.marker))
                    
            if self.marker:
                return True
            
            else:            
            
                self.marker = True
                return False        
