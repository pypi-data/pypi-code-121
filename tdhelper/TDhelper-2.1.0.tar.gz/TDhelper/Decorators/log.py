import functools
import logging
import logging.config

logging.basicConfig(level= logging.INFO)

def logging_setup(config_json):
    logging.config.dictConfig(config= config_json)

def SYS_LOGS(func):
    def wapper(*args, **kwargs):
        try:
            logging.info("{} start..." % func.__name__)
            ret= func(*args, **kwargs)
            logging.info("{} end..." % func.__name__)
            return ret
        except Exception:
            logging.exception("System Faild.",exc_info= True)
    return wapper

def log(func):
    def wapper(*args, **kwargs):
        try:
            logging.info('{} is start.' % func.__name__)
            ret= func(*args, **kwargs)
            logging.info('{} is end.' % func.__name__)
            return ret
        except Exception as e:
            logging.error("{} has error:" % func.__name__)
            logging.error("{}" % e)
    return wapper