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

import time
import logging

class HeartbeatLog:
    """ heartbeat log class
    Provide a heartbeat logging as per the specified interval. It doesn't request the main app to have a timer.
    """
    def __init__(self, name, interval_env:str):
        """ constructor
        :param name: The forever module name passed from app
        :param interval_env: interval for the heartbeat log
        """
        assert interval_env == None or isinstance(interval_env, str), "interval_env has to be either None or a string!"

        self._name = name
        if interval_env is not None and interval_env.isdigit():     # Note, interval_env must be positive integer number!
            self._interval_val = int(interval_env)
        else:
            self._interval_val = 0
        self._start_time = None


    def log(self, logger:logging.Logger = None, message = None, replace = False):
        """ log function
        :param logger: The underlying logger. If this is None, it won't log.
        :param message: customised log message to attach or replace depending on the replace setting
        :param replace: replace the default message with customised one if set to True   
        Note, if interval value is 0, it won't log.
        """
        if self._interval_val == 0:
            return

        if self._start_time == None:
            self._start_time = time.time()

        curr_time = time.time()
        if round(curr_time-self._start_time) >= self._interval_val and logger != None:
            ori_fmtter = None
            if len(logger.root.handlers) > 0:
                new_fmtter = logging.Formatter("%(asctime)s - " + self._name + " - %(funcName)s:%(lineno)d - %(levelname)s - %(message)s")
                ori_fmtter = logger.root.handlers[0].formatter
                logger.root.handlers[0].setFormatter(new_fmtter)
            else:
                new_fmtter = "%(asctime)s - " + self._name + " - %(funcName)s:%(lineno)d - %(levelname)s - %(message)s"
                logging.basicConfig(format=new_fmtter)
            if replace and message:
                logger.info(message)
            elif message: 
                logger.info(f'Heart beat ----- alive. Logged every {self._interval_val} seconds. {message}')
            else:
                logger.info(f'Heart beat ----- alive. Logged every {self._interval_val} seconds.')
            if len(logger.root.handlers) > 0:
                logger.root.handlers[0].setFormatter(ori_fmtter)               
            self._start_time = curr_time

