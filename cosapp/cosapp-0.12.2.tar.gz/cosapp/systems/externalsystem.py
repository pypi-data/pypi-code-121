import json
import logging
import socket
import subprocess
import sys
from abc import abstractmethod
from struct import pack, unpack
from threading import Timer
from typing import Any, Dict, Optional

import numpy.distutils
from numpy.distutils.exec_command import find_executable

from cosapp.systems.system import System
from cosapp.utils.json import JSONEncoder

logger = logging.getLogger(__name__)


class Communication:
    def __init__(self, port):
        self.port = port
        self.connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.my_connection = None

    def send_message(self, message):
        msg = message.encode()
        length = pack(">Q", len(msg))
        self.my_connection.sendall(length)
        self.my_connection.sendall(msg)

        # self.my_connection.send(message.encode())

    def wait_for_message(self, nb_characters=1024):
        bs = self.my_connection.recv(8)
        (length,) = unpack(">Q", bs)
        message = b""
        while len(message) < length:
            to_read = length - len(message)
            message += self.my_connection.recv(min(to_read, 4096))

        # message = self.my_connection.recv(nb_characters)
        return message.decode()

    def close_connection(self):
        self.connection.close()

    def __del__(self):
        self.close_connection()


class Server(Communication):
    def __init__(self, port, failed_connection_attempt_max=1):
        Communication.__init__(self, port)

        self.connection.bind(("", port))
        self.connection.listen(failed_connection_attempt_max)

    def accept(self):
        self.my_connection, (clientsocket, ip) = self.connection.accept()
        return self.my_connection, (clientsocket, ip)


class Client(Communication):
    def __init__(self, name, port):
        Communication.__init__(self, port)

        self.name = name
        self.my_connection = None
        self.retry = True
        self.connected = False

    def connect_server(self, timeout=5.0):
        self.connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.connected = False
        self.timer = Timer(timeout, self.stop)
        self.timer.start()

        while self.retry and not self.connected:
            try:
                self.connection.connect(("localhost", self.port))
            except ConnectionRefusedError:
                pass
            else:
                self.connected = True
                self.my_connection = self.connection
                logger.debug(f"Connected to service provided by {self.name!r} at port {self.port}")

        if not self.connected:
            logger.warning(f"Failed to connect service {self.name!r} at port {self.port}")
            raise ConnectionRefusedError(f"Server is not responding after {timeout}s")

    def stop(self) -> None:
        self.retry = False

    def close_connection(self) -> None:
        self.connected = False
        self.retry = True
        self.connection.close()


class ExternalSystem(System):

    __slots__ = ("_process",)

    def __init__(self, name: str, **kwargs):
        self._process = None
        # here _initialize will be called then user setup
        super().__init__(name, **kwargs)

    def serialize_data(self) -> Dict[str, Any]:
        """Serialize all input data into a dictionary"""
        return {name: port.serialize_data() for name, port in self.inputs.items()}

    @abstractmethod
    def send_inputs(self) -> None:
        pass

    @abstractmethod
    def read_outputs(self) -> Any:
        pass


class TCPSystem(ExternalSystem):
    def __init__(
        self,
        name: str,
        init_variables: Optional[dict] = None,
        port: Optional[int] = 13000,
        **kwargs,
    ):
        object.__setattr__(self, "_port", port)
        object.__setattr__(self, "_client", Client(name, port))
        object.__setattr__(
            self, "_service", {"exec": str(), "script": str(), "arguments": list()}
        )

        # here _initialize will be called then user setup
        super().__init__(name, init_variables, **kwargs)

    def call_setup_run(self):
        super().call_setup_run()
        self._launch_service()
        self._client.connect_server()

        self._client.send_message(self._wrap_inputs())
        msg = self._client.wait_for_message()
        logger.debug(
        	f"Service provided by {self.name!r} is running and returned message {msg!r}"
        )

    def compute(self):
        self._client.send_message(self._wrap_inputs())
        out = self._client.wait_for_message()

        if out == "see you soon":
            logger.debug(
            	f"Successfully disconnected from service provided by {self.name!r}"
            )
            self._client.close_connection()

    def call_clean_run(self):
        try:
            self.close_service()
        except:
            pass
        else:
            self._client.close_connection()
        self._process.terminate()
        super().call_clean_run()

    def close_service(self):
        self._client.send_message("shutdown_service")
        out = self._client.wait_for_message()
        logger.debug(
        	f"Successfully disconnected from service provided by {self.name!r}"
        )

    def _wrap_inputs(self) -> str:
        return json.dumps(self.serialize_data(), cls=JSONEncoder)

    def _launch_service(self) -> None:
        # Make sure command exists
        service = self._service
        command = service['exec']
        if not isinstance(command, str):
            raise TypeError(
                f"Executable of external system {self.name!r} must be a string; got {command!r}")

        if not command:
            raise TypeError(f"Executable of external system {self.name!r} is not defined")

        # Suppress message from find_executable function, we'll handle it
        numpy.distutils.log.set_verbosity(-1)

        command_full_path = find_executable(command)
        if not command_full_path:
            raise ValueError(f"Requested command '{command}' cannot be found")

        command_for_shell_proc = [command, service['script']] + service['arguments']

        if sys.platform == "win32":
            command_for_shell_proc = ["cmd.exe", "/c"] + command_for_shell_proc

        self._process = subprocess.Popen(command_for_shell_proc,
            stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    def send_inputs(self) -> None:
        # TODO use this method to send inputs
        pass

    def read_outputs(self) -> Any:
        # TODO use this method to read outputs
        pass
