from escriptorium_connector.utils.pydantic_dataclass_fix import dataclass
from typing import List
from escriptorium_connector.dtos.super_dtos import PagenatedResponse


@dataclass(init=True, frozen=True)
class GetOnboarding:
    onboarding: bool


@dataclass
class GetUser(PagenatedResponse):
    results: List[GetOnboarding]
