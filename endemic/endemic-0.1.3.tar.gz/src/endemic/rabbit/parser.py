import inspect
from functools import wraps
from .constant import *


"""
Rabbitmq message example
{
    "project_flow": [
        {
            "task": "......",
            "link": "......",
            'current-iteration': 1,
            'next-task-queue': "...",
            'next-task-priority': "..."
        },
        {
            "task": "......",
            "link": "......",
            'current-iteration': 1,
            'next-task-queue': "...",
            'next-task-priority': "..."
        },
        {
            "task": "......",
            "link": "......",
            'current-iteration': 1,
            'next-task-queue': "...",
            'next-task-priority': "..."
        },
        ....
    ],
    "message-created": "2021-01-02 15:53:25",
    "link": "0efa7304-dc86-4fd3-95fc-9c9d2da7ae5b",
    "data: []
}
"""


def decorator_check_exits_variable(part: str, name: str, is_raise=False):
    def wrapper(f):
        @wraps(f)
        def wrapped(self):

            if not self.message:
                raise ValueError('Message not exists')

            if not self.current_task:
                raise ValueError('Current task not exists')

            body = self.current_task if part == PART_TASK else self.message

            if name not in body:
                if is_raise:
                    raise ValueError('Variable "{}" not in {}'.format(name, part))
                return None

            return f(self)

        return wrapped

    return wrapper


class Parser:

    def __init__(self):
        self.__message = None
        self.__current_queue = None
        self.__current_priority = 1

        self.__tasks_all = []

    @property
    @decorator_check_exits_variable(PART_MESSAGE, LINK, True)
    def link_message(self) -> str:
        return self.message[LINK] if self.message[LINK] else ''

    @property
    @decorator_check_exits_variable(PART_TASK, LINK, True)
    def link_task(self) -> str:
        return self.current_task.get(LINK, '')

    @property
    @decorator_check_exits_variable(PART_TASK, TASK, False)
    def task_title(self) -> str:
        return self.current_task[TASK] if TASK in self.current_task else None

    @property
    @decorator_check_exits_variable(PART_TASK, NEXT_TASK_QUEUE, False)
    def next_task_queue(self):
        return self.current_task[NEXT_TASK_QUEUE] if NEXT_TASK_QUEUE in self.current_task else ''

    @property
    @decorator_check_exits_variable(PART_TASK, NEXT_TASK_PRIORITY, False)
    def next_task_priority(self):
        return self.current_task[NEXT_TASK_PRIORITY] if NEXT_TASK_PRIORITY in self.current_task else ''

    @property
    @decorator_check_exits_variable(PART_TASK, CURRENT_ITERATION, False)
    def iteration(self):
        return self.current_task[CURRENT_ITERATION] if CURRENT_ITERATION in self.current_task else 0

    @property
    def queue(self):
        if not self.__current_queue:
            method_name = inspect.currentframe().f_code.co_name
            raise ValueError('"{}" is empty'.format(method_name))
        return self.__current_queue

    @property
    def priority(self):
        if not self.__current_priority:
            method_name = inspect.currentframe().f_code.co_name
            raise ValueError('"{}" is empty'.format(method_name))
        return self.__current_priority

    @property
    def message(self):
        if not self.__message:
            method_name = inspect.currentframe().f_code.co_name
            raise ValueError('"{}" is empty'.format(method_name))
        return self.__message

    @property
    def tasks_all(self) -> list:
        return self.__tasks_all

    @property
    def next_tasks(self) -> list:
        return self.__tasks_all[1:]

    @property
    def current_task(self) -> dict:
        return self.__tasks_all[:1][0]

    @queue.setter
    def queue(self, value: str):
        self.__current_priority = value

    @priority.setter
    def priority(self, value: int):
        self.__current_priority = value

    @message.setter
    def message(self, value: dict):
        self.__message = value
        self.__tasks_all = self.__message[PROJECT_FLOW] if PROJECT_FLOW in self.__message else []
