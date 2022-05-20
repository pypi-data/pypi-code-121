# NEON AI (TM) SOFTWARE, Software Development Kit & Application Framework
# All trademark and other rights reserved by their respective owners
# Copyright 2008-2022 Neongecko.com Inc.
# Contributors: Daniel McKnight, Guy Daniels, Elon Gasper, Richard Leeds,
# Regina Bloomstine, Casimiro Ferreira, Andrii Pernatii, Kirill Hrymailo
# BSD-3 License
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
# 1. Redistributions of source code must retain the above copyright notice,
#    this list of conditions and the following disclaimer.
# 2. Redistributions in binary form must reproduce the above copyright notice,
#    this list of conditions and the following disclaimer in the documentation
#    and/or other materials provided with the distribution.
# 3. Neither the name of the copyright holder nor the names of its
#    contributors may be used to endorse or promote products derived from this
#    software without specific prior written permission.
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO,
# THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR
# PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR
# CONTRIBUTORS  BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL,
# EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO,
# PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA,
# OR PROFITS;  OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF
# LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING
# NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
# SOFTWARE,  EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

import time
from typing import Union, Callable

from neon_utils import LOG
from neon_utils.net_utils import check_port_is_open


def get_timeout(backoff_factor: float, number_of_retries: int) -> float:
    """
        Gets timeout based on backoff_factor

        :param backoff_factor: value of backoff factor
        :param number_of_retries: current number of retries made

        Examples:
            >>> __backoff_factor, __number_of_retries = 0.1, 1
            >>> timeout = get_timeout(__backoff_factor, __number_of_retries)
            >>> assert timeout == 0.1
            >>>
            >>> __backoff_factor, __number_of_retries = 0.1, 2
            >>> timeout = get_timeout(__backoff_factor, __number_of_retries)
            >>> assert timeout == 0.2
    """
    return backoff_factor * (2 ** (number_of_retries - 1))


def retry(callback_on_exceeded: Union[str, Callable] = None, callback_on_attempt_failure: Union[str, Callable] = None,
          num_retries: int = 3, backoff_factor: int = 5, use_self: bool = False,
          callback_on_attempt_failure_args: list = None, callback_on_exceeded_args: list = None):
    """
        Decorator for generic retrying function execution

        :param use_self: to call a function from current class instance (defaults to False)
        :param num_retries: num of retries for function execution
        :param callback_on_exceeded: function to call when all attempts fail (is s
        :param callback_on_exceeded_args: args for :param callback_on_exceeded
        :param callback_on_attempt_failure: function to call when single attempt fails
        :param callback_on_attempt_failure_args: args for :param callback_on_attempt_failure
        :param backoff_factor: value of backoff factor for setting delay between function execution retry,
                               refer to "get_timeout()" for details
    """
    # TODO: given function shows non-thread-safe behaviour for Consumer Thread, need to fix this before using
    if not callback_on_attempt_failure_args:
        callback_on_attempt_failure_args = []
    if not callback_on_exceeded_args:
        callback_on_exceeded_args = []

    def decorator(function):
        def wrapper(self, *args, **kwargs):
            with_self = use_self and self
            num_attempts = 1
            error_body = f"{function.__name__}(args={args}, kwargs={kwargs})"
            if with_self:
                error_body = f'{self.__class__.__name__}.{error_body}'
            while num_attempts <= num_retries:
                if num_attempts > 1:
                    LOG.info(f'Retrying {function} execution. '
                             f'Attempt #{num_attempts}')
                try:
                    if with_self:
                        return function(self, *args, **kwargs)
                    else:
                        return function(*args, **kwargs)
                except Exception as e:
                    for i in range(len(callback_on_attempt_failure_args)):
                        if callback_on_attempt_failure_args[i] == 'e':
                            callback_on_attempt_failure_args[i] = e
                        elif callback_on_attempt_failure_args[i] == 'self':
                            callback_on_attempt_failure_args[i] = self
                    try:
                        if callback_on_attempt_failure:
                            if with_self and isinstance(callback_on_attempt_failure, str):
                                getattr(self, callback_on_attempt_failure)(*callback_on_attempt_failure_args)
                            elif isinstance(callback_on_attempt_failure, Callable):
                                callback_on_attempt_failure(*callback_on_attempt_failure_args)
                    except Exception as ex:
                        LOG.error(f'Failed to execute callback_on_attempt_failure function {callback_on_attempt_failure.__name__}({callback_on_attempt_failure_args}) - {ex}')
                    sleep_timeout = get_timeout(backoff_factor=backoff_factor, number_of_retries=num_attempts)
                    LOG.error(f'{error_body}: {e}. Timeout for {sleep_timeout} secs')
                    num_attempts += 1
                    time.sleep(sleep_timeout)
            LOG.error(f'Failed to execute function {error_body} after {num_retries} attempts')
            if callback_on_exceeded:
                if with_self and isinstance(callback_on_exceeded, str):
                    return getattr(self, callback_on_exceeded)(*callback_on_exceeded_args)
                elif isinstance(callback_on_exceeded, Callable):
                    return callback_on_exceeded(*callback_on_exceeded_args)
        return wrapper
    return decorator


def wait_for_mq_startup(addr: str, port: int, timeout: int = 60) -> bool:
    """
    Wait up to `timeout` seconds for the MQ connection at `addr`:`port` to come online.
    :param addr: URL or IP address to monitor
    :param port: MQ port to query
    :param timeout: Max seconds to wait for connection to come online
    """
    stop_time = time.time() + timeout
    while not check_port_is_open(addr, port):
        LOG.debug("Waiting for MQ server to come online")
        if time.time() > stop_time:
            return False
    return True
