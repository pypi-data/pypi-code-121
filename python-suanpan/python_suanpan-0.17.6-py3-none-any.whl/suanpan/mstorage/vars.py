# coding=utf-8
from __future__ import absolute_import, print_function

from suanpan import error
from suanpan.utils import json


class Variable(object):
    def __init__(self, vars, mstorage, key):
        self.vars = vars
        self.mstorage = mstorage
        self.key = key
        self._value = None

    @property
    def value(self):
        if self._value is None:
            self._value = self.get()
        return self._value

    def get(self, default=None):
        value = self.mstorage.get(self.key)
        value = default if value is None else self.decode(value)
        self._value = value
        return self._value

    def set(self, value, expire=None):
        self._value = value
        self.mstorage.set(
            self.key, self.encode(self._value), expire=expire or self.vars.VARS_EXPIRE
        )

    def delete(self):
        self.mstorage.delete(self.key)

    @classmethod
    def encode(cls, value):
        return value

    @classmethod
    def decode(cls, value):
        return value


class String(Variable):
    pass


class Int(Variable):
    @classmethod
    def encode(cls, value):
        return str(value)

    @classmethod
    def decode(cls, value):
        return int(value)


class Float(Variable):
    @classmethod
    def encode(cls, value):
        return str(value)

    @classmethod
    def decode(cls, value):
        return float(value)


class Json(Variable):
    @classmethod
    def encode(cls, value):
        return json.dumps(value)

    @classmethod
    def decode(cls, value):
        return json.loads(value)


class Variables(object):
    VARS_EXPIRE = None
    VARS_REGISTER_KEY = "global.vars"
    DEFAULT_VAR_TYPE = "string"
    VARS = {
        "string": String,
        "int": Int,
        "float": Float,
        "json": Json,
    }

    def __init__(self, mstorage):
        self.mstorage = mstorage

    def _getVar(self, key, type=DEFAULT_VAR_TYPE):
        var = self.VARS.get(type)
        if not var:
            raise error.MStorageUnknownVarTypeError(type)
        return var(self, self.mstorage, key)

    def _getFullKey(self, key):
        return key

    def _getOriginKey(self, fullKey):
        return fullKey

    def _getRelativeKey(self, key, prefix=None, delimiter="."):
        if not prefix or not key.startswith(prefix):
            return key
        return key[len(prefix) :].lstrip(delimiter)

    def _getRegisterKey(self):
        return self.VARS_REGISTER_KEY

    def _register(self, key, type):
        return self.mstorage.mset(
            self._getRegisterKey(), {key: type}, expire=self.VARS_EXPIRE
        )

    def _getAllRegistered(self):
        return self.mstorage.mget(self._getRegisterKey())

    def _getRegisteredType(self, key):
        return self._getAllRegistered().get(key)

    def _getAllVars(self):
        return [
            self.var(key, type=type) for key, type in self._getAllRegistered().items()
        ]

    def _getVars(self, prefix=None):
        return [
            var
            for var in self._getAllVars()
            if not prefix or var.key.startswith(prefix)
        ]

    def var(self, key, type=None):
        _type = self._getRegisteredType(key)
        if _type is not None and type is not None and _type != type:
            raise error.MStorageVarHasRegisteredAsAnotherTypeError(
                f"{key}({type}) is not {_type}"
            )
        type = type or _type or self.DEFAULT_VAR_TYPE
        var = self._getVar(self._getFullKey(key), type=type)
        self._register(key, type)
        return var

    def vars(self, prefix=None):
        return self._getVars(prefix=prefix)

    def get(self, key):
        type = self._getRegisteredType(key)
        if not type:
            raise error.MStorageUnregisterVarKeyError(key)
        return self.var(key, type=type).get()

    def getall(self, prefix=None):
        return {
            self._getRelativeKey(self._getOriginKey(arg.key), prefix=prefix): arg.get()
            for arg in self._getVars(prefix=prefix)
        }

    def Int(self, key):
        return self.var(key, type="int")

    def Float(self, key):
        return self.var(key, type="float")

    def String(self, key):
        return self.var(key, type="string")

    def Json(self, key):
        return self.var(key, type="json")
