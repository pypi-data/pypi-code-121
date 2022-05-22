from logging import DEBUG, Formatter, StreamHandler, getLogger

__all__ = ['get_logger']

DEFAULT_NAME = 'nameless'
BLACK, RED, GREEN, YELLOW, BLUE, MAGENTA, CYAN, WHITE = range(8)
RESET_SEQ = "\033[0m"
COLOR_SEQ = "\033[;%dm"
BOLD_COLOR_SEQ = "\033[1;%dm"

_COLORS = {
    'WARNING': YELLOW,
    'INFO': GREEN,
    'DEBUG': BLUE,
    'CRITICAL': YELLOW,
    'ERROR': RED
}


class MyHandler(StreamHandler):

    def __init__(self, ):
        super().__init__()


def get_logger(name=DEFAULT_NAME):
    logger = getLogger(name)

    cond = True
    for handler in logger.handlers:
        if isinstance(handler, MyHandler):
            cond = False

    if cond:
        # stream handler
        logger.setLevel(DEBUG)
        if logger.name == 'nameless':
            fmr = _ColoredFormatter('%(asctime)s - %(filename)s:%(lineno)s '
                                    '- %(levelname)s:  %(message)s')
        else:
            fmr = _ColoredFormatter('%(asctime)s - %(name)s '
                                    '- %(levelname)s:  %(message)s')
        ch = MyHandler()
        ch.setLevel(DEBUG)
        ch.setFormatter(fmr)
        logger.addHandler(ch)

    return logger


# The background is set with 40 plus the number of the color,
# and the foreground with 30

# These are the sequences need to get colored ouput


class _ColoredFormatter(Formatter):
    def __init__(self, msg, use_color=True):
        Formatter.__init__(self, msg)
        self.use_color = use_color

    def format(self, record):
        if self.use_color:
            record.levelname = COLOR_SEQ % (
                    30 + _COLORS[record.levelname]) + record.levelname + RESET_SEQ

            if record.name == DEFAULT_NAME:
                record.filename = BOLD_COLOR_SEQ % (30 + RED) + record.filename + RESET_SEQ
            else:
                record.name = BOLD_COLOR_SEQ % (30 + RED) + record.name + RESET_SEQ

        return Formatter.format(self, record)
