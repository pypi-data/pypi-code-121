from dataclasses import dataclass
from gornilo.models.action_names import CHECK, PUT, GET


@dataclass(frozen=True)
class CheckRequest:
    hostname: str
    action: str = CHECK


@dataclass(frozen=True)
class __PutGetBase:
    flag_id: str
    flag: str
    vuln_id: int


@dataclass(frozen=True)
class PutRequest(CheckRequest, __PutGetBase):
    action: str = PUT


@dataclass(frozen=True)
class GetRequest(CheckRequest, __PutGetBase):
    public_flag_id: str = ""
    action: str = GET


@dataclass(frozen=True)
class __PublicFlagIdBase:
    public_flag_id: str
