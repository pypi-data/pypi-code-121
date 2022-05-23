import logging

from concurrent.futures import ThreadPoolExecutor

from functools import wraps

from typing import Any, Callable, Optional, List, Dict, Union


from JuMonC import settings


logger = logging.getLogger(__name__)

_thread_pool: Optional[ThreadPoolExecutor] = None
_task_pool_avaiable = False



def setupTaskPool() -> None:
    global _thread_pool
    global _task_pool_avaiable
    if _task_pool_avaiable:
        return
    logging.info("started task pool with a maximum of %s workers", str(settings.MAX_WORKER_THREADS))
    _thread_pool = ThreadPoolExecutor(settings.MAX_WORKER_THREADS)
    _task_pool_avaiable = True

    
def executeAsTask(func: Callable[..., List[Dict[str, Union[str, Dict[str, Union[int, float, str]]]]]] 
                 ) -> Callable[..., Optional[List[Dict[str, Union[str, Dict[str, Union[int, float, str]]]]]]]:
    @wraps(func)
    def decorated_function(*args: Any, **kwargs: Any
                          ) -> Optional[List[Dict[str, Union[str, Dict[str, Union[int, float, str]]]]]]:
        if kwargs["duration"] >= settings.SHORT_JOB_MAX_TIME:
            addTask(func, *args, **kwargs)
            return None
        return func(*args, **kwargs)
        
    return decorated_function
        
def addTask(func: Callable, *args: Any, **kwargs: Any) -> None:
    setupTaskPool()
    if _thread_pool is None:
        logging.error("Thread Pool should be available")
        return
    _thread_pool.submit(func, *args, **kwargs)