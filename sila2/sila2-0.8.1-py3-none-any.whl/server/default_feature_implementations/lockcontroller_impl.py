from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Any, List, Optional, Union

from sila2.features.lockcontroller import (
    InvalidLockIdentifier,
    LockControllerBase,
    LockControllerFeature,
    LockServer_Responses,
    ServerAlreadyLocked,
    ServerNotLocked,
    UnlockServer_Responses,
)
from sila2.framework import Command, Feature, FullyQualifiedIdentifier, Property
from sila2.server import MetadataInterceptor, SilaServer
from sila2.server.metadata_dict import MetadataDict


@dataclass
class Lock:
    token: str
    timeout_duration: timedelta
    last_usage: datetime = field(default_factory=lambda: datetime.now())

    @property
    def is_expired(self):
        return (datetime.now() - self.timeout_duration) > self.last_usage


class LockControllerImpl(LockControllerBase):
    def __init__(self, parent_server: SilaServer):
        super().__init__(parent_server=parent_server)
        self.lock: Optional[Lock] = None
        self.parent_server.add_metadata_interceptor(LockControllerInterceptor(self))

    @property
    def is_locked(self) -> bool:
        if self.lock is None:
            return False

        if self.lock.is_expired:
            self.lock = None

        return self.lock is not None

    def get_IsLocked(self, *, metadata: MetadataDict) -> bool:
        return self.is_locked

    def LockServer(self, LockIdentifier: str, Timeout: int, *, metadata: MetadataDict) -> LockServer_Responses:
        if self.is_locked:
            raise ServerAlreadyLocked

        self.lock = Lock(LockIdentifier, timedelta(seconds=Timeout))
        return LockServer_Responses()

    def UnlockServer(self, LockIdentifier: str, *, metadata: MetadataDict) -> UnlockServer_Responses:
        if not self.is_locked:
            raise ServerNotLocked

        if self.lock.token != LockIdentifier:
            raise InvalidLockIdentifier

        self.lock = None
        return UnlockServer_Responses()

    def get_calls_affected_by_LockIdentifier(self) -> List[Union[Feature, Command, Property, FullyQualifiedIdentifier]]:
        return [
            feature
            for feature in self.parent_server.features.values()
            if feature._identifier not in ("SiLAService", "LockController")
        ]


class LockControllerInterceptor(MetadataInterceptor):
    def __init__(self, lockcontroller_impl: LockControllerImpl):
        super().__init__([LockControllerFeature["LockIdentifier"]])
        self.lockcontroller_impl = lockcontroller_impl

    def intercept(self, parameters: Any, metadata: MetadataDict, target_call: FullyQualifiedIdentifier) -> None:
        token: str = metadata[LockControllerFeature["LockIdentifier"]]
        if token != self.lockcontroller_impl.lock.token:
            raise InvalidLockIdentifier
