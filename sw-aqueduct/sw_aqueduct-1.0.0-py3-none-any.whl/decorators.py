# -*- coding: utf-8 -*-
from functools import wraps

from requests.exceptions import ConnectionError, HTTPError, RequestException, Timeout
from swimlane.exceptions import SwimlaneHTTP400Error

# Copyright: (c) 2022, Swimlane <info@swimlane.com>
# MIT License (see LICENSE or https://opensource.org/licenses/MIT)
from .base import Base
from .utils.exceptions import ModelError


def log_exception(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except ModelError as me:
            Base().log(me.args, level="critical")
            if not Base().continue_on_error:
                raise me
        except SwimlaneHTTP400Error as sw:
            Base().log(sw.args)
            if not Base.continue_on_error:
                raise sw
        except HTTPError as he:
            log = f"Unable to process '{func.__name__}' request"
            if kwargs:
                log += f" with the requested parameters '{', '.join([x for x in kwargs.keys()])}' {kwargs}."
            Base().log(log)
            if not Base.continue_on_error:
                raise he
        except ConnectionError as errc:
            Base().log(f"An Error Connecting to the API occurred: {repr(errc)}")
            if not Base.continue_on_error:
                raise errc
        except Timeout as errt:
            Base().log(f"A timeout error occurred: {repr(errt)}")
            if not Base.continue_on_error:
                raise errt
        except RequestException as err:
            Base().log(f"An Unknown Error occurred: {repr(err)}")
            if not Base.continue_on_error:
                raise err
        except Exception as e:
            Base().log(f"There was an unknown exception that occurred in '{func.__name__}': {e}")
            if not Base.continue_on_error:
                raise e

    return wrapper
