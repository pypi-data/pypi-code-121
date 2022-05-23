import os
import webbrowser
import logging

#######################################################################################################
def launchDocs():
    ROOT_DIR = (os.path.dirname(os.path.abspath(__file__)))
    url = os.path.join(ROOT_DIR, 'docs/index.html')
    url = 'file://' + url
    new = 2  # open in a new tab, if possible
    webbrowser.open(url, new=new)

#######################################################################################################
def print_log(msg, logger=None, logLvl=logging.INFO):
    """
        Print message to console and log in logger

        :param msg: (``string``) - Message to be printed
        :param logger (``Logger`` - optional) - Logger variable to be used to print in log file (default value None)
        :param logLvel (``int`` - optional) - Logging level number (default value logging.INFO, which is equivalent to 20)

        :return: No return
    """
    print(msg)

    if logger != None:
        logger.log(logLvl, msg)

#######################################################################################################
def setup_logger(name, log_file, formatter=None, logLvl=logging.INFO):
    """
        Setup logger

        :param name: (``string``) - Name of the logger
        :param name: (``string``) - Name of the log file
        :param formatter (``string`` - optional) - Format of the log file (default value None)
        :param logLvel (``int`` - optional) - Logging level number (default value logging.INFO, which is equivalent to 20)

        :return: (``Logger``) - Logger object
    """
    if formatter == None:
        formatter = ('%(asctime)s - [%(levelname)s] %(message)s')

    handler = logging.FileHandler(log_file, mode='w')
    handler.setFormatter(logging.Formatter(formatter))
    logger = logging.getLogger(name)
    logger.setLevel(logLvl)
    logger.addHandler(handler)
    return logger

#######################################################################################################
if __name__ == '__main__':
    launchDocs()