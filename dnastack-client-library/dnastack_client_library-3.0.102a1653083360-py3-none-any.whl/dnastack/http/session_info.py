import json
import os
import re
import shutil
from abc import ABC
from json import loads
from threading import Lock
from typing import Optional, Dict, Any

import yaml
from imagination.decorator import service, EnvironmentVariable
from imagination.decorator.config import Service
from pydantic import BaseModel
from time import time

from dnastack.constants import CLI_DIRECTORY
from dnastack.common.logger import get_logger


class SessionInfoHandler(BaseModel):
    auth_info: Dict[str, Any]


class SessionInfo(BaseModel):
    model_version: int = 3

    config_hash: Optional[str]
    access_token: Optional[str]
    refresh_token: Optional[str]
    scope: Optional[str]
    token_type: str

    handler: Optional[SessionInfoHandler]  # Added in v4

    # Pre-computed Properties
    issued_at: int  # Epoch timestamp (UTC)
    valid_until: int  # Epoch timestamp (UTC)

    def is_valid(self) -> bool:
        return time() <= self.valid_until


# Alias for backward-compatibility with early release candidates
Session = SessionInfo


class UnknownSessionError(RuntimeError):
    """ Raised when an unknown session is requested """


class BaseSessionStorage(ABC):
    """
    Base Storage Adapter for Session Information Manager

    It requires the implementations of `__contains__` for `in` operand, `__getitem__`, `__setitem__`, and `__delitem__`
    for dictionary-like API.
    """
    def __contains__(self, id: str) -> bool:
        raise NotImplementedError()

    def __getitem__(self, id: str) -> Optional[SessionInfo]:
        raise NotImplementedError()

    def __setitem__(self, id: str, session: SessionInfo):
        raise NotImplementedError()

    def __delitem__(self, id: str):
        raise NotImplementedError()


class InMemorySessionStorage(BaseSessionStorage):
    """
    In-memory Storage Adapter for Session Information Manager

    This is for testing.
    """
    def __init__(self):
        self.__logger = get_logger(type(self).__name__)
        self.__cache_map: Dict[str, SessionInfo] = dict()

    def __contains__(self, id: str) -> bool:
        return id in self.__cache_map

    def __getitem__(self, id: str) -> Optional[SessionInfo]:
        return self.__cache_map.get(id)

    def __setitem__(self, id: str, session: SessionInfo):
        self.__cache_map[id] = session

    def __delitem__(self, id: str):
        del self.__cache_map[id]


@service.registered(
    params=[
        EnvironmentVariable('DNASTACK_SESSION_DIR',
                            default=os.path.join(CLI_DIRECTORY, 'sessions'),
                            allow_default=True)
    ]
)
class FileSessionStorage(BaseSessionStorage):
    """
    Filesystem Storage Adapter for Session Information Manager

    This is used by default.
    """
    _PATH_BLOCK_SIZE = 16

    def __init__(self, dir_path : str):
        self.__logger = get_logger(type(self).__name__)
        self.__dir_path = dir_path

        if not os.path.exists(self.__dir_path):
            os.makedirs(self.__dir_path, exist_ok=True)

    def __contains__(self, id: str) -> bool:
        return os.path.exists(self.__get_file_path(id))

    def __getitem__(self, id: str) -> Optional[SessionInfo]:
        final_file_path = self.__get_file_path(id)

        with open(final_file_path, 'r') as f:
            content = f.read()

        return SessionInfo(**loads(content))

    def __setitem__(self, id: str, session: SessionInfo):
        final_file_path = self.__get_file_path(id)
        temp_file_path = f'{final_file_path}.{time()}.swap'

        content: str = session.json(indent=2)

        os.makedirs(os.path.dirname(final_file_path), exist_ok=True)
        with open(temp_file_path, 'w') as f:
            f.write(content)
        shutil.copy(temp_file_path, final_file_path)
        os.unlink(temp_file_path)

    def __delitem__(self, id: str):
        final_file_path = self.__get_file_path(id)
        os.unlink(final_file_path)

    def __get_file_path(self, id: str) -> str:
        path_blocks = []

        remaining_key = id
        while remaining_key:
            path_blocks.append(remaining_key[:self._PATH_BLOCK_SIZE])
            remaining_key = remaining_key[self._PATH_BLOCK_SIZE:]

        return f'{os.path.join(self.__dir_path, *path_blocks)}.json'


@service.registered(
    params=[
        Service(FileSessionStorage),
        # Fixed session info (YAML or JSON)
        EnvironmentVariable('DNASTACK_SESSION', default=None, allow_default=True),
        # Fixed session info file (YAML or JSON)
        EnvironmentVariable('DNASTACK_SESSION_FILE', default=None, allow_default=True),
    ],
    auto_wired=False
)
class SessionManager:
    """ Session Information Manager """
    def __init__(self,
                 storage: BaseSessionStorage,
                 static_session: Optional[str] = None,
                 static_session_file: Optional[str] = None):
        self.__logger = get_logger(type(self).__name__)
        self.__storage = storage
        self.__change_locks: Dict[str, Lock] = dict()
        self.__static_session: Optional[SessionInfo] = None

        self.__logger.debug('Session Storage: %s', type(self.__storage).__name__)

        # Initialize the static session, used by all sessions.
        raw_static_session: Optional[str] = None
        if static_session_file and os.path.exists(static_session_file):
            # Retrieve the session info from the given file path.
            with open(static_session_file, 'r') as f:
                raw_static_session = f.read().strip()
            self.__logger.debug('Restored the static session info from the given JSON/YAML file')
        elif static_session:
            # Retrieve the session info from the given argument directly.
            raw_static_session = static_session.strip()
            self.__logger.debug('Restored the static session info from the given JSON/YAML string')
        if raw_static_session:
            # If the static session info is given, load it here.
            if re.search(r'^\{', raw_static_session):
                # Assume to be a JSON-formatted string.
                self.__static_session = SessionInfo(**json.loads(raw_static_session))
            else:
                # Assume to be a YAML-formatted string.
                self.__static_session = SessionInfo(**yaml.load(raw_static_session, Loader=yaml.SafeLoader))
            self.__logger.debug('Loaded the static session info')

    def restore(self, id: str) -> Optional[SessionInfo]:
        with self.__lock(id):
            if id not in self.__storage:
                return None

            session = self.__storage[id]

        return session

    def save(self, id: str, session: SessionInfo):
        # Note (1): This is designed to have file operation done as quickly as possible to reduce race conditions.
        # Note (2): Instead of interfering with the main file directly, the new content is written to a temp file before
        #           swapping with the real file to minimize the I/O block.
        with self.__lock(id):
            self.__storage[id] = session

    def delete(self, id: str):
        with self.__lock(id):
            try:
                if id not in self.__storage:
                    return
                del self.__storage[id]
            finally:
                del self.__change_locks[id]

    def __lock(self, id) -> Lock:
        if id not in self.__change_locks:
            self.__change_locks[id] = Lock()
        return self.__change_locks[id]