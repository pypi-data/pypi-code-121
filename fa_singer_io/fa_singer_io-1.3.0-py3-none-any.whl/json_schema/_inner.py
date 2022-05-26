from dataclasses import (
    dataclass,
    field,
)
from fa_purity.json.factory import (
    JsonObj,
)
from jsonschema import (
    Draft4Validator,
)


@dataclass(frozen=True)
class InnerJsonSchema:
    raw: JsonObj
    validator: Draft4Validator = field(compare=False)
