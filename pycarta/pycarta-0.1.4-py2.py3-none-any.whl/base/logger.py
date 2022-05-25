import inspect
import logging
import types

from functools import wraps
from logging.handlers import SysLogHandler
# from socket import SOCK_STREAM


_log_format = f"%(asctime)s - [%(levelname)s] - %(name)s - (%(filename)s).%(funcName)s(%(lineno)d) - %(message)s"


def get_file_handler():
    # file_handler = logging.FileHandler("pycarta.log")
    file_handler = SysLogHandler()
    file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(logging.Formatter(_log_format))
    return file_handler


def get_stream_handler():
    stream_handler = logging.StreamHandler()
    stream_handler.setLevel(logging.WARNING)
    stream_handler.setFormatter(logging.Formatter(_log_format))
    return stream_handler


def get_logger(name):
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)
    logger.addHandler(get_file_handler())
    logger.addHandler(get_stream_handler())
    return logger


def functionlogger(fn):
    function_name = fn.__name__
    logger = get_logger(function_name)
    # logger = logging.getLogger(function_name)
    # logger = logging.getLogger()
    @wraps(fn)
    def wrapper(*args, **kwds):
        state = "Success"
        try:
            result = fn(*args, **kwds)
        except:
            state = "Failed"
            raise
        else:
            return result
        finally:
            logger.debug("%s (%s)", function_name, state)
    return wrapper


class MetaLogger(type):
    """
    Metaclass to enable automatic logging for every function that
    uses MetaLogger as a metaclass.
    """
    def __new__(cls, name, base, dct):
        _type = super().__new__(cls, name, base, dct)
        # _type.logger = logging.getLogger(name)
        # _type.logger.setLevel(logging.DEBUG)
        _type.logger = get_logger(name)
        MetaLogger.update_class_methods(_type)
        return _type

    @staticmethod
    def add_log_decorator(cls, attribute, attribute_name):
        """
        Decoration function which is used for logging the success
        or failure of every function.
        """
        @wraps(attribute)
        def wrapper(*args, **kwargs):
            logger = cls.logger
            state = "Success"
            try:
                result = attribute(*args, **kwargs)
            except:
                state = "Failed"
                raise
            else:
                return result
            finally:
                logger.debug("%s (%s)", attribute_name, state)
        return wrapper

    @staticmethod
    def update_class_methods(cls):
        """
        Updates each class to ensure it is has been wrapped to log events.
        """
        if not hasattr(cls, "__decorated"):
            for attr_name, attr in inspect.getmembers(cls):
                if isinstance(attr, types.FunctionType):
                    setattr(
                        cls,
                        attr_name,
                        MetaLogger.add_log_decorator(
                            cls,
                            attr,
                            cls.__name__ + '.' + attr_name
                        )
                    )
        cls.__decorated = True
