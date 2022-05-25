from collections import UserDict as _UserDict
from symtable import SymbolTable
from typing import (
    TYPE_CHECKING,
    Any,
    Callable,
    Dict,
    KeysView,
    NewType,
    Optional,
    TypedDict,
    Union,
)

from jetpack import _utils

Symbol = NewType("Symbol", str)


class DuplicateKeyError(LookupError):
    pass


class _SymbolTable:
    def __init__(self) -> None:
        self.registered_symbols: Dict[Symbol, Callable[..., Any]] = {}
        self.registered_endpoints: Dict[str, str] = {}
        self._enable_key_overwrite: bool

    def register(
        self, func: Callable[..., Any], endpoint_path: Optional[str] = None
    ) -> Symbol:
        name = Symbol(_utils.qualified_func_name(func))
        if name in self.registered_symbols and not self._enable_key_overwrite:
            raise DuplicateKeyError(f"Function name {name} is already registered")
        if endpoint_path in self.registered_endpoints:
            raise DuplicateKeyError(
                f"Endpoint {endpoint_path} is already registered with Function {self.registered_endpoints[endpoint_path]}"
            )

        # Registering the jetroutine
        self.registered_symbols[name] = func
        # Registering the endpoint
        if endpoint_path is not None:
            # Saving a mapping of endpoint path to jetroutine name to recognize which
            # jetroutines have endpoints and what are their paths, for runtime.
            self.registered_endpoints[endpoint_path] = name
        return name

    def defined_symbols(self) -> KeysView[Symbol]:
        # returns a list of [jetroutine_names]
        return self.registered_symbols.keys()

    def get_registered_symbols(self) -> Dict[Symbol, Callable[..., Any]]:
        # returns a mapping of {jetroutine_name: callable python function}
        return self.registered_symbols

    def get_registered_endpoints(self) -> Dict[str, str]:
        # returns a mapping of {endpoint_path: jetroutine_name}
        return self.registered_endpoints

    def enable_key_overwrite(self, enable: bool) -> None:
        self._enable_key_overwrite = enable


# making _SymbolTable a singleton
_symbol_table = _SymbolTable()


def get_symbol_table() -> _SymbolTable:
    return _symbol_table


def clear_symbol_table_for_test() -> None:
    _symbol_table.registered_symbols = {}
    _symbol_table.registered_endpoints = {}
    _symbol_table._enable_key_overwrite = False
