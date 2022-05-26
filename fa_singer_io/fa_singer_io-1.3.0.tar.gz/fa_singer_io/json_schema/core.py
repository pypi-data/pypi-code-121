from ._inner import (
    InnerJsonSchema,
)
from dataclasses import (
    dataclass,
)
from fa_purity import (
    JsonObj,
    Result,
)
from fa_purity.json.transform import (
    to_raw,
)
from jsonschema.exceptions import (
    ValidationError,
)


@dataclass(frozen=True)
class JsonSchema:
    _inner: InnerJsonSchema

    def validate(self, record: JsonObj) -> Result[None, ValidationError]:
        try:
            self._inner.validator.validate(to_raw(record))  # type: ignore[misc]
            return Result.success(None)
        except ValidationError as error:  # type: ignore[misc]
            return Result.failure(error)

    def encode(self) -> JsonObj:
        return self._inner.raw
