# Copyright 2022 Cegal AS
# All rights reserved.
# Unauthorized copying of this file, via any medium is strictly prohibited.

from types import FunctionType
from typing import Dict, Iterator, Tuple

from .capability import HubCapability
from .payload_auth import PayloadAuth


class HubTaskRegistry:

    def __init__(self):
        self._supported_tasks: Dict[str, HubCapability] = {}

    def register_unary_task(self, 
                            wellknown_payload_identifier: str,
                            task: FunctionType,
                            friendly_name: str,
                            description: str,
                            payload_auth: PayloadAuth,
                            major_version: int = 0,
                            minor_version: int = 0) -> Tuple[bool, str]:
        self._supported_tasks[wellknown_payload_identifier] = HubCapability(wellknown_payload_identifier, task, friendly_name, description, payload_auth, major_version, minor_version)

    def get_supported_tasks(self) -> Iterator[HubCapability]:
        for task in self._supported_tasks.values():
            yield task

    def get_unary_task(self, wellknown_payload_identifier) -> FunctionType:
        if wellknown_payload_identifier not in self._supported_tasks.keys():
            return None
        return self._supported_tasks[wellknown_payload_identifier].task
