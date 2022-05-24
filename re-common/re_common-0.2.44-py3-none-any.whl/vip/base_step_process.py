from abc import ABC, abstractmethod


class BaseStepProcess(ABC):

    def __init__(self):
        self.stat_dicts = {}

    @abstractmethod
    def do_task(self, *args, **kwargs):
        pass
