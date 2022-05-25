from threading import Thread


class MyThread(Thread):

    def __init__(self, target, *args, **kwargs):
        super(MyThread, self).__init__()
        self.error_ignore = False
        if "error_ignore" in kwargs:
            self.error_ignore = kwargs.get("error_ignore")
            kwargs.pop("error_ignore")
        self.func = target
        self.args = args
        self._kwargs = kwargs
        self.result = None

    def run(self):
        try:
            self.result = self.func(*self.args, **self._kwargs)
        except Exception as e:
            if not self.error_ignore:
                raise e

    def get_result(self):
        return self.result


def thread_task(task_list: list):
    thread_list = []
    for task in task_list:
        if isinstance(task, list):
            if len(task) == 1:
                thread_list.append(MyThread(target=task[0]))
            elif len(task) == 2:
                if isinstance(task[1], list) or isinstance(task[1], tuple):
                    thread_list.append(MyThread(target=task[0], *task[1]))
                elif isinstance(task[1], dict):
                    thread_list.append(MyThread(target=task[0], **task[1]))
            else:
                raise Exception("task format error")
        else:
            raise Exception("task_list is not list")
    for j in thread_list:
        j.start()
    for t in thread_list:
        t.join()
    return [i.get_result() for i in thread_list]
