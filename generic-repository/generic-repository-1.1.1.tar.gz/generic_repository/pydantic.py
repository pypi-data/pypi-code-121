from typing import Any, Generic, Type, TypeVar

import pydantic

from .mapper import Mapper

_Model = TypeVar("_Model", bound=pydantic.BaseModel)


class PydanticDictMapper(Mapper[_Model, dict], Generic[_Model]):
    """Pydantic to dict converter.

    Example:
    >>> class A(pydantic.BaseModel):
    ...     x: int
    ...
    >>> class B:
    ...     x: int
    ...     def __init__(self, x: int):
    ...         self.x = x
    ...
    >>> PydanticDictMapper(B)
    Traceback (most recent call last):
      ...
    TypeError: ...
    >>> mapper=PydanticDictMapper(A)

    >>> mapper(A(x=3))
    {'x': 3}
    >>> mapper(B(3))
    Traceback (most recent call last):
      ...
    AssertionError: ...
    >>>
    """

    def __init__(self, *model_classes: Type[_Model]) -> None:
        for cls in model_classes:
            if not issubclass(cls, pydantic.BaseModel):
                raise TypeError(
                    "The class `{class_name}` is not a pydantic model.".format(
                        class_name=f"{cls.__module__}.{cls.__qualname__}"
                    )
                )

        super().__init__()

        self.model_classes = model_classes

    def map_item(self, item: _Model, **kwargs) -> dict:
        if not any(map(lambda x: isinstance(item, x), self.model_classes)):
            raise AssertionError("The passed object isnot of any provided class.")

        return item.dict(**kwargs)


class PydanticObjectMapper(Mapper[Any, _Model], Generic[_Model]):
    def __init__(self, model_class: Type[_Model]) -> None:
        self.model_class = model_class

    def map_item(self, item, **kwargs: Any):
        assert self.model_class.Config.orm_mode
        return self.model_class.from_orm(item)
