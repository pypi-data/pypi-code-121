from multiprocessing import Pool, Queue, Process, SimpleQueue, cpu_count
from threading import Thread
from queue import Empty
import time
from json import dumps
import signal
from database import *

"""
A class to run many tasks in parallel when they are mostly independent.  This engine is perfectly
appropriate for long, repetitive calculations (for example: computing f(x) on a large
dataset).

They will make use of all processors and cores and will use either threads or child processes.
You decide which one you use when you create the ComputeEngine:

engine = ComputeEngine(maxTaskCount=None, useThreads=True):

Differences between threads and processes:

* Threads start quickly (ms) and share the memory with the calling thread.  Processes require
  a copy of all the memory used, and will therefore take some time to actually start (~1s)
  Typically, threads will be used when you perform many small calculations.  If a calculation
  is really long, then a process can be more appropriate as 1) it does not suffer much 
  from the startup time and 2) any misbehaving code cannot crash your main code.
* If you use Processes, it is possible to set a timeout and terminate the task when it is taking
  too long. You can return an exit code and check it. It is not possible to terminate a thread.
* A badly behaving Thread can corrupt and crash your program (by modifying memory that it 
  should not for instance).  A Process cannot crash the calling program because it is running
  in a separate space.

To use this engine:

1. create an engine = ComputeEngine()
2. put the input data onto the "input queue" with engine.inputQueue.put(someData)
3. write a function someFunction(inputQueue, outputQueue) that takes two arguments: 
   inputQueue and outputQueue
4. that function will take its input data with inputQueue.get() and store the result
   on outputQueue.put(result)
5. you can put whatever you want on queues (numbers, dictionaries, tuples, other objects, etc...)
6. call engine.compute(), which will start many tasks (either processes or threads).  The function
   will return when all the tasks have run.
7. As the calculation progresses, the compute() function will call processTaskResult() with
   your function or the default function (which prints the results to the screen).
8. If using processes, it is possible to terminate a long running task with a timeout
9. You can change the processTaskResults() function to your own function (to save to disk for instance)

"""

class ComputeEngine:
    def __init__(self, maxTaskCount=None, useThreads=True):
        """
        ComputeEngine that will launch parallel tasks to compute a function on an input queue.

        The engine willstart at most maxTaskCount (number of cpu/cores is the default).
        useThreads=True will use threads and False will use processes.

        When using processes, it is possible to terminate a task that is taking too long.
        When using threads, it is possible to access shared memory (with you own locks).

        """
        self.inputQueue = Queue()
        self.outputQueue = Queue()
        self.runningTasks = []
        self.useThreads = useThreads

        if maxTaskCount is None:
            self.maxTaskCount = cpu_count()
        else:
            self.maxTaskCount = maxTaskCount

        self.signalNames = dict((k, v) for v, k in reversed(sorted(signal.__dict__.items())) if v.startswith('SIG') and not v.startswith('SIG_'))

    def __del__(self):
        """
        Upon deleting this object, we terminate all tasks if we can.
        """
        self.terminateTimedOutTasks(timeoutInSeconds=0)

    def compute(self, target, 
                      processTaskResults=None, 
                      processCompletedTask=None, 
                      timeoutInSeconds=None):
        """
        Call target from a separate task (thread or process) with the inputQueue and outputQueue
        as parameters. Typically, the target function will get its arguments from the inputQueue
        and will put the result on the outputQueue.

        The target function must:
            1. accept two queue arguments (inputQueue and outputQueue)
            2. call inputQueue.get_nowait() or get() and assume the queue *could* be empty.
            2. typically put its result on outputQueue.

        As the calculation progresses, the outputQueue is processed.  The default processing
        prints everything to screen. You can provide your own function processTaskResults(queue) that
        must accept a queue as an argument.

        When using processes, it is possible to kill a task that is taking too long. It is not
        possible with threads.

        When tasks are completed, you get a last chance to do something with them with 
        processCompletedTask(listOfTasks).
        """
        if processTaskResults is None:
            processTaskResults = self.processTaskResults

        if timeoutInSeconds is not None and self.useThreads:
            raise ValueError('To use a timeout, you must use processes with useThreads=False')
        
        self.waitForInputQueue()

        while self.hasTasksStillRunning() or self.hasTasksLeftToLaunch():
            while len(self.runningTasks) < self.maxTaskCount and self.hasTasksLeftToLaunch():
                self.launchTask(target=target)

            processTaskResults(self.outputQueue)

            self.terminateTimedOutTasks(timeoutInSeconds=timeoutInSeconds)
            self.pruneCompletedTasks()
            time.sleep(0.1)

        processTaskResults(self.outputQueue)


    def waitForInputQueue(self, timeout=0.3):
        """
        A queue will not appear non-empty immediately after putting an element into it.
        we really want to have a non-empty inputQueue for calculations so we check
        here with a short timeout in case it is really empty.
        """
        timeoutTime = time.time() + timeout
        while self.inputQueue.empty() and time.time() < timeoutTime:
            time.sleep(0.1)

    def hasTasksLeftToLaunch(self) -> bool:
        """
        If the inputQueue is not empty, then we still have tasks to run.
        """
        return not self.inputQueue.empty()

    def hasTasksStillRunning(self) -> bool:
        """
        When tasks that are running are alive, then we obviously still have tasks running
        """
        return len([ task for task,startTime in self.runningTasks if task.is_alive()]) != 0

    def launchTask(self, target)  -> (object, float):
        """
        Launch either a Thread or a Process with the target processing the inputQueue and outputQueue.

        We keep an internal timer with the start time of the task to determine if it has
        timed out in the future.
        """
        if self.useThreads:
            task=Thread(target=target, args=(self.inputQueue, self.outputQueue))
        else:
            task=Process(target=target, args=(self.inputQueue, self.outputQueue))

        startTime = time.time()
        self.runningTasks.append((task, startTime))
        task.start()
        return task, startTime

    def processTaskResults(self, queue):
        """
        We get (and remove) elements from the outputQueue. The default action is to print everything
        to screen,but this function can be replaced by your own when calling compute().
        """
        while not queue.empty():
            results = queue.get()
            try:
                print(json.dumps(results))
            except:
                print(results)

    def terminateTimedOutTasks(self, timeoutInSeconds):
        """
        If tasks are taking too long, we terminate (kill) them. This is only possible with processes.
        """
        if timeoutInSeconds is None:
            return

        for (task, startTime) in self.runningTasks:
            if time.time() > startTime+timeoutInSeconds:
                if not self.useThreads:
                    task.terminate()
                    task.join()
                else:
                    print("Task has timed out but threads cannot be terminated")

    def processCompletedTasks(self, completedTasks):
        """
        The last chance to manipulate a completed task before it is deleted. Here
        we simply warn the user if the task timedout.
        """
        for task, startTime in completedTasks:
            if isinstance(task, Process):
                if task.exitcode > 0:
                    print("The process {0} failed with error {1}".format(task.pid, task.exitcode))
                elif task.exitcode == -signal.SIGTERM:
                    print("The process {0} timed out".format(task.pid))
                elif task.exitcode < 0:
                    print("The process {0} was terminated with signal {1}".format(task.pid, self.signalNames[-task.exitcode]))
            else:
                # Threads do not have "an exit code". There is nothing to check.
                pass

    def pruneCompletedTasks(self):
        """
        Internal function to keep a list of tasks that are alive (i.e. still running).
        Completed tasks (normal or terminated) get processed by processCompletedTasks() before being 
        deleted.
        """
        completedTasks = [ (task,startTime) for task,startTime in self.runningTasks if not task.is_alive()]
        self.runningTasks = [ (task,startTime) for task,startTime in self.runningTasks if task.is_alive()]

        self.processCompletedTasks(completedTasks)

