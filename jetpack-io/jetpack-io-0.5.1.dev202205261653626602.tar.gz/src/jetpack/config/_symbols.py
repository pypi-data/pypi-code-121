from dataclasses import dataclass
from typing import Any, Callable, Dict, KeysView, List, Optional

from schedule import Job as ScheduleJob

from jetpack import _utils


class DuplicateKeyError(LookupError):
    pass


@dataclass
class SymbolData:
    name: str
    func: Callable[..., Any]
    endpoint: Optional[str] = None
    schedule: Optional[str] = None
    repeat_pattern: Optional[ScheduleJob] = None


class _SymbolTable:
    table: Dict[str, SymbolData] = {}

    def __init__(self) -> None:
        self._enable_key_overwrite: bool

    def register(
        self,
        func: Callable[..., Any],
        endpoint: Optional[str] = None,
        schedule: Optional[str] = None,
        repeat_pattern: Optional[ScheduleJob] = None,
    ) -> str:
        name = _utils.qualified_func_name(func)
        if name in self.table and not self._enable_key_overwrite:
            raise DuplicateKeyError(f"Function name {name} is already registered")

        # Add jetroutine to table
        self.table[name] = SymbolData(
            name=name,
            func=func,
            endpoint=endpoint,
            schedule=schedule,
            repeat_pattern=repeat_pattern,
        )
        return name

    def get(self, symbol: str) -> Optional[SymbolData]:
        return self.table.get(symbol)

    def getX(self, symbol: str) -> SymbolData:
        symbolData = self.table.get(symbol)
        if not symbolData:
            raise LookupError(f"No symbol with name {symbol}")
        return symbolData

    def defined_symbols(self) -> KeysView[str]:
        # returns a list of [jetroutine_names]
        return self.table.keys()

    def get_registered_symbols(self) -> Dict[str, Callable[..., Any]]:
        # returns a mapping of {jetroutine_name: callable python function}
        return dict([(s.name, s.func) for s in self.table.values()])

    def get_cronjobs(self) -> List[SymbolData]:
        return [s for s in self.table.values() if s.schedule or s.repeat_pattern]

    def get_registered_endpoints(self) -> Dict[str, str]:
        # returns a mapping of {endpoint_path: jetroutine_name}
        return dict([(s.name, s.endpoint) for s in self.table.values() if s.endpoint])

    def enable_key_overwrite(self, enable: bool) -> None:
        self._enable_key_overwrite = enable


# making _SymbolTable a singleton
_symbol_table = _SymbolTable()


def get_symbol_table() -> _SymbolTable:
    return _symbol_table


def clear_symbol_table_for_test() -> None:
    _symbol_table.table = {}
    _symbol_table._enable_key_overwrite = False
