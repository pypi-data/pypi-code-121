from collections.abc import Hashable
from typing import TypeVar, TYPE_CHECKING, Union

if TYPE_CHECKING:

    from .channel import Channel, Group
    from .hook import Hook, ResourceHook
    from .plug import Plug


Object = Union["Plug", "Hook", "Channel", "Group"]

TAny = TypeVar("TAny")
TKey = TypeVar("TKey", bound=Hashable)

TObject = TypeVar("TObject", bound=Object)
TResource = TypeVar("TResource", bound="ResourceHook")
