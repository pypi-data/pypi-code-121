from multiprocessing import Pipe, Process
from multiprocessing.connection import Connection
from typing import Any, Callable, Tuple
import time

from .types.health_check import HealthCheck

class Task():
    def __init__(self, target: Callable, daemon=True) -> None:
        """
        Creates an instance of the Task object.

        A Task will call the target parameter whenever Task.run is invoked

        Parameters
        ----------
        target : Callable
            Any top level python function or callable class attribute

        Returns
        -------
        Task
            An instance of ez_task.task.Task 

        """
        connections: Tuple[Connection, Connection] = Pipe()
        self.internal_connection, self.external_connection = connections
        self._target = target
        self.process: Process = Process(target=Task._call_function, args=(self.internal_connection, self._target), daemon=daemon)
        self.process.start()
        self.is_initialized: bool = False
        pass

    def __enter__(self):
        return self

    def __exit__(self, exception_type, exception_value, traceback):
        try:
            self.terminate()
        except:
            return

    def respawn(self):
        """
        Attempts to revive a dead process
        
        Parameters
        ----------
        None

        Returns
        -------
        None
        """
        try:
            self.terminate()
        except:
            pass
        connections: Tuple[Connection, Connection] = Pipe()
        self.internal_connection, self.external_connection = connections
        self.process: Process = Process(target=Task._call_function, args=(self.internal_connection, self._target), daemon=True)
        self.process.start()
        self.is_initialized: bool = False

    def is_alive(self):
        try:
            return self.process.is_alive()
        except:
            return False

    def terminate(self) -> None:
        """
        Terminates Task's running process and associated piped connections.

        Parameters
        ----------
        None

        Returns
        -------
        None
        """
        self.internal_connection.close()
        self.external_connection.close()
        self.process.terminate()
        self.process.kill()
        self.process.join()
        self.process.close()

    def run(self, *args, **kwargs) -> None:
        """
        Asychronously applies target function upon an number of valid positional arguments.

        Parameters
        ----------
        *args : 
            Accepts any number of positional arguments that are also accepted by specified target function
        **kwargs:
            Accepts any number of keyword arguments
        Returns
        -------
        None
        """
        if not args and not kwargs:
            self.external_connection.send(None)
        else:
            self.external_connection.send((args, kwargs))

    
    def _blocking_health_check(self):
        if self.is_alive():
            self.is_initialized = True
            return True
        elif self.is_initialized:
            raise(Exception('Process has terminated'))
        while True:
            healthy = self.is_alive()
            if healthy:
                self.is_initialized = True
                return True
            elif not healthy and self.is_initialized:
                return False
            time.sleep(0.1)
        pass


    def get_result(self) -> Any:
        """
        Returns the result of a previous invocation of Task.run

        Blocks until a result of Task.run is available.
        
        Parameters
        ----------
        None

        Returns
        -------
        Any :
            The result of invoking the target function upon the positional arguments specified in Task.run invocation
        """
        result = self.external_connection.recv()
        return result

    @staticmethod
    def _call_function(conn, function):
        while True:
            res = conn.recv()
            if (isinstance(res, tuple)):
                args, kwargs = res
                if args and isinstance(args[0], HealthCheck):
                        out = True
                else:
                    out = function(*args, **kwargs)
            else:
                out = function()
            conn.send(out)
