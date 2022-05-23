# coding=utf-8
from __future__ import absolute_import, print_function

import os

from suanpan import error, utils
from suanpan.log import logger
from suanpan.objects import HasName
from suanpan.utils import env, json

DEFAULT_MAX_VALUE_LENGTH = 120


class Arg(HasName):
    MAX_VALUE_LENGTH = DEFAULT_MAX_VALUE_LENGTH

    def __init__(self, key, **kwargs):
        self.key = key
        self.alias = kwargs.pop("alias", None)
        self.label = kwargs.pop("label", None)
        self.required = kwargs.pop("required", False)
        self.default = kwargs.pop("default", None)
        self.choices = kwargs.pop("choices", [])
        self.type = kwargs.pop("type", str)
        self.value = None

        self.kwargs = self.cleanParams(kwargs)
        for k, v in kwargs.items():
            setattr(self, k, v)

    @property
    def preprocess(self):
        return getattr(self, "_preprocess", None)

    @preprocess.setter
    def preprocess(self, func):
        self._preprocess = func

    @property
    def isSet(self):
        return self.required or self.default != self.value

    def _load(self, args):
        if self.key and self.key in args:
            return args.get(self.key)
        if self.alias and self.alias in args:
            return args.get(self.alias)
        return None

    def load(self, args):
        self.value = self._load(args)
        if self.value is None:
            self.value = env.get(self.envKeyFormat(self.key))
        if self.required and self.value is None and self.default is None:
            raise error.ArgumentRequiredError(f"{self.key} is required")
        return self

    def format(self):
        if self.value is None:
            self.value = self.default
        else:
            try:
                self.value = self.transform(self.value)
                if getattr(self, "preprocess", None):
                    self.value = self.preprocess(self.value)
            except Exception as e:
                raise error.ArgumentTypeError(
                    f"({self.name}) {self.key}: {utils.shorten(self.value, maxlen=self.MAX_VALUE_LENGTH)}"
                ) from e
        if self.choices and self.value not in self.choices.values():
            raise error.ArgumentTypeError(
                f"({self.name}) {self.key}: should be one of {self.choices.values()}"
            )
        self.logLoaded(self.value)
        return self

    def transform(self, value):
        return self.type(value)

    def clean(self):  # pylint: disable=unused-argument
        return self

    def save(self, result):  # pylint: disable=unused-argument
        self.logSaved(result.value)
        return result.value

    def cleanParams(self, params):
        return {k: v for k, v in params.items() if not k.startswith("_")}

    @property
    def keyString(self):
        return self.alias or self.key

    def logLoaded(self, value):
        logger.debug(
            f"({self.name}) {self.keyString} loaded: {utils.shorten(value, maxlen=self.MAX_VALUE_LENGTH)}"
        )

    def logSaved(self, value):
        logger.debug(
            f"({self.name}) {self.keyString} saved: {utils.shorten(value, maxlen=self.MAX_VALUE_LENGTH)}"
        )

    def fixGlobalKey(self, key):
        return key.replace("-", "_")

    def envKeyFormat(self, key):
        return f"SP_{self.fixGlobalKey(key).upper()}"

    def getOutputTmpValue(self, *args):
        pass

    def getOutputTmpArg(self, *args):
        value = self.getOutputTmpValue(  # pylint: disable=assignment-from-no-return
            *args
        )
        return (f"--{self.key}", value) if value is not None else tuple()

    @property
    def paramType(self):
        return "select" if self.choices else "string"

    @property
    def paramName(self):
        return self.alias or self.key

    @property
    def paramLabel(self):
        return {"zh_CN": self.label or self.paramName}

    @property
    def paramOptionalKeys(self):
        return ["default", "required"]

    @property
    def paramConfigs(self):
        return {
            "type": self.paramType,
            "name": self.paramName,
            "label": self.paramLabel,
            "options": self.choices,
            **{
                key: getattr(self, key, None)
                for key in self.paramOptionalKeys
                if getattr(self, key, None) is not None
            },
        }


class String(Arg):
    pass


class Int(Arg):
    def __init__(self, *args, **kwargs):
        kwargs.setdefault("step", 1)
        super().__init__(*args, **kwargs)

    @classmethod
    def transform(cls, value):
        return int(value)

    @property
    def paramType(self):
        return "select" if self.choices else "number"

    @property
    def paramOptionalKeys(self):
        return [*super().paramOptionalKeys, "min", "max", "step"]


class Float(Int):
    def __init__(self, *args, **kwargs):
        kwargs.setdefault("step", 0.1)
        super().__init__(*args, **kwargs)

    @classmethod
    def transform(cls, value):
        return float(value)


class Bool(Arg):
    def __init__(self, key, **kwargs):
        kwargs.setdefault("default", False)
        super().__init__(key, **kwargs)

    @classmethod
    def transform(cls, value):
        if value.lower() in ("yes", "true", "t", "y"):
            return True
        if value.lower() in ("no", "false", "f", "n"):
            return False
        raise error.ArgumentError(cls.__name__)

    @property
    def paramType(self):
        return "switch"

    @property
    def paramConfigs(self):
        return {
            **super().paramConfigs,
            "options": {"true": True, "false": False},
        }


class List(Arg):
    def transform(self, value):
        return [i.strip() for i in value.split(",") if i.strip()]


class ListOfString(List):
    pass


class ListOfInt(List):
    def transform(self, value):
        items = super().transform(value)
        return [Int.transform(i) for i in items]


class ListOfFloat(List):
    def transform(self, value):
        items = super().transform(value)
        return [Float.transform(i) for i in items]


class ListOfBool(List):
    def transform(self, value):
        items = super().transform(value)
        return [Bool.transform(i) for i in items]


class Json(String):
    def transform(self, value):
        if value is not None:
            value = json.loads(value)
        return value

    def save(self, result):
        super().save(result)
        return json.dumps(result.value)

    @property
    def paramType(self):
        return "code"

    @property
    def paramConfigs(self):
        return {
            **super().paramConfigs,
            "mode": "javascript",
        }


class IntOrFloat(Arg):
    @classmethod
    def transform(cls, value):
        return Float.transform(value) if "." in value else Int.transform(value)


class IntFloatOrString(Arg):
    def transform(self, value):
        try:
            Float.transform(value)
            return IntOrFloat.transform(value)
        except ValueError:
            return value
        except TypeError:
            return value


class BoolOrString(Arg):
    def transform(self, value):
        return value if value == "auto" else Bool.transform(value)


class BoolOrInt(Arg):
    def transform(self, value):
        try:
            return Bool.transform(value)
        except error.ArgumentError:
            return Int.transform(value)


class StringOrListOfFloat(ListOfFloat):
    def transform(self, value):
        if "," in value:
            return super().transform(value)
        return value