class DBComputeEngine(ComputeEngine):
    def __init__(self, database, maxTaskCount=None):
        super().__init__(maxTaskCount=maxTaskCount)
        self.db = database

    def enqueueRecordsWithStatement(self, selectStatement):
        self.db.execute(selectStatement)
        rows = self.db.fetchAll()
        if len(rows) >= 32767:
            print("Warning: queue may be limited to 32768 elements")
        elif len(rows) == 0:
            raise ValueError("Warning: no records returned from {0}".format(selectStatement))

        for row in rows:
            record = {}
            for key in row.keys():
                record[key] = row[key]
            self.recordsQueue.put(record)

        # it takes a fraction of a second for the queue to appear non-empty.  We make sure it is ok before returning
        while self.recordsQueue.empty():
            pass

def calculateFactorial(inputQueue, outputQueue):
    try:
        value = inputQueue.get_nowait()
        product = 1
        for i in range(value):
            product *= (i+1)
        outputQueue.put( (value,  product) )
    except Empty as err:
        pass # not an error

def slowCalculation(inputQueue, outputQueue):
    try:
        value = inputQueue.get_nowait()
        time.sleep(10)
        outputQueue.put( value )
    except Empty as err:
        pass # not an error

def processSimple(queue):
    while not queue.empty():
        try:
            (n, nfactorial) = queue.get_nowait()
            print('Just finished calculating {0}!'.format(n))
        except Empty as err:
            break # we are done

if __name__ == "__main__":
    N = 11
    print("Calculating n! for numbers 0 to {0} (every calculation is independent)".format(N-1))
    print("======================================================================")    

    print("Using threads: fast startup time appropriate for quick calculations")
    engine = ComputeEngine(useThreads=True)
    for i in range(N):
        engine.inputQueue.put(i)
    engine.compute(target=calculateFactorial)

    print("Using processes: long startup time appropriate for longer calculations")
    engine = ComputeEngine(useThreads=False)
    for i in range(N):
        engine.inputQueue.put(i)
    engine.compute(target=calculateFactorial)

    print("Using threads and replacing the processTaskResult function")
    engine = ComputeEngine(useThreads=True)
    for i in range(N):
        engine.inputQueue.put(i)
    engine.compute(target=calculateFactorial, processTaskResults=processSimple)

    print("Using processes with very long calculations and timeout")
    engine = ComputeEngine(useThreads=False)
    for i in range(N):
        engine.inputQueue.put(i)
    engine.compute(target=slowCalculation, timeoutInSeconds=2)
