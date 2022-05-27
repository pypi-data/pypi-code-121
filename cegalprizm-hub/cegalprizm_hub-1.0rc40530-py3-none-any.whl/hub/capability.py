# Copyright 2022 Cegal AS
# All rights reserved.
# Unauthorized copying of this file, via any medium is strictly prohibited.

from types import FunctionType

from .payload_auth import PayloadAuth


class HubCapability:

    def __init__(self, wellknown_payload_identifier: str, task: FunctionType, friendly_name: str, description: str, payload_auth: PayloadAuth, major_version: int = 0, minor_version: int = 0):
        self._wellknown_payload_identifier = wellknown_payload_identifier
        self._friendly_name = friendly_name
        self._description = description
        self._payload_auth = payload_auth
        self._major_version = major_version
        self._minor_version = minor_version
        self._task = task

    @property
    def wellknown_payload_identifier(self) -> str:
        return self._wellknown_payload_identifier

    @property
    def friendly_name(self) -> str:
        return self._friendly_name

    @property
    def description(self) -> str:
        return self._description

    @property
    def payload_auth(self) -> PayloadAuth:
        return self._payload_auth

    @property
    def major_version(self) -> int:
        return self._major_version

    @property
    def minor_version(self) -> int:
        return self._minor_version

    @property
    def task(self) -> FunctionType:
        return self._task
