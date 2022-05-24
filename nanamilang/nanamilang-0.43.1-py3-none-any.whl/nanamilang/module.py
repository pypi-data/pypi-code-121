"""NanamiLang Module Class"""

# This file is a part of NanamiLang Project
# This project licensed under GNU GPL version 2
# Initially made by @jedi2light (aka Stoian Minaiev)

import time
from typing import List, Dict

from nanamilang.ast import AST
from nanamilang.token import Token
from nanamilang.datatypes import Base
from nanamilang.tokenizer import Tokenizer
from nanamilang.datatypes import NException
from nanamilang.shortcuts import (
    ASSERT_IS_CHILD_OF, ASSERT_COLLECTION_NOT_EMPTY
)


class Module:
    """
    NanamiLang Module

    from nanamilang import bdb
    from nanamilang import module
    from nanamilang import builtin

    # These steps are required to make builtins work

    bdb.BuiltinMacrosDB.initialize(builtin.BuiltinMacros)
    bdb.BuiltinFunctionsDB.initialize(builtin.BuiltinFunctions)

    source = str('(+ 2 2 (* 2 2))')
    m = module.Module('example', source=source)

    # or you can create empty module, then prepare a source code

    m: module.Module = module.Module('example')
    m.prepare(source)

    m.ast() # => will return an encapsulated AST instance
    m.tokenized() # => will return a collection of a Token instances
    # you can also look up for other getters using Python 3 dir() function

    results = m.evaluate().results() # will return an (<IntegerNumber>: 8)
    """

    class EnvironStorage:
        """NanamiLang Module Environ"""

        _storage: dict
        _m_ref: 'Module'
        _m_mapping: dict

        def __init__(self,
                     m_ref: 'Module') -> None:
            """Initialize a new Environ instance"""

            self._storage = {}
            self._m_ref = m_ref
            self._m_mapping = {m_ref.name(): m_ref}

        def storage(self) -> dict:
            """Module::Environ self._storage getter"""

            return self._storage

        def _from_qualified_name(self,
                                 g_name: str) -> tuple:
            """Module Environ get global unqualified name and module reference"""

            m_name, g_name = g_name.split('/') \
                if '/' in g_name and not g_name.startswith('/') \
                else (self._m_ref.name(), g_name)

            return g_name,  self._m_mapping.get(m_name)  # <- name and module ref

        def set(self, g_name: str, data_type: Base) -> None:
            """Module Environ set global by its qualified name"""

            unq_g_name, m_ref = self._from_qualified_name(g_name)
            if not m_ref:
                m_ref = self._m_ref
            if m_ref is not self._m_ref:
                return m_ref.environ().set(unq_g_name, data_type=data_type)
            retval = self._storage.update({unq_g_name: data_type})  # <--- do set
            m_ref.event('environment::set')([unq_g_name])  # <- trigger set event
            return retval  # <-------------- return result of a setting operation

        def get(self, g_name: str, default: Base = None) -> Base:
            """Module Environ get symbol by its qualified name"""

            unq_g_name, m_ref = self._from_qualified_name(g_name)
            if not m_ref:
                m_ref = self._m_ref
            if m_ref is not self._m_ref:
                return m_ref.environ().get(unq_g_name, default=default)
            retval = self._storage.get(unq_g_name, default)  # <---------- do get
            m_ref.event('environment::get')([unq_g_name])  # <- trigger get event
            return retval  # -------------<- return result of a getting operation

        def grab(self, m_ref: 'Module', refer_names: list) -> None:
            """Module::Environ take another module, then grab environ from it"""

            global_names = m_ref.environ().storage().keys()  # <--- global names

            refer_names = (global_names if refer_names and refer_names[0] == '*'
                           else refer_names)

            assert set(refer_names) <= set(global_names), (
                'Module::Environ::grab(): <refer-names> list contains extra name'
            )

            self._m_mapping.update({m_ref.name(): m_ref})
            for g_name, data_type in m_ref.environ().storage().items():
                if g_name in refer_names:  # <- if we're supposed to create alias
                    self.set(
                        f'{self._m_ref.name()}/{g_name}', data_type)  # <- create
                self.set(f'{m_ref.name()}/{g_name}', data_type)  # update environ

    class ModuleState:
        """NanamiLang Module :: ModuleState"""

        _meta: dict = None
        _state: str = None

        def __init__(self, state: str, meta: dict = None) -> None:
            """ModuleState, Initialize new Module State instance"""

            self._meta = meta
            self._state = state

        def meta(self) -> dict:
            """NanamiLang Module :: ModuleState, self._meta getter"""

            return self._meta

        def state(self) -> str:
            """NanamiLang Module :: ModuleState, self._state getter"""

            return self._state

        # Defines various module states which Module.prepare() method will return

        StateReady: str = 'StateReady'  # <- when module is ready to be evaluated
        StateIncomplete: str = 'StateIncompleteInput'  # <- when incomplete input

    _on: dict
    _ast: AST
    _name: str
    _state: ModuleState
    _source: str
    _tokenized: List[Token]
    _environ: EnvironStorage
    _evaluation_results = tuple
    _measurements: Dict[str, float] = None

    def __init__(self,
                 name, source: str = None) -> None:
        """
        Initialize a new NanamiLang Module instance

        :param name: the name of your NanamiLang Module
        :param source: your NanamiLang module source code
        """

        self._name = name
        self._measurements = {}
        self._evaluation_results = ()
        self._environ = self.EnvironStorage(self)
        self._on = {'environment::set': lambda args: None,
                    'environment::get': lambda args: None}

        if source:
            self._state = self.prepare(source)  # <- set module state

        # Source code is optional value, but if present, call prepare

    def name(self):
        """NanamiLang Module, self._name getter"""

        return self._name

    def state(self) -> ModuleState:
        """NanamiLang Module, self._state getter"""

        return self._state

    def environ(self) -> EnvironStorage:
        """NanamiLang Module, self._environ getter"""

        return self._environ  # <- to get/set global

    def broken(self) -> bool:
        """NanamiLang Module, returns true if has exceptions"""

        return bool(tuple(filter(
            lambda x: isinstance(x, NException), self.results()
        )))

    def prepare(self, source_code: str) -> ModuleState:
        """NanamiLang Module, prepare source code, return state"""

        ASSERT_IS_CHILD_OF(source_code,
                           str,
                           'Module: source code must be a string')
        ASSERT_COLLECTION_NOT_EMPTY(
            source_code, 'Module: source code could not be empty')

        self._source = source_code
        __tokenize_start__ = time.perf_counter()
        tokenizer = Tokenizer(source=self._source, m_name=self._name)
        tokenizer.tokenize()
        if tokenizer.incomplete():
            self._state = Module.ModuleState(
                Module.ModuleState.StateIncomplete,
                meta={'TBoundariesCnt': tokenizer.boundaries_count()}
            )
            return self._state  # <-- return the current module state
        self._tokenized = tokenizer.tokenized()
        __tokenize_delta__ = time.perf_counter() - __tokenize_start__
        __make_wood_start__ = time.perf_counter()
        self._ast = AST(self._tokenized, self.name())
        __make_wood_delta__ = time.perf_counter() - __make_wood_start__
        self._measurements = {
            '[Tree]': __make_wood_delta__, '[Parse]': __tokenize_delta__,
        }
        self._state = Module.ModuleState(Module.ModuleState.StateReady, {})
        return self._state  # <-- indicates that we are ready to evaluate()

    def ast(self) -> AST:
        """NanamiLang Module, self._ast getter"""

        return self._ast

    def event(self, event: str) -> callable:
        """NanamiLang Module, a self._on getter"""

        return self._on.get(event, lambda _: None)

    def on(self, event: str, cb) -> None:
        """Allows set a certain module event handler"""

        self._on[event] = cb  # <- store event callback

    def tokenized(self) -> List[Token]:
        """NanamiLang Module, self._tokenized getter"""

        return self._tokenized

    def measurements(self) -> Dict[str, float]:
        """NanamiLang Module, self._measurements getter"""

        return self._measurements

    def results(self) -> tuple:
        """NanamiLang Module, self.__evaluation_results getter"""

        return self._evaluation_results

    def evaluate(self) -> 'Module':
        """NanamiLang Module, call self._ast.evaluate() to evaluate your module"""

        __evaluate_start__ = time.perf_counter()
        self._evaluation_results = self._ast.evaluate(self._environ)
        __evaluate_delta__ = time.perf_counter() - __evaluate_start__
        self._measurements.update({'[Evaluation]': __evaluate_delta__})
        return self

        # Measure [Evaluation] time and store measurement in self._measurements dictionary
        # Store all evaluated results using self.ast().evaluate(), and return self pointer
