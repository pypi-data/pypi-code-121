"""NanamiLang Token Class"""

# This file is a part of NanamiLang Project
# This project licensed under GNU GPL version 2
# Initially made by @jedi2light (aka Stoian Minaiev)

from typing import List

from nanamilang import datatypes
from nanamilang.bdb import (
    BuiltinFunctionsDB, BuiltinMacrosDB
)
from nanamilang.shortcuts import (
    ASSERT_IS_CHILD_OF, ASSERT_COLL_LENGTH_EQUALS_TO,
    ASSERT_COLL_CONTAINS_ITEM, ASSERT_COLLECTION_NOT_EMPTY
)


class Token:
    """NanamiLang Token"""

    _type: str = None
    _valid: bool = True
    _reason: str = None
    _raw_symbol: str = None
    _position_msg: str = ''
    _position: tuple = ('UNK', 1, 1)
    _dt_instance: datatypes.Base = None

    Proxy: str = 'Proxy'
    Invalid: str = 'Invalid'
    ListBegin: str = 'ListBegin'
    ListEnd: str = 'ListEnd'
    Identifier: str = 'Identifier'
    Nil: str = datatypes.Nil.name
    Boolean: str = datatypes.Boolean.name
    String: str = datatypes.String.name
    Date: str = datatypes.Date.name
    FloatNumber: str = datatypes.FloatNumber.name
    IntegerNumber: str = datatypes.IntegerNumber.name
    Keyword: str = datatypes.Keyword.name
    NException: str = datatypes.NException.name
    Symbol: str = datatypes.Symbol.name
    Character: str = datatypes.Character.name

    data_types: List[str] = datatypes.DataType.simple + [Identifier]

    _valid_types: List[str] = [Proxy,
                               Invalid, ListBegin, ListEnd] + data_types

    def __init__(self,
                 _type: str, _value=None,
                 _valid: bool = True, _reason: str = None,
                 _position: tuple = None, _raw_symbol: str = None) -> None:
        """
        Initialize a new NanamiLang Token instance

        Respective Data Type instance will be initialized on __init__ stage

        :param _type: must be a Token.<something>
        :param _value: must be a type of a "_type"
        :param _valid: whether Token is valid or not
        :param _reason: reason why token is invalid?
        :param _position: source position of a symbol
        :param _raw_symbol: this must be a raw symbol
        """

        # if _valid has been passed, verify that it is type of boolean.
        if _valid is not None:
            ASSERT_IS_CHILD_OF(_valid,
                               bool,
                               'Token: <_valid> needs to be a boolean')
            self._valid = _valid
        # if _reason has been passed, verify that it's non-empty string
        if _reason is not None:
            ASSERT_IS_CHILD_OF(_reason,
                               str,
                               'Token: <_reason> needs to be a string')
            ASSERT_COLLECTION_NOT_EMPTY(
                _reason, 'Token: <_reason> could not be empty string!')
            self._reason = _reason
        # if _position has been passed, verify it is triple-items tuple
        if _position is not None:
            ASSERT_IS_CHILD_OF(
                _position,
                tuple, 'Token: <_position> needs to be tuple-triplet!')
            ASSERT_COLL_LENGTH_EQUALS_TO(
                _position,
                3, 'Token: <_position> should contain exactly 3 items')
            self._position = _position
            self._position_msg = ':'.join(map(str, _position))
        # if _raw_symbol has been passed, verify it is non-empty string
        if _raw_symbol is not None:
            ASSERT_IS_CHILD_OF(
                _raw_symbol,
                str, 'Token: <_raw_symbol> value needs to be a string')
            ASSERT_COLLECTION_NOT_EMPTY(
                _raw_symbol,
                'Token: <_raw_symbol> value could not be empty string')
            self._raw_symbol = _raw_symbol
        # _type must be a type of <str> && could not be an empty string
        ASSERT_IS_CHILD_OF(
            _type, str, 'Token: a <_type> value needs to be a string!')
        ASSERT_COLLECTION_NOT_EMPTY(
            _type, 'Token: <_type> value could not be an empty string')
        # _type could not be something different from self._valid_types
        ASSERT_COLL_CONTAINS_ITEM(
            self._valid_types, _type, 'Token: <_type> value is wrong!')
        self._type = _type
        # the code bellow allows to assign 'self._dt_instance' directly
        if _type == Token.Proxy:
            self._dt_instance = _value
            return
        # try to initialize self._dt_instance if _type is the data type
        if _type in self.data_types:
            if _type != Token.Identifier:
                self._dt_instance = (
                    datatypes.DataType.resolve(_type)(_value)
                )
            else:
                resolved_mc = BuiltinMacrosDB.resolve(_value)
                resolved_fn = BuiltinFunctionsDB.resolve(_value)
                resolved_mt = datatypes.type.Type.resolve(_value)
                if resolved_mc:
                    self._dt_instance = datatypes.Macro(resolved_mc)
                elif resolved_fn:
                    self._dt_instance = datatypes.Function(resolved_fn)
                elif resolved_mt:
                    self._dt_instance = resolved_mt  # would be an instance
                else:
                    self._dt_instance = datatypes.Undefined(reference=_value)
                # in case Identifier could not be resolved, mark as Undefined

    def end(self) -> bool:
        """Nanamilang Token, is ListEnd?"""

        return self.type() == Token.ListEnd

    def begin(self) -> bool:
        """NanamiLang Token, is ListBegin?"""

        return self.type() == Token.ListBegin

    def identifier(self) -> bool:
        """Nanamilang Token, is Identifier?"""

        return self._type == Token.Identifier

    def type(self) -> str:
        """NanamiLang Token, self._type getter"""

        return self._type

    def reason(self) -> str:
        """NanamiLang Token, self._reason getter"""

        return self._reason

    def position(self) -> tuple:
        """NanamiLang Token, self._position getter"""

        return self._position

    def dt(self) -> datatypes.Base:
        """NanamiLang Token, self._dt_instance getter"""

        return self._dt_instance

    def __repr__(self) -> str:
        """NanamiLang Token, _repr__() method implementation"""

        return self.__str__()

    def __str__(self) -> str:
        """NanamiLang Token, __str__() method implementation"""

        if self._valid:
            if self._dt_instance is not None:
                return f'<{self._type}>: {self._dt_instance.format()}'
            return f'<{self._type}>'
        return f'Invalid token at <{self._position_msg}>. Reason: {self._reason}'
