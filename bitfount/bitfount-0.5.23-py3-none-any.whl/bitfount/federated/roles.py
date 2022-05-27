"""Contains mixin for role-finding code."""
from __future__ import annotations

from enum import Enum, unique
from functools import cached_property
import inspect
from typing import Any, Set, Union


@unique
class Role(Enum):
    """Enum representing roles available in factory classes.

    This applies to Protocols, Algorithms and Aggregators.
    """

    # The value should be the function name that returns
    # classes related to that role.
    MODELLER = "modeller"
    WORKER = "worker"


class _RolesMixIn:
    """A mixin providing a list of roles available in a class."""

    def __init__(self, **kwargs: Any) -> None:
        super().__init__()

    # Ideally we will make this a property of the class, so an instance is not
    # required to get this information. However, class properties are not supported
    # until Python 3.9 (when @classmethod can wrap @property) and so this is the
    # best solution until then.
    @cached_property
    def roles(self) -> Set[Role]:
        """The set of roles available for this class."""
        available_roles = set()

        # Find roles that have the correct factory methods on this class.
        for role in Role:
            func_name: str = role.value
            # AttributeError will be thrown if the target attribute doesn't exist
            # at all so we catch that during iteration.
            try:
                if inspect.ismethod(getattr(self, func_name)):
                    available_roles.add(role)
            except AttributeError:
                pass
        return available_roles

    def create(self, role: Union[str, Role], **kwargs: Any) -> Any:
        """Create an instance representing the role specified."""
        r_role: Role = Role(role)

        # If role is available for this class, use the underlying factory method.
        if r_role in self.roles:
            fact_func = getattr(self, r_role.value)
            return fact_func(**kwargs)
        # Otherwise, report not supported role
        else:
            raise ValueError(
                f"Role not supported: {r_role} not usable with {type(self)}"
            )
