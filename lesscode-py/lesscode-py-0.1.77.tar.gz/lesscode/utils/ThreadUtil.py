import logging
from threading import Thread


def calculate_common_pool(thread_list):
    for j in thread_list:
        j.start()
    for t in thread_list:
        t.join()
    return [i.get_result() for i in thread_list]


class MyThread(Thread):

    def __init__(self, target, args=(), kwargs=None):
        super(MyThread, self).__init__()
        if kwargs is None:
            kwargs = {}
        self.func = target
        self.args = args
        self._kwargs = kwargs

    def run(self):
        self.result = self.func(*self.args, **self._kwargs)

    def get_result(self):
        try:
            return self.result
        except:
            logging.info("多线程执行报错")
            return None
