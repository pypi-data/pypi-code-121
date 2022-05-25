from abc import ABC, ABCMeta, abstractmethod

from paramiko import SSHClient


class SSHconnectable(ABC, metaclass=ABCMeta):
    user: str
    password: str
    host: str
    port: int

    @abstractmethod
    def exec(self, client: SSHClient, command: str) -> None:
        pass
