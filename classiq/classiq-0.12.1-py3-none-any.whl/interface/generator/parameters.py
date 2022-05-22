from typing import TYPE_CHECKING, Any, Union

import pydantic

if TYPE_CHECKING:
    from typing_extensions import TypeAlias
else:
    TypeAlias = Any


class Parameter(pydantic.BaseModel):

    name: str = pydantic.Field(description="The name of the parameter")


ParameterFloatType: TypeAlias = Union[float, Parameter]
