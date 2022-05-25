import time
import typing as t


_T = t.TypeVar("_T")


def wait_until(condition: t.Callable[[], _T], timeout: float, check_interval: float) -> _T:
    """
    Checks the return value of ``condition``, retrying every ``check_interval`` seconds until it returns a truthy value.
    Once that happens, returns ``condition``'s return value. ``condition`` should not take any arguments. If ``timeout``
    is reached before the condition is met, a ``TimeoutError`` is raised.
    """
    start_time = time.time()
    while True:
        state = condition()
        if state:
            return state
        if time.time() - start_time > timeout:
            raise TimeoutError("condition was not met before the timeout")
        time.sleep(check_interval)
