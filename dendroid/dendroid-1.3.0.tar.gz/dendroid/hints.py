from typing import Callable

from .core import (hints as _hints,
                   maps as _maps,
                   sets as _sets)

Key = _hints.Key
Value = _hints.Value
Item = _hints.Item
Order = _hints.Order
Map = _maps.Map
Set = _sets.Set
MapFactory = Callable[..., Map]
SetFactory = Callable[..., Set]
