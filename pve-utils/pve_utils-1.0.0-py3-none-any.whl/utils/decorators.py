from functools import wraps
from typing import Callable

import paramiko

from pve_utils.utils import pprint

from .ssh import SSHconnectable


def with_ssh(func) -> Callable:
    @wraps(func)
    def wrapper(self, *args, **kwargs):
        assert issubclass(type(self), SSHconnectable), (
            "Декторатор with_ssh можно использовать"
            "только для классов SSHconnectable"
        )

        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        try:
            client.connect(
                hostname=self.host,
                port=self.port,
                username=self.user,
                password=self.password,
            )
            pprint.success(f"Successfully connected to SSH: {self.host}")
        except paramiko.SSHException as e:
            pprint.error(f"Failed to connect: {self.host}")
            pprint.info("Traceback:")
            pprint.normal(e)

        return func(self, client, *args, **kwargs)
        client.close()

    return wrapper


__all__ = ("with_ssh",)
