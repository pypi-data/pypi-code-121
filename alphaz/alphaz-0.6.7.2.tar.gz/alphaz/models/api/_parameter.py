import json, datetime, dataclasses, re
import typing

from sqlalchemy.orm.base import object_mapper
from sqlalchemy.orm.exc import UnmappedInstanceError
from sqlalchemy.ext.declarative import DeclarativeMeta

from collections.abc import Callable

from ..main import AlphaException

from ...libs import date_lib, json_lib, py_lib

from enum import Enum


def set_value_like_mode(value, mode):
    value = str(value).replace("*", "%")

    if not value.startswith("%") and mode in [
        ParameterMode.IN_LIKE,
        ParameterMode.START_LIKE,
    ]:
        value = f"%{value}"

    if not value.endswith("%") and mode in [
        ParameterMode.IN_LIKE,
        ParameterMode.END_LIKE,
    ]:
        value = f"{value}%"
    return value


class ParameterMode(Enum):
    NONE = 0
    LIKE = 1
    IN_LIKE = 2
    START_LIKE = 3
    END_LIKE = 4

    def __str__(self):
        return str(self.value)

    def to_json(self):
        return str(self.value)


class Parameter:
    _value = None
    no_log: bool = False

    def __init__(
        self,
        name: str,
        default=None,
        empty_value=None,
        none_value=None,
        options=None,
        cacheable: bool = True,
        required: bool = False,
        ptype: type = str,
        private: bool = False,
        mode: ParameterMode = ParameterMode.NONE,
        override: bool = False,
        function: Callable = None,
        automap:bool=False,
        max_size:int=None,
        min_size:int=None
    ):
        """[summary]

        Args:
            name (str): [description]
            default ([type], optional): [description]. Defaults to None.
            options ([type], optional): [description]. Defaults to None.
            cacheable (bool, optional): [description]. Defaults to True.
            required (bool, optional): [description]. Defaults to False.
            ptype (type, optional): [description]. Defaults to str.
            private (bool, optional): [description]. Defaults to False.
            mode (str, optional): [description]. Defaults to "none".
        """
        self.name = name
        self.default = default
        self.cacheable = cacheable
        self.empty_value = empty_value
        self.none_value = none_value
        self.options = options
        self.required = required
        self.ptype: type = ptype
        self.function: Callable = function
        self.type = str(ptype).replace("<class '", "").replace("'>", "")
        self.private = private
        self.mode = mode
        self.override = override
        self.is_value = False
        self.automap = automap
        self.max_size = max_size
        self.min_size = min_size

    @property
    def value(self):
        return self._value if self._value is not None else self.default

    def __check_options(self, value):
        if (
            self.options is not None
            and value not in self.options
            and not (not self.required and value is None)
        ):
            raise AlphaException(
                "api_wrong_parameter_option",
                parameters={
                    "value": value,
                    "parameter": self.name,
                    "options": str(self.options),
                },
            )

    def set_value(self, method: str, dataDict, json, form, args):
        """Set parameter value

        Raises:
            AlphaException: [description]
        """
        # dataDict: for list GET
        self._value = self.default

        if form is not None and self.name in form:
            self._value = form[self.name]
            self.is_value = True
        elif json is not None and self.name in json:
            self._value = json[self.name]
            self.is_value = True
        elif self.name in args:
            self._value = args.get(self.name)
            self.is_value = True

        # check size
        if self.max_size is not None and self._value is not None and len(self._value) > self.max_size:
             raise AlphaException(
                "api_parameter_length_too_long",
                parameters={
                    "parameter": self.name,
                    "size": len(self.value),
                    "value": self._value,
                    "max": self.max_size
                },
            )
        if self.min_size is not None and self._value is not None and len(self._value) < self.min_size:
             raise AlphaException(
                "api_parameter_length_too_long",
                parameters={
                    "parameter": self.name,
                    "size": len(self.value),
                    "value": self._value,
                    "min": self.min_size
                },
            )

        # List
        if self.ptype == list or py_lib.is_subtype(self.ptype, typing.List):
            if self._value is None or str(self._value).strip() == "":
                self._value = self.default
            elif (
                not ";" in self._value
                and not "," in self._value
                and self._value == [""]
            ):
                self._value = []
            elif not ";" in self._value and not "," in self._value:
                self._value = (
                    dataDict[self.name] if self.name in dataDict else self.default
                )
            
            sub_type = py_lib.get_subtype(self.ptype)
            if dataclasses.is_dataclass(sub_type):
                values = re.findall(r'{[^{]*}',self._value)
                self._value = [sub_type.map_from_json(x,automap=self.automap) for x in values]

        if self._value is None and form is not None and self.name in form:
            self._value = form[self.name]
        if self._value is None and form is not None and self.name in form:
            self._value = form[self.name]

        if isinstance(self.ptype, DeclarativeMeta):
            if self._value is None:
                parameters = {x: y for x, y in form.items() if hasattr(self.ptype, x)}
            else:
                parameters = json_lib.load_json(self._value)
                parameters = {
                    x: y for x, y in parameters.items() if hasattr(self.ptype, x)
                }  # TODO: enhance
            self._value = self.ptype(**parameters)
        elif dataclasses.is_dataclass(self.ptype):
            self._value = self.ptype.map_from_json(self._value,automap=self.automap)

        if self.ptype == dict:
            self._value = json_lib.load_json(self._value)

        if self.required and self._value is None:
            raise AlphaException(
                "api_missing_parameter", parameters={"parameter": self.name}
            )

        if self._value is None:
            self.__check_options(self._value)
            return

        if str(self._value).lower() in ["null", "none", "undefined"]:
            self._value = self.none_value if self.is_value else None
        if self.empty_value is not None and str(self._value).lower() == "":
            self._value = self.empty_value

        if self.ptype == str and (
            self.mode
            in [
                ParameterMode.LIKE,
                ParameterMode.IN_LIKE,
                ParameterMode.START_LIKE,
                ParameterMode.END_LIKE,
            ]
        ):
            self._value = set_value_like_mode(self._value, self.mode)

        if self.ptype == bool:
            str_value = str(self._value).lower()
            self.__check_options(str(self._value))

            if str_value in ["y", "true", "t", "1"]:
                value = True
            elif str_value in ["n", "false", "f", "0"]:
                value = False
            else:
                raise AlphaException(
                    "api_wrong_parameter_value",
                    parameters={
                        "parameter": self.name,
                        "type": "bool",
                        "value": self._value,
                    },
                )
            self._value = value

        if self.ptype == list or py_lib.is_subtype(self.ptype, typing.List):
            if type(self._value) == str and str(self._value).strip() == "":
                self._value = []
            elif type(self._value) == str:
                try:
                    if ";" in str(self._value) or "," in str(self._value):
                        self._value = (
                            str(self._value).split(";")
                            if ";" in str(self._value)
                            else str(self._value).split(",")
                        )
                    else:
                        self._value = [self._value]
                except:
                    raise AlphaException(
                        "api_wrong_parameter_value",
                        parameters={
                            "parameter": self.name,
                            "type": "list",
                            "value": self._value,
                        },
                    )

            if py_lib.is_subtype(self.ptype, typing.List[int]):
                self._value = [int(x) for x in self._value]
            if py_lib.is_subtype(self.ptype, typing.List[float]):
                self._value = [float(x) for x in self._value]

            for val in self._value:
                self.__check_options(val)

            if self.mode in [
                ParameterMode.LIKE,
                ParameterMode.IN_LIKE,
                ParameterMode.START_LIKE,
                ParameterMode.END_LIKE,
            ]:
                self._value = [set_value_like_mode(x, self.mode) for x in self._value]

        if self.ptype == int:
            try:
                self._value = int(self._value)
            except:
                raise AlphaException(
                    "api_wrong_parameter_value",
                    parameters={
                        "parameter": self.name,
                        "type": "int",
                        "value": self._value,
                    },
                )
            self.__check_options(self._value)

        if self.ptype == float:
            try:
                self._value = float(self._value)
            except:
                raise AlphaException(
                    "api_wrong_parameter_value",
                    parameters={
                        "parameter": self.name,
                        "type": "float",
                        "value": self._value,
                    },
                )
            self.__check_options(self._value)

        if self.ptype == datetime.datetime:
            self.__check_options(self._value)
            self._value = date_lib.str_to_datetime(self._value)

        if hasattr(self.ptype, "metadata") and not hasattr(self._value, "metadata"):
            r = json.loads(self._value)
            self._value = self.ptype(**r)

        if self.ptype == str:
            self.__check_options(str(self._value))

        if self.function is not None:
            self._value = self.function(self._value)
