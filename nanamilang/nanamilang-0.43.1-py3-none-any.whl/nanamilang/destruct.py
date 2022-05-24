"""NanamiLang Collection Destructuring"""

# This file is a part of NanamiLang Project
# This project licensed under GNU GPL version 2
# Initially made by @jedi2light (aka Stoian Minaiev)

from typing import List
from nanamilang.token import Token
from nanamilang.datatypes import Nil
from nanamilang.datatypes import Base
from nanamilang.datatypes import String
from nanamilang.datatypes import Keyword
from nanamilang.datatypes import Collection
from nanamilang.datatypes import IntegerNumber
from nanamilang.datatypes import Vector, HashMap
from nanamilang.datatypes import Py3Object, Py3Inst
from nanamilang.shortcuts import (
    NML_M_ITERATE_AS_PAIRS,
    NML_M_FORM_IS_A_VECTOR, NML_M_FORM_IS_A_HASHMAP
)


class Destructuring:
    """Vector, HashMap, Interop destructuring"""

    _nil: Nil = Nil('nil')
    _target_token_or_form: List[Token] or Token

    def __init__(self, target_token_or_form: (list
                                              or Token)):
        """Initialize a new Destructuring instance"""

        self._target_token_or_form = target_token_or_form

    def destruct(self,
                 any_valid_data_type: (Base
                                       or Py3Inst
                                       or Py3Object
                                       or Collection)) -> dict:
        """Try to destruct, return environment or raise AssertionError"""

        if isinstance(self._target_token_or_form, Token):
            any_valid_data_type: Base
            return self._single_token_destructure(any_valid_data_type)
        if isinstance(self._target_token_or_form, list):
            any_valid_data_type: Collection or Py3Inst or Py3Object
            return self._collection_form_destructure(any_valid_data_type)
        return {}  # <------------ unreachable, just to make Pylint happy

    def _vector_form_destructure(self, vector: Vector) -> dict:
        """When the left form is a Vector and the right is a Vector type"""

        environ = {}

        for idx, idn in enumerate(
                NML_M_ITERATE_AS_PAIRS(self._target_token_or_form)):
            idn: Token
            assert isinstance(idn, Token), (
                'destructuring: each element needs to be a Token'
            )
            assert idn.type() == Token.Identifier, (
                'destructuring: each element needs to be an Identifier'
            )
            element_index = IntegerNumber(idx)  # <- cast it to IntegerNumber
            environ[idn.dt().origin()] = vector.get(element_index, self._nil)

        return environ

    def _hashmap_hashmap_form_destructure(self, hashmap: HashMap) -> dict:
        """When the left form is a HashMap and the right is a HashMap type"""

        hashmap_form = tuple(
            self._target_token_or_form[1:])
        assert len(hashmap_form) == 2, (
            'destructuring: wrong HashMap form arity'
        )
        kind: Token
        vector_form: List[Token]
        kind, vector_form = hashmap_form
        assert isinstance(kind, Token), (
            'destructuring: kind needs to be a Token'
        )
        assert kind.type() == Token.Keyword, (
            'destructuring: kind needs to be a Keyword'
        )
        assert NML_M_FORM_IS_A_VECTOR(vector_form), (
            'destructuring: Vector form needs to be a Vector'
        )
        identifiers = []
        for idn in NML_M_ITERATE_AS_PAIRS(vector_form):
            idn: Token
            assert isinstance(idn, Token), (
                'destructuring: each element needs to be a Token'
            )
            assert idn.type() == Token.Identifier, (
                'destructuring: each element needs to be an Identifier'
            )
            identifiers.append(idn.dt().origin())
        assert kind.dt().reference() in ['strs', 'keys'], (
            'destructuring: an unknown HashMap destructuring operation'
        )
        if kind.dt().reference() == 'strs':
            return self._strs_destruct(identifiers, hashmap)  # <------- strs
        if kind.dt().reference() == 'keys':
            return self._keys_destruct(identifiers, hashmap)  # <------- keys
        return {}  # <---------------- unreachable, just to make Pylint happy

    def _hashmap_interop_form_destructure(self, interop: (Py3Object or
                                                          Py3Inst)) -> dict:
        """When the left form is a HashMap and the right is an Interop type"""

        hashmap_form = tuple(
            self._target_token_or_form[1:])
        assert len(hashmap_form) == 2, (
            'destructuring: wrong HashMap form arity'
        )
        kind: Token
        vector_form: List[Token]
        kind, vector_form = hashmap_form
        assert isinstance(kind, Token), (
            'destructuring: kind needs to be a Token'
        )
        assert kind.type() == Token.Keyword, (
            'destructuring: kind needs to be a Keyword'
        )
        assert NML_M_FORM_IS_A_VECTOR(vector_form), (
            'destructuring: Vector form needs to be a Vector'
        )
        identifiers = []
        for idn in NML_M_ITERATE_AS_PAIRS(vector_form):
            idn: Token
            assert isinstance(idn, Token), (
                'destructuring: each element needs to be a Token'
            )
            assert idn.type() == Token.Identifier, (
                'destructuring: each element needs to be an Identifier'
            )
            identifiers.append(idn.dt().origin())
        assert kind.dt().reference() == 'keys', (
            'destructuring: an unknown interop destructuring operation'
        )
        return self._keys_destruct(identifiers, interop)  # <------- keys only

    def _single_token_destructure(self, any_valid_data_type: Base) -> dict:
        """When the left form is a token and the right is an any valid type"""

        self._target_token_or_form: Token
        assert self._target_token_or_form.type() == Token.Identifier, (
            'destructuring: the left-side needs to be an Identifier'
        )
        return {self._target_token_or_form.dt().origin(): any_valid_data_type}

    def _collection_form_destructure(self,
                                     valid_data_type: (Base or
                                                       Collection or
                                                       Py3Inst or
                                                       Py3Object)) -> dict:
        """When the left form is a collection and the right is a valid type"""

        if NML_M_FORM_IS_A_VECTOR(self._target_token_or_form):
            if isinstance(valid_data_type, Vector):
                valid_data_type: Vector
                return self._vector_form_destructure(valid_data_type)
            mock: Vector = Vector(tuple())
            return self._vector_form_destructure(mock)  # <---------- get nils
        if NML_M_FORM_IS_A_HASHMAP(self._target_token_or_form):
            if isinstance(valid_data_type, HashMap):
                valid_data_type: HashMap
                return self._hashmap_hashmap_form_destructure(valid_data_type)
            if isinstance(valid_data_type, (Py3Object, Py3Inst)):
                valid_data_type: Py3Object or Py3Inst
                return self._hashmap_interop_form_destructure(valid_data_type)
            mock: HashMap = HashMap(tuple())
            return self._hashmap_hashmap_form_destructure(mock)  # <- get nils

        raise AssertionError('destructuring: incorrect/unsupported left-side')

    def _strs_destruct(self, lst: list,
                       hashmap: HashMap) -> dict:
        """When we need to extract strs from a given HashMap"""

        return {s: hashmap.get(String(s), self._nil) for s in lst}

    def _keys_destruct(self, lst: list,
                       hashmap_or_interop: (HashMap or
                                            Py3Inst or Py3Object)) -> dict:
        """When we need to extract keys from a given HashMap or an Interop"""

        return {k: hashmap_or_interop.get(Keyword(k), self._nil) for k in lst}
