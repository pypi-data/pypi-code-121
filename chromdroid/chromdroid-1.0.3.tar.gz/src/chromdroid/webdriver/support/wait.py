import os
import time
import threading

from chromdroid.webdriver.common import utils
from chromdroid.webdriver.remote.command import Command


class WebDriverWait:

    def __init__(self, driver, timeout):
        self.driver = driver
        self.timeout = timeout
        self.kill = False
        self.result = None

    def time(self):
        end_time = time.time() + self.timeout
        while True:
            if self.kill:
                self.kill = False
                break
            if time.time() > end_time:
                self.kill = True
                utils.exception(
                    TimeoutError, "Time out to wait element", no_exit=True)
                break

    def recv_result(self, method, command):
        self.result = method(self.driver, command)

    def until(self, method):
        time_thread = threading.Thread(target=self.time, daemon=True)
        recv_thread = threading.Thread(target=self.recv_result, args=(
            method, Command.WAIT_UNTIL_ELEMENT), daemon=True)
        time_thread.start()
        recv_thread.start()
        while True:
            if self.kill or time_thread.is_alive() == False:
                os._exit(0)
            try:
                result = self.result
                if result != None:
                    if time_thread.is_alive() == True:
                        self.kill = True
                    self.result = None
                    return result
            except Exception as ex:
                raise ex

    def until_not(self, method):
        time_thread = threading.Thread(target=self.time, daemon=True)
        recv_thread = threading.Thread(target=self.recv_result, args=(
            method, Command.WAIT_UNTIL_NOT_ELEMENT), daemon=True)
        time_thread.start()
        recv_thread.start()
        while True:
            if self.kill or time_thread.is_alive() == False:
                os._exit(0)
            try:
                result = self.result
                if result == True:
                    if time_thread.is_alive() == True:
                        self.kill = True
                    self.result = None
                    return result
            except Exception as ex:
                raise ex
