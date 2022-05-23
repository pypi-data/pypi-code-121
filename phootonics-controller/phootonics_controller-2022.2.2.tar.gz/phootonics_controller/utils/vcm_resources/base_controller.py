# -*- coding: utf-8 -*-
"""
Created by gregory on 16.03.16

Copyright 2016 Alpes Lasers SA, Neuchatel, Switzerland
"""

import logging
import threading
import functools

logger = logging.getLogger(__name__)

__author__ = 'gregory'
__copyright__ = "Copyright 2016, Alpes Lasers SA"


def run_in_thread(func):
    """Decorator to run the func in a thread."""
    @functools.wraps(func)
    def threaded_func(*args, **kwargs):
        thread = threading.Thread(target=func, name=func.__name__, args=args, kwargs=kwargs)
        thread.setDaemon(True)
        thread.start()
        return thread

    return threaded_func


class BaseController(object):
    """Base class for controllers. Provides the connection logic, with several abstract protected methods that must be
    implemented in subclasses.
    """
    DISCONNECTED = 'DISCONNECTED'
    CONNECTION_ERROR = 'CONNECTION_ERROR'
    CONNECTED = 'CONNECTED'

    @property
    def status(self):
        if self.__connection_status == BaseController.CONNECTED:
            return self._connected_status()
        return self.__connection_status

    def __init__(self, monitor_interval=5.0):
        self.monitor_interval = monitor_interval  # connection monitoring interval in seconds
        self.connection_interval = 5.0  # connection retry interval.

        self.__connection_status = BaseController.DISCONNECTED
        # Private threading variables used for connection, monitoring and stopping.
        self.__connection_lock = threading.RLock()
        self.__stop_event = threading.Event()
        self.__stop_event.set()

    def start(self):
        # First command called
        """Starts the controller. It first tries to connect at regular intervals until it succeeds. Once connected, it
        monitors the connection status. It tries to reconnect if the connection is lost."""
        with self.__connection_lock:
            if self.__stop_event.is_set():
                self.__stop_event.clear()
                self.__connect_loop()

    def stop(self):
        """Stops the controller. It disconnects if needed."""
        with self.__connection_lock:
            if not self.__stop_event.is_set():
                self.__stop_event.set()
                self.__connection_status = BaseController.DISCONNECTED
                try:
                    self._disconnect()
                    logger.debug('Successfully disconnected [{}]'.format(self.__class__.__name__))
                except Exception:
                    logger.debug('Error while disconnecting [{}]'.format(self.__class__.__name__), exc_info=1)

    @run_in_thread
    def __monitor_connection(self):
        while not self.__stop_event.wait(self.monitor_interval):
            connection_ok = False
            try:
                connection_ok = self._check_connection()
            except Exception:
                logger.error('Error while checking connection [{}]'.format(self.__class__.__name__), exc_info=1)
            if not connection_ok:
                try:
                    self._disconnect()
                except Exception:
                    pass
                self.__connection_status = BaseController.CONNECTION_ERROR
                self.__connect_loop()
                return

    @run_in_thread
    def __connect_loop(self):
        while True:
            with self.__connection_lock:
                if not self.__stop_event.is_set():
                    try:
                        self._connect()
                        self._check_connection()
                        self.__connection_status = BaseController.CONNECTED
                        logger.debug('Connection successful [{}]'.format(self.__class__.__name__))
                        self.__monitor_connection()
                        return
                    except Exception as e:
                        logger.info(e)
                        if self.__connection_status != BaseController.CONNECTION_ERROR:
                            logger.debug('Could not connect [{}]'.format(self.__class__.__name__), exc_info=1)
                            self.__connection_status = BaseController.CONNECTION_ERROR
            if self.__stop_event.wait(self.connection_interval):
                return

    def _connected_status(self):
        """Protected method implemented by concrete controllers. It is to be called automatically by the base controller
        methods. It must return a status specific to the controller when it is connected."""
        return 'READY'

    def _connect(self):
        """Protected method implemented by concrete controllers. It is to be called automatically by the base controller
        methods. It must raise an Exception if the connection fails."""
        raise NotImplementedError()

    def _disconnect(self):
        """Protected method implemented by concrete controllers. It is to be called automatically by the base controller
        methods. Exceptions are logged, but otherwise ignored."""
        raise NotImplementedError()

    def _check_connection(self):
        """Protected method implemented by concrete controllers. It is to be called automatically by the base controller
        methods. It must return True if the connection is OK, False otherwise or raise an Exception."""
        raise NotImplementedError()


if __name__ == '__main__':
    # playground -- nothing relevant.
    logging.basicConfig(level=logging.DEBUG)
    controller = BaseController()
    controller._connect = lambda: True
    controller._disconnect = lambda: True
    controller._check_connection = lambda: True
    controller.connection_interval=1.0
    controller.monitor_interval = 1.0
    controller.start()
    controller.stop()
    import time
    time.sleep(5.0)
    controller.stop()
    time.sleep(5.0)