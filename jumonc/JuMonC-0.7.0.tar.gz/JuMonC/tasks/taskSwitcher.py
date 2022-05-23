import logging

from queue import Queue

from typing import List, Optional, Any, Callable, Dict


from JuMonC import settings



logger = logging.getLogger(__name__)



class _taskSwitcher:
    pending_tasks: Queue = Queue(settings.PENDING_TASKS_SOFT_LIMIT + settings.MAX_THREADS_PER_TASK * settings.MAX_WORKER_THREADS + 1)
    
    def __init__(self) -> None:
        self.max_id = 0
        """Singelton class that switches taks depending on id."""
        self.switch_dic: Dict[int, Callable[..., None]] = {}
        
    def executeNextTask(self) -> None:
        data = self.pending_tasks.get()
        logging.debug("Executing task: %s", str(data))
        task = self.switch_dic.get(data[0], lambda data: logging.warning("Invalid taskID: %s", str(data[0])))
        task(data)
        self.pending_tasks.task_done()
        
    def addTask(self, data: Optional[List[Any]]) -> None:
        logging.debug("Adding task with data: %s", str(data))
        if data is not None:
            self.pending_tasks.put(data)
            return
        logging.info("added taks has no data")
    
    def addFunction(self, func: Callable[..., None]) -> int:
        logging.debug("Adding function: %s", str(func))
        self.max_id = self.max_id + 1
        self.switch_dic[self.max_id] = func
        logging.debug("function ID: %s", str(self.max_id))
        return self.max_id


task_switcher = _taskSwitcher()