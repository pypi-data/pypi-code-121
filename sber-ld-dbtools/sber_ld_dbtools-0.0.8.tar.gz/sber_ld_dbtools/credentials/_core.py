from getpass import getpass
from io import StringIO
from os import PathLike
from subprocess import run as run_cmd, CalledProcessError
from typing import Optional, Union

from varutils.types import NoneType
from varutils.typing import check_type_compatibility

__all__ = (
    'PasswordKeeper',
    'KerberosPrincipalSwitcher',
    'set_default_kerberos_principal',
)


class PasswordKeeper:
    __slots__ = ('username', 'host', 'prompt', '__password')

    def __init__(self,
                 username: str,
                 *,
                 host: Optional[str] = None,
                 prompt: str = '',
                 passwd_file_or_buffer: Union[str, bytes, PathLike, StringIO, None] = None) -> None:

        check_type_compatibility(username, str)
        check_type_compatibility(host, (str, NoneType), 'str or None')
        check_type_compatibility(prompt, str)
        check_type_compatibility(passwd_file_or_buffer, (str, bytes, PathLike, StringIO, NoneType))

        self.username = username
        self.host = host
        self.prompt = prompt
        if isinstance(passwd_file_or_buffer, (str, bytes, PathLike)):
            with open(passwd_file_or_buffer, 'r') as f:
                self.__password = f.read().strip('\n')
        elif isinstance(passwd_file_or_buffer, StringIO):
            self.__password = passwd_file_or_buffer.read().strip('\n')
        else:
            self.__password = getpass(prompt=prompt)

    def set_password(self) -> 'PasswordKeeper':
        self.__password = getpass(prompt=self.prompt)
        return self

    def get_username(self) -> str:
        return self.username

    def get_host(self) -> str:
        if self.host is None:
            raise ValueError("host is not set")
        return self.host

    def get_username_with_host(self) -> str:
        return f'{self.username}@{self.get_host()}'

    def get_password(self) -> str:
        return self.__password


def set_default_kerberos_principal(passkeeper: PasswordKeeper) -> None:
    username_with_host = passkeeper.get_username_with_host()
    password = passkeeper.get_password()

    cmd_base = f'kinit {username_with_host}'
    completed_process = run_cmd(
        f"unset HISTFILE && {cmd_base} <<< '{password}'",
        shell=True,
        capture_output=True,
        text=True
    )
    if completed_process.returncode:
        raise CalledProcessError(
            completed_process.returncode,
            f'{cmd_base} <<< ***',
            completed_process.stderr.strip()
        )


class KerberosPrincipalSwitcher:
    __slots__ = ('__context_credentials', '__exit_credentials')

    def __init__(self, context_credentials: PasswordKeeper, exit_credentials: PasswordKeeper) -> None:
        check_type_compatibility(context_credentials, PasswordKeeper)
        check_type_compatibility(exit_credentials, PasswordKeeper)
        self.__context_credentials = context_credentials
        self.__exit_credentials = exit_credentials

    def __enter__(self) -> None:
        set_default_kerberos_principal(self.__context_credentials)

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        set_default_kerberos_principal(self.__exit_credentials)
        if exc_type is not None:
            raise
