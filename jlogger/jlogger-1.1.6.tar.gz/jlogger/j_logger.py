# The MIT License (MIT)
# Copyright (c) 2022 Jim S Chen
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.


import logging
from logging.handlers import *
import os
import queue


""" Set up logger with a handler (default to rotating) as root logger
:param file_name: the logger file name from the app 
:param handler: the type of the handler. default to rotatingfile. It can also be:
                timedrotatingfile, watchedfile, socket, datagram
                syslog, smtp, http, buffering, memory, queue
                Note: each type has different argument set and has to be provided properly 
:param level: The logging level for the root logger. Value needs to be in ["CRITICAL", "ERROR", "WARNING", "INFO", "DEBUG"]
                If the specified is not in the list, INFO is the default
:param max_size: This argument is for rotating logs to specify the maximum log size. In mega byte.
:param rotate_num: For rotating logs only. It specifies how many backup file needed. The value has to be
                at least 1 to work with rotation
:param logger_name: named logger if provided, otherwise set up the root logger
:param propogate: decide whether the logger can propogate to ancestors 
:param host: For socket, datagram, http types of logger to specify the host name or IP address 
:param port: For socket, datagram, http types of logger to specify the port number
:param mailhost: For smtp type to set up the mail server
:param fromaddr: For smtp type to set up the mail sender address
:param toaddrs: For smtp type to set up the mail recipient address
:param subject: For smtp type to set up the mail subject
:param url: For http handler to specify the website url
:param queue: For queue handler to pass a queue object
"""
def set_logger(file_name:str, handler:str="rotatingfile", level:str="info", max_size=1024*1024*50, 
                rotate_num=1, logger_name=None, propogate=True,
                host="localhost", port="51000", 
                mailhost=None, fromaddr=None, toaddrs=None, subject=None, 
                url=None, 
                queue:queue=None):

    # sanity check
    if (file_name == None or file_name == "") and (handler == "rotatingfile" or handler == "timedrotatingfile" or handler == "watchedfile"):
        raise ValueError("Must specify a valid log file name! For e.g. /data/lec.log")

    # if file_name includes a path. Check the folder existence. If not create.
    if (handler == "rotatingfile" or handler == "timedrotatingfile" or handler == "watchedfile"):
        if len(file_name.split("/")) > 1 and not os.path.exists("/".join(file_name.split("/")[:-1])):
            os.makedirs(os.path.dirname(file_name), exist_ok=True)
    
    # configure the root logger
    if logger_name is not None:
        logger = logging.getLogger(logger_name)                     # configure named logger
    else:
        logger = logging.getLogger()                                # configure root logger
    log_level = getattr(logging, level.upper(), logging.INFO)
    logger.setLevel(log_level) 
    logger.propagate = propogate

    # sort out the handler
    if handler.lower() == "rotatingfile": 
        file_handler = RotatingFileHandler(file_name, maxBytes=max_size, backupCount=rotate_num)
    elif handler.lower() == "timedrotatingfile":
        file_handler = TimedRotatingFileHandler(file_name, backupCount=rotate_num)
    elif handler.lower() == "watchedfile":
        file_handler = WatchedFileHandler(file_name)
    elif handler.lower() == "socket":
        file_handler = SocketHandler(host, port)
    elif handler.lower() == "datagram":
        file_handler = DatagramHandler(host, port)
    elif handler.lower() == "syslog":
        file_handler = SysLogHandler()
    elif handler.lower() == "smtp" and mailhost != None and fromaddr != None and toaddrs != None and subject != None:
        file_handler = SMTPHandler(mailhost, fromaddr, toaddrs, subject)
    elif handler.lower() == "http" and url != None:
        file_handler = HTTPHandler(host, url)
    elif handler.lower() == "buffering":
        file_handler = BufferingHandler(max_size)
    elif handler.lower() == "memory":
        file_handler = MemoryHandler(max_size)
    elif handler.lower() == "queue" and queue != None:
        file_handler = QueueHandler(queue)
    else:
        file_handler = logging.StreamHandler()
    if logger_name is not None:
        formatter = logging.Formatter("%(asctime)s - " + logger_name + " - %(funcName)s:%(lineno)d - %(levelname)s - %(message)s")
    else:
        formatter = logging.Formatter("%(asctime)s - %(filename)s - %(funcName)s:%(lineno)d - %(levelname)s - %(message)s")
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    return logger


if __name__ == '__main__':
    print("start logging...")

    # *****************testing code**************
    set_logger("data/test_rotate.log", max_size=2048)
    set_logger("data/test_rotate.log", level="debug")
    logger = logging.getLogger(__name__)
    for i in range(1000):
        logger.info(f"Test log rotation {i}")
    # *****************testing code**************

    print("finished logging")



