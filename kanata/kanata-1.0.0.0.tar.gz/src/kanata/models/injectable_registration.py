from .injectable_scope_type import InjectableScopeType
from dataclasses import dataclass, field
from typing import Any, ClassVar, Set, Type

@dataclass
class InjectableRegistration:
    """Holds information about the registration of an injectable type."""

    PROPERTY_NAME: ClassVar[str] = "kanata_injectable_registrations"
    """The name of the property used to hold the list
    of registration objects attached to an injectable type."""

    injectable_type: Type[Any]
    """Gets or sets the type of the injectable object."""

    contract_types: Set[Type[Any]] = field(default_factory=set)
    """Gets or sets the types of the contracts by which an instance of the object is injectable."""

    scope: InjectableScopeType = InjectableScopeType.TRANSIENT
    """Gets or sets the lifetime scope type of the created instances."""

    def __str__(self) -> str:
        return (
            "<InjectableRegistration"
            f" injectable={self.injectable_type},"
            f" contracts={len(self.contract_types)},"
            f" scope={self.scope}>"
        )
