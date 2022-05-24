from typing import Any, Optional, Type

from ...meta import non_default_kwargs
from ...meta.code_repr import CodeRepresentation, from_init
from ..._ClassRegistry import ClassRegistry
from .._typing import OptionsList
from ._Option import Option


class ClassOption(Option):
    """
    Option which selects a class from a class registry.
    Selection can only be made from aliases.
    """
    def __init__(self,
                 *flags: str,
                 registry: ClassRegistry,
                 default: Type = ...,
                 required: bool = ...,
                 metavar: str = ...,
                 help: str = ...):
        # Capture the code-representation of the option
        code_representation: CodeRepresentation = from_init(self, locals())

        # Save the registry
        self._registry: ClassRegistry = registry

        # Make sure there are some choices to choose from
        choices = tuple(registry.aliases())
        if len(choices) == 0:
            raise ValueError("No classes to choose from")

        super().__init__(code_representation,
                         *flags,
                         choices=choices,
                         **non_default_kwargs(ClassOption.__init__, locals()))

    def _namespace_value_to_internal_value(self, namespace_value: str) -> Optional[type]:
        return self._registry.find(namespace_value)

    def _internal_value_to_namespace_value(self, internal_value: type) -> Optional[str]:
        return self._registry.get_alias(internal_value)

    def _namespace_value_to_options_list(self, namespace_value: str) -> OptionsList:
        return [self._flags[0], namespace_value]

    def _validate_internal_value(self, internal_value: Any):
        # Internal values are classes
        if not isinstance(internal_value, type):
            raise TypeError(f"Class-registry option expects classes for internal values")

        # Make sure it's an aliased class
        if self._registry.get_alias(internal_value) is None:
            raise ValueError(f"Type '{internal_value.__qualname__}' is not a valid type for this option")

    def _validate_namespace_value(self, namespace_value: Any):
        # Namespace value should be a string otherwise
        if not isinstance(namespace_value, str):
            raise TypeError(f"Class-registry options expect string namespace values")

        # The string should be a registered alias
        if not self._registry.has_alias(namespace_value):
            raise NameError(f"Registry has no alias '{namespace_value}'")
