from thompcoutils.threading_utils import ThreadManager, Watchdog, WorkerThread, WorkerLoopThread
from thompcoutils.log_utils import current_function_name
import time
import datetime
import unittest

_time_format = '%H:%M:%S'


def function_test1(name, value1, value2):
    print("thread {} starting at {}".format(name, datetime.datetime.now().strftime(_time_format)))
    time.sleep(2)
    print("thread {} done at {}".format(name, datetime.datetime.now().strftime(_time_format)))
    value1 *= 5
    value2 *= 2
    return value1, value2


def function_test2(name, value1):
    print("thread {} starting at {}".format(name, datetime.datetime.now().strftime(_time_format)))
    time.sleep(1)
    print("thread {} done at {}".format(name, datetime.datetime.now().strftime(_time_format)))
    value1 *= 3
    return value1


def _timeout_function(watchdog):
    print('{} Test timeout function called'.format(datetime.datetime.now()))
    watchdog.stop()


def worker_function():
    for i in range(0,5):
        print('{} running _worker_thread'.format(datetime.datetime.now()))
        time.sleep(1)
    print('WorkerThread finishing')


class TestThreadUtils(unittest.TestCase):
    def setUp(self):
        pass

    def atest_watchdog_1(self):
        print('{} {} starting'.format(datetime.datetime.now(), current_function_name()))
        watchdog = Watchdog(2, _timeout_function)
        watchdog.start()
        for i in range(0, 2):
            time.sleep(1)
            print('{} tickling'.format(datetime.datetime.now()))
            watchdog.tickle()
        time.sleep(2)
        print('{} watchdog_test done...'.format(datetime.datetime.now()))

    def atest_worker_thread(self):
        print('{} {} starting'.format(datetime.datetime.now(), current_function_name()))
        worker_thread = WorkerThread(worker_function)
        worker_thread.start()
        print('{} {} done'.format(datetime.datetime.now(), current_function_name()))

    def atest_threads(self):
        print('{} {} starting'.format(datetime.datetime.now(), current_function_name()))
        ThreadManager('one', function_test1, 'one', 1, 2)
        ThreadManager('two', function_test1, 'two', 3, 4)
        ThreadManager('three', function_test2, 'three', 5)
        ThreadManager.start_all_threads()
        print('main starting work at {}'.format(datetime.datetime.now().strftime(_time_format)))
        time.sleep(1)
        print('main done working at {}'.format(datetime.datetime.now().strftime(_time_format)))
        ThreadManager.join_all_threads()

        for thread in ThreadManager.threads:
            print(ThreadManager.threads[thread].rtn)
        print("Back to Main Thread")

        # Or you can manage them yourself:
        thread1 = ThreadManager('one', function_test1, 'one', 1, 2)
        thread2 = ThreadManager('two', function_test1, 'two', 3, 4)
        thread3 = ThreadManager('three', function_test2, 'three', 5)
        thread1.start()
        thread2.start()
        thread3.start()
        print('main starting work at {}'.format(datetime.datetime.now().strftime(_time_format)))
        time.sleep(1)
        print('main done working at {}'.format(datetime.datetime.now().strftime(_time_format)))
        thread1.join()
        thread2.join()
        thread3.join()
        print(thread1.rtn)
        print(thread2.rtn)
        print(thread3.rtn)
        print("Back to Main Thread")
        print('{} {} ending'.format(datetime.datetime.now(), current_function_name()))

    def test_worker_loop_thread(self):
        print('{} {} starting'.format(datetime.datetime.now(), current_function_name()))
        looper = WorkerLoopThread(worker_function)
        looper.start()
        time.sleep(5)
        looper.stop()
        print('{} {} ending'.format(datetime.datetime.now(), current_function_name()))
