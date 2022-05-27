import logging


LOG_FORMAT = '%(asctime)s | %(levelname)-8s | %(message)s'


class Formatter(logging.Formatter):
    def __init__(
            self,
            fmt:str = LOG_FORMAT,
            *args,
            **kwargs
    ):
        super().__init__(fmt=fmt, *args, **kwargs)


class ConsoleHandler(logging.StreamHandler):
    '''
    控制台日志处理程序
    '''
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setFormatter(Formatter())


class ConsoleHighlightedHandler(logging.StreamHandler):
    '''
    控制台日志高亮处理程序
    '''
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setFormatter(Formatter())


class Logger(logging.Logger):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.addHandler(ConsoleHandler())


def getLogger(name:str = 'mfhm'):
    return Logger(name)