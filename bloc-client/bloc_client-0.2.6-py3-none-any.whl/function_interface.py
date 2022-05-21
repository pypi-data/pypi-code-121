import abc
from typing import List

from bloc_client.function_opt import FunctionOpt
from bloc_client.function_ipt import FunctionIpt
from bloc_client.function_run_opt import FunctionRunOpt
from bloc_client.function_run_queue import FunctionRunMsgQueue


class FunctionInterface(metaclass=abc.ABCMeta):
    @classmethod
    def __subclasshook__(cls, subclass):
        return (
            hasattr(subclass, 'all_progress_milestones') and 
            callable(subclass.all_progress_milestones) and 
            hasattr(subclass, 'ipt_config') and 
            callable(subclass.ipt_config) and 
            hasattr(subclass, 'opt_config') and 
            callable(subclass.opt_config) and 
            hasattr(subclass, 'run') and 
            callable(subclass.run) or 
            NotImplemented)

    @abc.abstractmethod
    def ipt_config(self) -> List[FunctionIpt]:
        raise NotImplementedError

    @abc.abstractmethod
    def opt_config(self) -> List[FunctionOpt]:
        raise NotImplementedError

    @abc.abstractmethod
    def all_progress_milestones(self) -> List[str]:
        raise NotImplementedError

    @abc.abstractmethod
    def run(
        self,
        ipts: List[FunctionIpt],
        queue: FunctionRunMsgQueue
    ) -> FunctionRunOpt:
        raise NotImplementedError
