import inspect
import logging
import logging.config
import logging.handlers
import os


class LogUtilsMissingConfigFileException(Exception):
    pass


class LogUtilsMissingFileOrFolderException(Exception):
    pass


class LogUtilsConfigFileFormatException(Exception):
    pass


class RelativePathRotatingFileHandler(logging.handlers.RotatingFileHandler):
    def __init__(self, relative_path, file_name, max_bytes=2000, backup_count=100):
        local_path = os.path.dirname(os.path.abspath(__file__))
        log_path = os.path.join(local_path, relative_path)
        if not os.path.isdir(log_path):
            os.mkdir(log_path)
        log_file_name = os.path.join(log_path, file_name)
        super(RelativePathRotatingFileHandler, self).__init__(log_file_name, max_bytes, backup_count)


def get_log_file_name():
    for handler in logging.root.handlers:
        if handler.baseFilename is not None:
            return handler.baseFilename
    return None


def get_logger(additional_name=None):
    stack = inspect.stack()
    if len(stack) == 2:
        file_name = os.path.basename(stack[1][1]).split(".")[0]
    else:
        file_name = os.path.basename(stack[2][1]).split(".")[0]
    the_function = stack[1][3]
    # noinspection PyBroadException
    try:
        if len(stack[1][0].f_locals) > 0:
            the_class = str(stack[1][0].f_locals["self"].__class__.__name__) + "."
        else:
            the_class = ""
    except Exception:
        the_class = ""
    if additional_name is None:
        additional_name = ''
    logger_name = "{}.{}{}{}".format(file_name, the_class, the_function, additional_name)
    return logging.getLogger(logger_name)


def _get_arg_list(kwargs):
    string = None
    count = 0
    if len(kwargs) == 1:
        # noinspection PyBroadException
        try:
            string = kwargs["msg"]
        except Exception:
            pass
    if string is None:
        string = ""
        for key in kwargs:
            val = kwargs[key]
            string += str(key) + "=" + str(val)
            if count < len(kwargs) - 1:
                string += ","
                count += 1
    return string


def current_function_name():
    stack = inspect.stack()
    the_function = stack[1][3]
    return the_function


def start_function(logger, **kwargs):
    stack = inspect.stack()
    the_function = stack[1][3]
    logger.debug("Starting {}({})".format(the_function, _get_arg_list(kwargs)))


def end_function(logger, **kwargs):
    stack = inspect.stack()
    the_function = stack[1][3]
    logger.debug("Ending {}({})".format(the_function, _get_arg_list(kwargs)))


class _Test:
    @staticmethod
    def function1():
        logger = get_logger()
        logger.debug("debug in function1")
        logger.info("info in function2")
        logger.warning("warning in function1")
        logger.error("error in function1")
        logger.critical("critical in function1")


def _test_function3():
    logger = get_logger()
    val1 = 5
    val2 = 6
    logger.debug("debug in _test_function3")
    logger.info("info in _test_function3")
    logger.warning("warning in _test_function3")
    logger.error("error in _test_function3")
    logger.critical("critical in _test_function3")
    start_function(logger, msg="_test_function3")
    start_function(logger, val1=val1, val2=val2)
    val1 = 10
    val2 = {"first": 1, "second": 2}
    end_function(logger, val1=val1, val2=val2)


def _test_function2():
    logger = get_logger()
    val1 = 5
    val2 = 6
    logger.debug("debug in _test_function2")
    logger.info("info in _test_function2")
    logger.warning("warning in _test_function2")
    logger.error("error in _test_function2")
    logger.critical("critical in _test_function2")
    start_function(logger, msg="_test_function2")
    start_function(logger, val1=val1, val2=val2)
    val1 = 10
    val2 = {"first": 1, "second": 2}
    end_function(logger, val1=val1, val2=val2)


def _test_function():
    logger = get_logger()
    val1 = 5
    val2 = 6
    logger.debug("debug in _test_function")
    logger.info("info in _test_function")
    logger.warning("warning in _test_function")
    logger.error("error in _test_function")
    logger.critical("critical in _test_function")
    start_function(logger, msg="_test_function")
    start_function(logger, val1=val1, val2=val2)
    val1 = 10
    val2 = {"first": 1, "second": 2}
    end_function(logger, val1=val1, val2=val2)


def load_log_config(config_file_name):
    logger = get_logger()
    if not os.path.exists(config_file_name):
        raise LogUtilsMissingConfigFileException("Log configuration file {} does not exist.  "
                                                 "Consider creating one for better debugging".format(config_file_name))
    try:
        logging.config.fileConfig(config_file_name)
    except FileNotFoundError as e:
        raise LogUtilsConfigFileFormatException('Missing file or folder.  '
                                                'Are you missing a file or folder defined in '
                                                '{}:{}'.format(config_file_name, str(e)))
    except KeyError as e:
        raise LogUtilsConfigFileFormatException('log file format exception:{}'.format(str(e)))
    logger.debug("Beginning logging with configuration from:{}".format(config_file_name))


def _main():
    logger = get_logger()
    start_function(logger, msg="starting")
    test = _Test()
    test.function1()
    _test_function()
    _test_function2()
    _test_function3()


if __name__ == '__main__':
    load_log_config('../tests/logging.ini')
    _main()
