"""Contains the base abstract class for all transformations."""
from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, ClassVar, Dict, List, Optional, Type, cast
from uuid import uuid4

import attr
import desert
from marshmallow import Schema

from bitfount.transformations.exceptions import TransformationRegistryError
from bitfount.transformations.utils import _MarshmallowYamlShim

TRANSFORMATION_REGISTRY: Dict[str, Type[Transformation]] = {}


# Keyword-only dataclasses allow us to get around the issue of subclasses having
# non-default args following default args (i.e. name and output). Every subclass
# should be marked using the same.
@attr.dataclass(kw_only=True)
class Transformation:
    """The base class that all transformations inherit from.

    By default these will be `attr.dataclass`es and their schemas will be generated
    from this. If more manual control over the schema is needed you may create a nested
    `Schema` class on the transformation that will be used instead. This nested
    class must inherit from `TransformationSchema`.

    Args:
        name: The name of the transformation. If not provided a unique name
            will be generated from the class name.
        output: Whether or not this transformation should be included in the
            final output. Defaults to False.

    Raises:
        TransformationRegistryError: If the transformation name is already in use.
        TransformationRegistryError: If the transformation name hasn't been provided
            and the transformation is not registered.
    """

    # Non-serializable variables
    _registry_name: ClassVar[Optional[str]] = None

    # Serializable variables
    name: Optional[str] = None
    output: bool = False

    def __attrs_post_init__(self) -> None:
        if not self.name:
            self.name = self._gen_name()

    @classmethod
    def __init_subclass__(cls, **kwargs: Any) -> None:
        # Register concrete transformations with the registry
        if cls._registry_name:
            registry_name = cls._registry_name.lower()
            # Fail if name is already registered
            if registry_name in TRANSFORMATION_REGISTRY:
                raise TransformationRegistryError(
                    f"A transformation is already registered with name "
                    f'"{registry_name}"'
                )
            TRANSFORMATION_REGISTRY[registry_name] = cls

    @classmethod
    def schema(cls) -> Schema:
        """Gets an instance of the Schema associated with this Transformation.

        Raises:
            TypeError: If the transformation doesn't have a `TransformationSchema` as
                the schema.
        """
        # If the transformation has a custom schema, use it
        if hasattr(cls, "_Schema"):
            if issubclass(cls._Schema, _TransformationSchema):  # type: ignore[attr-defined] # Reason: hasattr check above # noqa: B950
                return cast(_TransformationSchema, cls._Schema())  # type: ignore[attr-defined] # Reason: hasattr check above # noqa: B950
            else:
                raise TypeError(
                    f"Schema attribute for class {cls.__name__} must be a "
                    f"TransformationSchema instance."
                )
        # Otherwise generate one from desert
        else:
            return desert.schema(cls, meta={"render_module": _MarshmallowYamlShim})

    @classmethod
    def _gen_name(cls) -> str:
        """Generates a unique name for the transformation."""
        if not cls._registry_name:
            raise TransformationRegistryError(
                f'Transformation "{cls.__name__}" isn\'t registered; '
                f"can't generate name."
            )
        slugged_reg_name = "-".join(cls._registry_name.split())
        return f"{slugged_reg_name.lower()}_{uuid4().hex}"


class MultiColumnOutputTransformation(ABC):
    """Marks a Transformation class as producing multi-column output."""

    @property
    @abstractmethod
    def columns(self) -> List[str]:
        """Returns a list of the columns that will be output."""
        raise NotImplementedError


class _TransformationSchema(Schema):
    """A custom schema class for more involved transformations.

    If you are inheriting from this note that you will need to ensure all fields
    in the inheritance hierarchy are included in the inherited schema.
    """

    class Meta:
        render_module = _MarshmallowYamlShim
