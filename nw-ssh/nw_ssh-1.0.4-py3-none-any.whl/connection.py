import re
import asyncio
from typing import Optional, List, Any

import asyncssh.connection
import asyncssh.stream

from . import exception


class SSHConnection(object):
    def __init__(
        self,
        host: str,
        username: str,
        delimiter: str,
        port: int = 22,
        password: Optional[str] = None,
        client_keys: Optional[List[str]] = None,
        passphrase: Optional[str] = None,
        known_hosts_file: Optional[str] = None,
        timeout: int = 10,
        term_type: str = 'vt100',
    ) -> None:
        self.host = host
        self.port = port
        self.username = username
        self.password = password
        self.client_keys = client_keys
        self.passphrase = passphrase
        self.known_hosts_file = known_hosts_file
        self.delimiter = delimiter
        self.timeout = timeout
        self.term_type = term_type
        self.login_message = ''
        self._conn: Optional[asyncssh.connection.SSHClientConnection] = None
        self._writer: Optional[asyncssh.stream.SSHWriter] = None
        self._reader: Optional[asyncssh.stream.SSHReader] = None

    async def open(
        self,
        delimiter: Optional[str] = None,
        timeout: Optional[int] = None,
    ) -> None:
        if delimiter is None:
            delimiter = self.delimiter

        if timeout is None:
            timeout = self.timeout

        try:
            await asyncio.wait_for(
                self._open(delimiter=delimiter),
                timeout=timeout)
        except Exception:
            await self.close()
            raise

    async def _open(self, delimiter: str) -> None:
        self._conn = await asyncssh.connection.connect(
            host=self.host,
            port=self.port,
            username=self.username,
            password=self.password,
            client_keys=self.client_keys,
            passphrase=self.passphrase,
            known_hosts=self.known_hosts_file,
        )
        self._writer, self._reader, _ = await self._conn.open_session(term_type=self.term_type)
        output = await self._read_until(delimiter=delimiter)
        self.login_message = output

    async def close(self) -> None:
        if self._conn is not None:
            self._conn.close()
            await self._conn.wait_closed()
        self._conn = None
        self._writer = None
        self._reader = None

    async def __aenter__(self) -> "SSHConnection":
        await self.open()
        return self

    async def __aexit__(self, *args) -> None:
        await self.close()

    async def send(
        self,
        input: str,
        delimiter: Optional[str] = None,
        timeout: Optional[int] = None,
    ) -> str:
        if delimiter is None:
            delimiter = self.delimiter

        if timeout is None:
            timeout = self.timeout

        output = await asyncio.wait_for(
            self._send(input=input, delimiter=delimiter),
            timeout=timeout)

        return output

    async def _send(self, input: str, delimiter: str) -> str:
        if self._writer is None:
            raise exception.Error(f"No connection")

        normalized_input = self._normalize_input(input=input)
        self._writer.write(normalized_input)

        output = await self._read_until(delimiter=delimiter)
        return output

    async def _read_until(self, delimiter: str) -> str:
        if self._reader is None:
            raise exception.Error(f"No connection")

        buffer = ''
        while True:
            data = await self._reader.read(1024)
            if not data:
                return self._normalize_output(buffer)

            buffer = buffer + data

            m = re.search(delimiter, buffer)
            if m:
                return self._normalize_output(buffer)

    @staticmethod
    def _normalize_input(input: str) -> str:
        return input.rstrip() + '\n'

    @staticmethod
    def _normalize_output(output: str) -> str:
        # Replace \r
        output_1 = re.sub(r'\r\n|\r', '\n', output)

        # Delete ANSI color codes
        output_2 = re.sub(r'\x1b\[[0-9;]*m', '', output_1)

        return output_2
