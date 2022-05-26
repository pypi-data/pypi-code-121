from .core import (
    SingerState,
)
from fa_purity.frozen import (
    freeze,
)
from fa_purity.json import (
    JsonObj,
    JsonValue,
)


def encode_state(state: SingerState) -> JsonObj:
    return freeze(
        {
            "type": JsonValue("STATE"),
            "value": JsonValue(state.value),
        }
    )
