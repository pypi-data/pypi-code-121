from random import random
import time
from functools import wraps

from .exceptions import StorageServerException
from .validation.utils import is_decorated_method
from .models.http_options import BASE_DELAY_DEFAULT, MAX_DELAY_DEFAULT


def get_delay_with_jitter(delay):
    # @SONAR-OFF
    return delay * (0.8 + random() * 0.4)  # nosec: disable=B311
    # @SONAR-ON


def retry_on_server_exception(
    status_code,
    retry_base_delay=BASE_DELAY_DEFAULT,
    retry_max_delay=MAX_DELAY_DEFAULT,
):
    def decorator(function):
        @wraps(function)
        def inner(*args, **kwargs):
            if is_decorated_method(function, args):
                class_instance = args[0]
            else:
                class_instance = None

            base_delay_sec = retry_base_delay(class_instance) if callable(retry_base_delay) else retry_base_delay
            max_delay_sec = retry_max_delay(class_instance) if callable(retry_max_delay) else retry_max_delay

            current_delay_sec = base_delay_sec
            while True:
                try:
                    return function(*args, **kwargs)
                except StorageServerException as e:
                    if e.status_code != status_code:
                        raise

                    if current_delay_sec <= max_delay_sec:
                        time.sleep(get_delay_with_jitter(current_delay_sec))
                        current_delay_sec = current_delay_sec * 2
                        continue

                    raise

        return inner

    return decorator
