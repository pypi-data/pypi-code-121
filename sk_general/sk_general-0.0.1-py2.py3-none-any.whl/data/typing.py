from typing import Union, Protocol, Number, TypeVar, Literal, Mapping, Any

KeyTs = Union[Number, str]
KeyT = TypeVar("KeyT", bound=KeyTs)

DataT = Union[dict, tuple]
DataHandlingModeT = TypeVar("DataHandlingModeT", Literal["train"], Literal["predict"])


# TODO: is this too restrictive a protocol/signature for datahandling
class AbstractDataHandler(Protocol):
    """
    Takes a single data object and formats it for training or prediction.
    """

    def __call__(self, data: DataT, mode: DataHandlingModeT) -> DataT:
        ...
