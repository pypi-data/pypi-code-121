import queue
from typing import Any, Optional
from multiprocessing import Queue

from bloc_client.function_run_log import LogLevel
from bloc_client.function_run_opt import FunctionRunOpt
from bloc_client.function_run_log import FunctionRunMsg
from bloc_client.function_run_progress_report import HighReadableFunctionRunProgress


class FunctionRunMsgQueue:
    def __init__(self) -> None:
        self._queue = Queue()

    @classmethod
    def New(cls):
        return cls()
    
    def report_log(self, log_level:LogLevel, msg: str):
        self._queue.put(
            FunctionRunMsg(level=log_level, msg=msg)
        )
    
    def report_high_readable_progress(
        self,
        progress_percent: Optional[float]=None,
        progress_milestone_index: Optional[int]=None,
        progress_high_readable_msg: Optional[str]=None,
    ):
        if not any([
            progress_percent, progress_milestone_index is not None, progress_high_readable_msg
        ]):
            return
        self._queue.put(
            HighReadableFunctionRunProgress(
                progress_percent=progress_percent,
                msg=progress_high_readable_msg,
                progress_milestone_index=progress_milestone_index
            )
        )
    
    def report_function_run_finished_opt(
        self, func_run_opt: FunctionRunOpt
    ):
        self._queue.put(
            func_run_opt
        )
    
    def get(self, timeout: int) -> Any:
        try:
            return self._queue.get(block=True, timeout=timeout)
        except queue.Empty as err:
            return None