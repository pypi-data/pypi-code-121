import dataclasses
import datetime
from typing import Any, ClassVar, Dict, List, Optional

from servicefoundry.internal.const import ENTITY_JSON_DATETIME_FORMAT

# TODO: switch to Enums for str literals
# TODO: Implement NotImplementedError sections


@dataclasses.dataclass
class Entity:
    createdAt: datetime.datetime = dataclasses.field(repr=False)
    updatedAt: datetime.datetime = dataclasses.field(repr=False)
    list_display_columns: ClassVar[List[str]] = []
    get_display_columns: ClassVar[List[str]] = []

    @classmethod
    def from_dict(cls, dct: Dict[str, Any]):
        if isinstance(dct.get("createdAt"), str):
            dct["createdAt"] = datetime.datetime.strptime(
                dct["createdAt"], ENTITY_JSON_DATETIME_FORMAT
            ).replace(tzinfo=datetime.timezone.utc)
        if isinstance(dct.get("updatedAt"), str):
            dct["updatedAt"] = datetime.datetime.strptime(
                dct["updatedAt"], ENTITY_JSON_DATETIME_FORMAT
            ).replace(tzinfo=datetime.timezone.utc)
        known_attr_names = {field.name for field in dataclasses.fields(cls)}
        known_attrs = {}
        extra_attrs = {}
        for k, v in dct.items():
            if k in known_attr_names:
                known_attrs[k] = v
            else:
                extra_attrs[k] = v

        instance = cls(**known_attrs)
        for attr_name, attr_value in extra_attrs.items():
            if not hasattr(instance, attr_name):
                setattr(instance, attr_name, attr_value)
        return instance

    def to_dict(self) -> Dict[str, Any]:
        return vars(self).copy()


@dataclasses.dataclass
class Cluster(Entity):
    id: str = dataclasses.field(repr=False)
    name: str
    fqn: str
    region: str = dataclasses.field(repr=False)
    list_display_columns: ClassVar[List[str]] = [
        "name",
        "fqn",
        "region",
        "createdAt",
    ]
    get_display_columns: ClassVar[List[str]] = [
        "name",
        "fqn",
        "region",
        "createdAt",
        "updatedAt",
    ]

    def to_dict_for_session(self) -> Dict[str, Any]:
        return dataclasses.asdict(self)

    @property
    def workspaces(self) -> List["Workspace"]:
        raise NotImplementedError


@dataclasses.dataclass
class Workspace(Entity):
    id: str = dataclasses.field(repr=False)
    fqn: str
    name: str
    clusterId: str = dataclasses.field(repr=False)
    createdBy: str = dataclasses.field(repr=False)
    status: str = dataclasses.field(repr=False)
    workspaceTier: Dict[str, Any] = dataclasses.field(repr=False)
    grafanaEndpoint: Optional[str] = dataclasses.field(default=None, repr=False)
    list_display_columns: ClassVar[List[str]] = [
        "name",
        "fqn",
        "status",
        "createdAt",
    ]
    get_display_columns: ClassVar[List[str]] = [
        "name",
        "fqn",
        "createdBy",
        "status",
        "grafanaEndpoint",
        "workspaceTier",
        "createdAt",
        "updatedAt",
    ]

    @classmethod
    def from_dict(cls, dct: Dict[str, Any]):
        dct.setdefault(
            "grafanaEndpoint", dct.get("metadata", {}).get("grafanaEndpoint")
        )
        return super().from_dict(dct)

    def to_dict_for_session(self) -> Dict[str, Any]:
        return dataclasses.asdict(self)

    @property
    def cluster(self) -> Cluster:
        raise NotImplementedError

    @property
    def services(self) -> List["Service"]:
        raise NotImplementedError


@dataclasses.dataclass
class Service(Entity):
    id: str = dataclasses.field(repr=False)
    name: str
    fqn: str
    workspaceId: str = dataclasses.field(repr=False)
    status: str = dataclasses.field(repr=False)
    metadata: Dict[str, Any] = dataclasses.field(repr=False)  # TODO: flatten if needed
    endpointUrl: Optional[str] = dataclasses.field(default=None, repr=False)
    list_display_columns: ClassVar[List[str]] = [
        "name",
        "fqn",
        "status",
        "endpointUrl",
        "createdAt",
    ]
    get_display_columns: ClassVar[List[str]] = [
        "name",
        "fqn",
        "status",
        "endpointUrl",
        "metadata",
        "createdAt",
        "updatedAt",
    ]

    @classmethod
    def from_dict(cls, dct: Dict[str, Any]):
        dct.setdefault("endpointUrl", dct.get("metadata", {}).get("endpointUrl"))
        return super().from_dict(dct)

    @property
    def workspace(self) -> Workspace:
        raise NotImplementedError

    @property
    def deployments(self) -> List["Deployment"]:
        raise NotImplementedError


@dataclasses.dataclass
class Deployment(Entity):
    id: str = dataclasses.field(repr=False)
    name: str
    fqn: str
    serviceId: str = dataclasses.field(repr=False)
    status: int = dataclasses.field(repr=False)
    createdBy: str = dataclasses.field(repr=False)
    componentDef: Dict[str, Any] = dataclasses.field(repr=False)
    secrets: List[Any] = dataclasses.field(repr=False)
    envs: List[Dict[str, Any]] = dataclasses.field(repr=False)
    metadata: Dict[str, Any] = dataclasses.field(repr=False)
    dockerImage: Dict[str, Any] = dataclasses.field(repr=False)
    list_display_columns: ClassVar[List[str]] = [
        "name",
        "fqn",
        "status",
        "createdAt",
    ]
    get_display_columns: ClassVar[List[str]] = [
        "name",
        "fqn",
        "status",
        "componentDef",
        "secrets",
        "envs",
        "dockerImage",
        "metadata",
        "createdBy",
        "createdAt",
        "updatedAt",
    ]

    @property
    def service(self) -> Service:
        raise NotImplementedError


# TODO: Should treat displaying and handling these with more respect as it is sensitive data


@dataclasses.dataclass
class Secret(Entity):
    id: str = dataclasses.field(repr=False)
    name: str
    fqn: str
    value: str = dataclasses.field(repr=False)
    secretGroupId: str = dataclasses.field(repr=False)
    createdBy: str = dataclasses.field(repr=False)
    list_display_columns: ClassVar[List[str]] = [
        "name",
        "fqn",
        "createdAt",
    ]
    get_display_columns: ClassVar[List[str]] = [
        "name",
        "value",
        "createdAt",
        "updatedAt",
    ]

    @property
    def secret_group(self) -> "SecretGroup":
        raise NotImplementedError


@dataclasses.dataclass
class SecretGroup(Entity):
    id: str = dataclasses.field(repr=False)
    name: str
    fqn: str
    createdBy: str = dataclasses.field(repr=False)
    associatedSecrets: List[Secret] = dataclasses.field(repr=False)
    list_display_columns: ClassVar[List[str]] = [
        "name",
        "fqn",
        "createdAt",
    ]
    get_display_columns: ClassVar[List[str]] = [
        "name",
        "fqn",
        "associatedSecrets",
        "createdAt",
        "updatedAt",
    ]

    @classmethod
    def from_dict(cls, dct):
        dct.setdefault(
            "associatedSecrets",
            [Secret.from_dict(s) for s in dct.get("associatedSecrets", [])],
        )
        return super().from_dict(dct)
