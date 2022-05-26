import json
from datetime import datetime
from typing import Dict, List, Optional

from pydantic import BaseModel, Field
from sym.shared.cli.errors import UnknownError

from sym.flow.cli.models.service import SERVICE_KEY_SEPARATOR, BaseService
from sym.flow.cli.models.service_type import ServiceType
from sym.flow.cli.models.user_type import UserType


class CSVMatcher(BaseModel):
    service: BaseService
    value: str = Field(default_value="")

    @classmethod
    def from_dict(cls, service: BaseService, matcher: Dict):
        if service_type := ServiceType.get(service.service_type):
            value = matcher[service_type.matcher]
        else:
            value = json.dumps(matcher)
        return cls(service=service, value=value)

    @property
    def default_key(self) -> Optional[str]:
        if service_type := ServiceType.get(self.service.service_type):
            return service_type.matcher

        return None

    def to_dict(self) -> Dict:
        """Tries to generate the matcher dict if the service matcher key
        is known, otherwise use the value directly.
        """
        if self.default_key:
            return {self.default_key: self.value}

        try:
            return json.loads(self.value)
        except ValueError:
            raise ValueError(
                "Provided identity matcher '{}' for service '{}' should be valid json.".format(
                    self.value, self.service
                )
            )


class Identity(BaseModel):
    service: BaseService
    matcher: dict

    @classmethod
    def from_csv(cls, service_key: str, matcher_value: str) -> "Identity":
        service_type, external_id = Identity.parse_service_key(service_key=service_key)
        service = BaseService(slug=service_type, external_id=external_id)
        matcher = CSVMatcher(service=service, value=matcher_value).to_dict()
        return cls(service=service, matcher=matcher)

    @classmethod
    def parse_service_key(cls, service_key: str) -> List[str]:
        return service_key.split(SERVICE_KEY_SEPARATOR, 1)

    def to_csv(self) -> str:
        return CSVMatcher.from_dict(self.service, self.matcher).value


class User(BaseModel):
    id: str
    identities: List[Identity] = []
    type: UserType = UserType.NORMAL
    # Optional because this is only used to parse from the API, not when creating users
    created_at: Optional[datetime]

    @property
    def sym_email(self) -> str:
        for identity in self.identities:
            if identity.service.service_type == ServiceType.SYM.type_name:
                return identity.matcher["email"]

        raise UnknownError(Exception(f"No Sym Identity found for user id {self.id}"))

    @property
    def sym_identifier(self) -> str:
        """Returns value in the SYM Identity matcher, regardless of email or username"""
        if identifier := next(
            (
                list(identity.matcher.values())[
                    0
                ]  # Assumption is that Sym identity matcher has only one value
                for identity in self.identities
                if identity.service.service_type == ServiceType.SYM.type_name
            ),
            None,
        ):
            return identifier

        raise UnknownError(Exception(f"No Sym Identify found for user id {self.id}"))

    @property
    def identities_without_sym_service(self) -> List[Identity]:
        return self.filtered_identities([ServiceType.SYM.type_name])

    def filtered_identities(self, excluded_service_types: List[str]) -> List[Identity]:
        return [
            identity
            for identity in self.identities
            if identity.service.service_type not in excluded_service_types
        ]

    def get_identity_from_key(self, key: str) -> Optional[Identity]:
        service_type, external_id = Identity.parse_service_key(service_key=key)
        return next(
            iter(
                [
                    i
                    for i in self.identities
                    if i.service.service_type == service_type
                    and i.service.external_id == external_id
                ]
            ),
            None,
        )

    def identity_repr_for_service(self, service: BaseService) -> str:
        if identity := self.get_identity_from_key(service.service_key):
            return identity.to_csv()
        return ""
