"""Generated implementation of summary_statistics."""

# WARNING DO NOT EDIT
# This code was generated from summary-statistics.mcn

from __future__ import annotations

import abc  # noqa: F401
import dataclasses  # noqa: F401
import datetime  # noqa: F401
import enum  # noqa: F401
import isodate  # noqa: F401
import json  # noqa: F401
import jsonschema  # noqa: F401
import logging  # noqa: F401
import typing  # noqa: F401
import uuid  # noqa: F401
try:
    from anaml_client.utils.serialisation import JsonObject  # noqa: F401
except ImportError:
    pass


@dataclasses.dataclass(frozen=True)
class SummaryStatistics(abc.ABC):
    """Summary statistics for a feature.
    
    Args:
        countNulls (typing.Optional[int]): A data field.
        dataType (typing.Optional[str]): A data field.
        featureName (str): A data field.
    """
    
    ADT_TYPE: typing.ClassVar[str] = ""
    adt_type: str = dataclasses.field(init=False, repr=False, default=ADT_TYPE)
    
    countNulls: typing.Optional[int]
    dataType: typing.Optional[str]
    featureName: str
    
    @classmethod
    def json_schema(cls) -> SummaryStatistics:
        """JSON schema for variant SummaryStatistics.
        
        Returns:
            A Python dictionary describing the JSON schema.
        """
        adt_types = [klass.ADT_TYPE for klass in cls.__subclasses__()]
        return {
            "type": "object",
            "properties": {
                "adt_type": {
                    "type": "string",
                    "enum": adt_types
                }
            },
            "required": [
                "adt_type",
            ]
        }
    
    @classmethod
    def from_json(cls, data: dict) -> SummaryStatistics:
        """Validate and parse JSON data into an instance of SummaryStatistics.
        
        Args:
            data (dict): JSON data to validate and parse.
        
        Returns:
            An instance of SummaryStatistics.
        
        Raises:
            ValidationError: When schema validation fails.
            KeyError: When a required field is missing from the JSON.
        """
        try:
            jsonschema.validate(data, cls.json_schema())
            adt_type = data.get("adt_type", None)
            for klass in cls.__subclasses__():
                if klass.ADT_TYPE == adt_type:
                    return klass.from_json(data)
            raise ValueError("Unknown adt_type: '{ty}'".format(ty=adt_type))
        except jsonschema.exceptions.ValidationError as ex:
            logging.debug("Invalid JSON data received while parsing SummaryStatistics", exc_info=ex)
            raise
    
    @abc.abstractmethod
    def to_json(self) -> dict:
        """Serialise this instance as JSON.
        
        Returns:
            Data ready to serialise as JSON.
        """
        raise NotImplementedError


@dataclasses.dataclass(frozen=True)
class NumericalSummaryStatistics(SummaryStatistics):
    """Summary statistics for a numerical feature.
    
    Args:
        featureName (str): A data field.
        dataType (typing.Optional[str]): A data field.
        count (int): A data field.
        countNulls (typing.Optional[int]): A data field.
        min (typing.Optional[float]): A data field.
        max (typing.Optional[float]): A data field.
        mean (typing.Optional[float]): A data field.
        stdDev (typing.Optional[float]): A data field.
        quantiles (typing.List[float]): A data field.
        densities (typing.List[Density]): A data field.
        histogram (typing.Optional[typing.List[IntegralFrequency]]): A data field.
    """
    
    ADT_TYPE: typing.ClassVar[str] = "numerical"
    adt_type: str = dataclasses.field(init=False, repr=False, default=ADT_TYPE)
    
    featureName: str
    dataType: typing.Optional[str]
    count: int
    countNulls: typing.Optional[int]
    min: typing.Optional[float]
    max: typing.Optional[float]
    mean: typing.Optional[float]
    stdDev: typing.Optional[float]
    quantiles: typing.List[float]
    densities: typing.List[Density]
    histogram: typing.Optional[typing.List[IntegralFrequency]]
    
    @classmethod
    def json_schema(cls) -> dict:
        """Return the JSON schema for NumericalSummaryStatistics data.
        
        Returns:
            A Python dictionary describing the JSON schema.
        """
        return {
            "type": "object",
            "properties": {
                "adt_type": {
                    "type": "string",
                    "enum": [cls.ADT_TYPE]
                },
                "featureName": {
                    "type": "string"
                },
                "dataType": {
                    "oneOf": [
                        {"type": "null"},
                        {"type": "string"},
                    ]
                },
                "count": {
                    "type": "integer"
                },
                "countNulls": {
                    "oneOf": [
                        {"type": "null"},
                        {"type": "integer"},
                    ]
                },
                "min": {
                    "oneOf": [
                        {"type": "null"},
                        {"type": "number"},
                    ]
                },
                "max": {
                    "oneOf": [
                        {"type": "null"},
                        {"type": "number"},
                    ]
                },
                "mean": {
                    "oneOf": [
                        {"type": "null"},
                        {"type": "number"},
                    ]
                },
                "stdDev": {
                    "oneOf": [
                        {"type": "null"},
                        {"type": "number"},
                    ]
                },
                "quantiles": {
                    "type": "array",
                    "item": {"type": "number"}
                },
                "densities": {
                    "type": "array",
                    "item": Density.json_schema()
                },
                "histogram": {
                    "oneOf": [
                        {"type": "null"},
                        {"type": "array", "item": IntegralFrequency.json_schema()},
                    ]
                }
            },
            "required": [
                "adt_type",
                "featureName",
                "count",
                "quantiles",
                "densities",
            ]
        }
    
    @classmethod
    def from_json(cls, data: dict) -> NumericalSummaryStatistics:
        """Validate and parse JSON data into an instance of NumericalSummaryStatistics.
        
        Args:
            data (dict): JSON data to validate and parse.
        
        Returns:
            An instance of NumericalSummaryStatistics.
        
        Raises:
            ValidationError: When schema validation fails.
            KeyError: When a required field is missing from the JSON.
        """
        try:
            jsonschema.validate(data, cls.json_schema())
            return NumericalSummaryStatistics(
                featureName=str(data["featureName"]),
                dataType=(lambda v: v and str(v))(data.get("dataType", None)),
                count=int(data["count"]),
                countNulls=(lambda v: v and int(v))(data.get("countNulls", None)),
                min=(lambda v: v and float(v))(data.get("min", None)),
                max=(lambda v: v and float(v))(data.get("max", None)),
                mean=(lambda v: v and float(v))(data.get("mean", None)),
                stdDev=(lambda v: v and float(v))(data.get("stdDev", None)),
                quantiles=[float(v) for v in data["quantiles"]],
                densities=[Density.from_json(v) for v in data["densities"]],
                histogram=(
                    lambda v: v and [IntegralFrequency.from_json(v) for v in v]
                )(
                    data.get("histogram", None)
                ),
            )
        except jsonschema.exceptions.ValidationError as ex:
            logging.debug(
                "Invalid JSON data received while parsing NumericalSummaryStatistics",
                exc_info=ex
            )
            raise
    
    def to_json(self) -> dict:
        """Serialise this instance as JSON.
        
        Returns:
            Data ready to serialise as JSON.
        """
        return {
            "adt_type": self.ADT_TYPE,
            "featureName": str(self.featureName),
            "dataType": (lambda v: v and str(v))(self.dataType),
            "count": self.count,
            "countNulls": (lambda v: v and v)(self.countNulls),
            "min": (lambda v: v and v)(self.min),
            "max": (lambda v: v and v)(self.max),
            "mean": (lambda v: v and v)(self.mean),
            "stdDev": (lambda v: v and v)(self.stdDev),
            "quantiles": [v for v in self.quantiles],
            "densities": [v.to_json() for v in self.densities],
            "histogram": (lambda v: v and [v.to_json() for v in v])(self.histogram)
        }


@dataclasses.dataclass(frozen=True)
class DateSummaryStatistics(SummaryStatistics):
    """Summary statistics for a date feature.
    
    Args:
        featureName (str): A data field.
        dataType (typing.Optional[str]): A data field.
        count (int): A data field.
        countNulls (typing.Optional[int]): A data field.
        min (typing.Optional[datetime.date]): A data field.
        max (typing.Optional[datetime.date]): A data field.
        quantiles (typing.List[datetime.date]): A data field.
    """
    
    ADT_TYPE: typing.ClassVar[str] = "date"
    adt_type: str = dataclasses.field(init=False, repr=False, default=ADT_TYPE)
    
    featureName: str
    dataType: typing.Optional[str]
    count: int
    countNulls: typing.Optional[int]
    min: typing.Optional[datetime.date]
    max: typing.Optional[datetime.date]
    quantiles: typing.List[datetime.date]
    
    @classmethod
    def json_schema(cls) -> dict:
        """Return the JSON schema for DateSummaryStatistics data.
        
        Returns:
            A Python dictionary describing the JSON schema.
        """
        return {
            "type": "object",
            "properties": {
                "adt_type": {
                    "type": "string",
                    "enum": [cls.ADT_TYPE]
                },
                "featureName": {
                    "type": "string"
                },
                "dataType": {
                    "oneOf": [
                        {"type": "null"},
                        {"type": "string"},
                    ]
                },
                "count": {
                    "type": "integer"
                },
                "countNulls": {
                    "oneOf": [
                        {"type": "null"},
                        {"type": "integer"},
                    ]
                },
                "min": {
                    "oneOf": [
                        {"type": "null"},
                        {"type": "string", "format": "date"},
                    ]
                },
                "max": {
                    "oneOf": [
                        {"type": "null"},
                        {"type": "string", "format": "date"},
                    ]
                },
                "quantiles": {
                    "type": "array",
                    "item": {"type": "string", "format": "date"}
                }
            },
            "required": [
                "adt_type",
                "featureName",
                "count",
                "quantiles",
            ]
        }
    
    @classmethod
    def from_json(cls, data: dict) -> DateSummaryStatistics:
        """Validate and parse JSON data into an instance of DateSummaryStatistics.
        
        Args:
            data (dict): JSON data to validate and parse.
        
        Returns:
            An instance of DateSummaryStatistics.
        
        Raises:
            ValidationError: When schema validation fails.
            KeyError: When a required field is missing from the JSON.
        """
        try:
            jsonschema.validate(data, cls.json_schema())
            return DateSummaryStatistics(
                featureName=str(data["featureName"]),
                dataType=(lambda v: v and str(v))(data.get("dataType", None)),
                count=int(data["count"]),
                countNulls=(lambda v: v and int(v))(data.get("countNulls", None)),
                min=(lambda v: v and datetime.date.fromisoformat(v))(data.get("min", None)),
                max=(lambda v: v and datetime.date.fromisoformat(v))(data.get("max", None)),
                quantiles=[datetime.date.fromisoformat(v) for v in data["quantiles"]],
            )
        except jsonschema.exceptions.ValidationError as ex:
            logging.debug(
                "Invalid JSON data received while parsing DateSummaryStatistics",
                exc_info=ex
            )
            raise
    
    def to_json(self) -> dict:
        """Serialise this instance as JSON.
        
        Returns:
            Data ready to serialise as JSON.
        """
        return {
            "adt_type": self.ADT_TYPE,
            "featureName": str(self.featureName),
            "dataType": (lambda v: v and str(v))(self.dataType),
            "count": self.count,
            "countNulls": (lambda v: v and v)(self.countNulls),
            "min": (lambda v: v and v.isoformat())(self.min),
            "max": (lambda v: v and v.isoformat())(self.max),
            "quantiles": [v.isoformat() for v in self.quantiles]
        }


@dataclasses.dataclass(frozen=True)
class CategoricalSummaryStatistics(SummaryStatistics):
    """Summary statistics for a categorical feature.
    
    Args:
        featureName (str): A data field.
        dataType (typing.Optional[str]): A data field.
        count (int): A data field.
        countNulls (typing.Optional[int]): A data field.
        categoryFrequencies (typing.Optional[typing.List[CategoryFrequency]]): A data field.
    """
    
    ADT_TYPE: typing.ClassVar[str] = "categorical"
    adt_type: str = dataclasses.field(init=False, repr=False, default=ADT_TYPE)
    
    featureName: str
    dataType: typing.Optional[str]
    count: int
    countNulls: typing.Optional[int]
    categoryFrequencies: typing.Optional[typing.List[CategoryFrequency]]
    
    @classmethod
    def json_schema(cls) -> dict:
        """Return the JSON schema for CategoricalSummaryStatistics data.
        
        Returns:
            A Python dictionary describing the JSON schema.
        """
        return {
            "type": "object",
            "properties": {
                "adt_type": {
                    "type": "string",
                    "enum": [cls.ADT_TYPE]
                },
                "featureName": {
                    "type": "string"
                },
                "dataType": {
                    "oneOf": [
                        {"type": "null"},
                        {"type": "string"},
                    ]
                },
                "count": {
                    "type": "integer"
                },
                "countNulls": {
                    "oneOf": [
                        {"type": "null"},
                        {"type": "integer"},
                    ]
                },
                "categoryFrequencies": {
                    "oneOf": [
                        {"type": "null"},
                        {"type": "array", "item": CategoryFrequency.json_schema()},
                    ]
                }
            },
            "required": [
                "adt_type",
                "featureName",
                "count",
            ]
        }
    
    @classmethod
    def from_json(cls, data: dict) -> CategoricalSummaryStatistics:
        """Validate and parse JSON data into an instance of CategoricalSummaryStatistics.
        
        Args:
            data (dict): JSON data to validate and parse.
        
        Returns:
            An instance of CategoricalSummaryStatistics.
        
        Raises:
            ValidationError: When schema validation fails.
            KeyError: When a required field is missing from the JSON.
        """
        try:
            jsonschema.validate(data, cls.json_schema())
            return CategoricalSummaryStatistics(
                featureName=str(data["featureName"]),
                dataType=(lambda v: v and str(v))(data.get("dataType", None)),
                count=int(data["count"]),
                countNulls=(lambda v: v and int(v))(data.get("countNulls", None)),
                categoryFrequencies=(
                    lambda v: v and [CategoryFrequency.from_json(v) for v in v]
                )(
                    data.get("categoryFrequencies", None)
                ),
            )
        except jsonschema.exceptions.ValidationError as ex:
            logging.debug(
                "Invalid JSON data received while parsing CategoricalSummaryStatistics",
                exc_info=ex
            )
            raise
    
    def to_json(self) -> dict:
        """Serialise this instance as JSON.
        
        Returns:
            Data ready to serialise as JSON.
        """
        return {
            "adt_type": self.ADT_TYPE,
            "featureName": str(self.featureName),
            "dataType": (lambda v: v and str(v))(self.dataType),
            "count": self.count,
            "countNulls": (lambda v: v and v)(self.countNulls),
            "categoryFrequencies": (lambda v: v and [v.to_json() for v in v])(self.categoryFrequencies)
        }


@dataclasses.dataclass(frozen=True)
class DefaultSummaryStatistics(SummaryStatistics):
    """Summary statistics for an arbitrary feature.
    
    Args:
        featureName (str): A data field.
        dataType (typing.Optional[str]): A data field.
        count (int): A data field.
        countNulls (typing.Optional[int]): A data field.
    """
    
    ADT_TYPE: typing.ClassVar[str] = "default"
    adt_type: str = dataclasses.field(init=False, repr=False, default=ADT_TYPE)
    
    featureName: str
    dataType: typing.Optional[str]
    count: int
    countNulls: typing.Optional[int]
    
    @classmethod
    def json_schema(cls) -> dict:
        """Return the JSON schema for DefaultSummaryStatistics data.
        
        Returns:
            A Python dictionary describing the JSON schema.
        """
        return {
            "type": "object",
            "properties": {
                "adt_type": {
                    "type": "string",
                    "enum": [cls.ADT_TYPE]
                },
                "featureName": {
                    "type": "string"
                },
                "dataType": {
                    "oneOf": [
                        {"type": "null"},
                        {"type": "string"},
                    ]
                },
                "count": {
                    "type": "integer"
                },
                "countNulls": {
                    "oneOf": [
                        {"type": "null"},
                        {"type": "integer"},
                    ]
                }
            },
            "required": [
                "adt_type",
                "featureName",
                "count",
            ]
        }
    
    @classmethod
    def from_json(cls, data: dict) -> DefaultSummaryStatistics:
        """Validate and parse JSON data into an instance of DefaultSummaryStatistics.
        
        Args:
            data (dict): JSON data to validate and parse.
        
        Returns:
            An instance of DefaultSummaryStatistics.
        
        Raises:
            ValidationError: When schema validation fails.
            KeyError: When a required field is missing from the JSON.
        """
        try:
            jsonschema.validate(data, cls.json_schema())
            return DefaultSummaryStatistics(
                featureName=str(data["featureName"]),
                dataType=(lambda v: v and str(v))(data.get("dataType", None)),
                count=int(data["count"]),
                countNulls=(lambda v: v and int(v))(data.get("countNulls", None)),
            )
        except jsonschema.exceptions.ValidationError as ex:
            logging.debug(
                "Invalid JSON data received while parsing DefaultSummaryStatistics",
                exc_info=ex
            )
            raise
    
    def to_json(self) -> dict:
        """Serialise this instance as JSON.
        
        Returns:
            Data ready to serialise as JSON.
        """
        return {
            "adt_type": self.ADT_TYPE,
            "featureName": str(self.featureName),
            "dataType": (lambda v: v and str(v))(self.dataType),
            "count": self.count,
            "countNulls": (lambda v: v and v)(self.countNulls)
        }


@dataclasses.dataclass(frozen=True)
class EmptySummaryStatistics(SummaryStatistics):
    """Summary statistics for an empty feature.
    
    Args:
        featureName (str): A data field.
        dataType (typing.Optional[str]): A data field.
        countNulls (typing.Optional[int]): A data field.
    """
    
    ADT_TYPE: typing.ClassVar[str] = "empty"
    adt_type: str = dataclasses.field(init=False, repr=False, default=ADT_TYPE)
    
    featureName: str
    dataType: typing.Optional[str]
    countNulls: typing.Optional[int]
    
    @classmethod
    def json_schema(cls) -> dict:
        """Return the JSON schema for EmptySummaryStatistics data.
        
        Returns:
            A Python dictionary describing the JSON schema.
        """
        return {
            "type": "object",
            "properties": {
                "adt_type": {
                    "type": "string",
                    "enum": [cls.ADT_TYPE]
                },
                "featureName": {
                    "type": "string"
                },
                "dataType": {
                    "oneOf": [
                        {"type": "null"},
                        {"type": "string"},
                    ]
                },
                "countNulls": {
                    "oneOf": [
                        {"type": "null"},
                        {"type": "integer"},
                    ]
                }
            },
            "required": [
                "adt_type",
                "featureName",
            ]
        }
    
    @classmethod
    def from_json(cls, data: dict) -> EmptySummaryStatistics:
        """Validate and parse JSON data into an instance of EmptySummaryStatistics.
        
        Args:
            data (dict): JSON data to validate and parse.
        
        Returns:
            An instance of EmptySummaryStatistics.
        
        Raises:
            ValidationError: When schema validation fails.
            KeyError: When a required field is missing from the JSON.
        """
        try:
            jsonschema.validate(data, cls.json_schema())
            return EmptySummaryStatistics(
                featureName=str(data["featureName"]),
                dataType=(lambda v: v and str(v))(data.get("dataType", None)),
                countNulls=(lambda v: v and int(v))(data.get("countNulls", None)),
            )
        except jsonschema.exceptions.ValidationError as ex:
            logging.debug(
                "Invalid JSON data received while parsing EmptySummaryStatistics",
                exc_info=ex
            )
            raise
    
    def to_json(self) -> dict:
        """Serialise this instance as JSON.
        
        Returns:
            Data ready to serialise as JSON.
        """
        return {
            "adt_type": self.ADT_TYPE,
            "featureName": str(self.featureName),
            "dataType": (lambda v: v and str(v))(self.dataType),
            "countNulls": (lambda v: v and v)(self.countNulls)
        }


@dataclasses.dataclass(frozen=True)
class Density:
    """Probability density at a specific value.
    
    Args:
        value (float): A data field.
        density (float): A data field.
    """
    
    value: float
    density: float
    
    @classmethod
    def json_schema(cls) -> dict:
        """Return the JSON schema for Density data.
        
        Returns:
            A Python dictionary describing the JSON schema.
        """
        return {
            "type": "object",
            "properties": {
                "value": {
                    "type": "number"
                },
                "density": {
                    "type": "number"
                }
            },
            "required": [
                "value",
                "density",
            ]
        }
    
    @classmethod
    def from_json(cls, data: dict) -> Density:
        """Validate and parse JSON data into an instance of Density.
        
        Args:
            data (dict): JSON data to validate and parse.
        
        Returns:
            An instance of Density.
        
        Raises:
            ValidationError: When schema validation fails.
            KeyError: When a required field is missing from the JSON.
        """
        try:
            jsonschema.validate(data, cls.json_schema())
            return Density(
                value=float(data["value"]),
                density=float(data["density"]),
            )
        except jsonschema.exceptions.ValidationError as ex:
            logging.debug(
                "Invalid JSON data received while parsing Density",
                exc_info=ex
            )
            raise
    
    def to_json(self) -> dict:
        """Serialise this instance as JSON.
        
        Returns:
            Data ready to serialise as JSON.
        """
        return {
            "value": self.value,
            "density": self.density
        }


@dataclasses.dataclass(frozen=True)
class CategoryFrequency:
    """Frequency of an individual categorical value.
    
    Args:
        category (str): A data field.
        frequency (int): A data field.
    """
    
    category: str
    frequency: int
    
    @classmethod
    def json_schema(cls) -> dict:
        """Return the JSON schema for CategoryFrequency data.
        
        Returns:
            A Python dictionary describing the JSON schema.
        """
        return {
            "type": "object",
            "properties": {
                "category": {
                    "type": "string"
                },
                "frequency": {
                    "type": "integer"
                }
            },
            "required": [
                "category",
                "frequency",
            ]
        }
    
    @classmethod
    def from_json(cls, data: dict) -> CategoryFrequency:
        """Validate and parse JSON data into an instance of CategoryFrequency.
        
        Args:
            data (dict): JSON data to validate and parse.
        
        Returns:
            An instance of CategoryFrequency.
        
        Raises:
            ValidationError: When schema validation fails.
            KeyError: When a required field is missing from the JSON.
        """
        try:
            jsonschema.validate(data, cls.json_schema())
            return CategoryFrequency(
                category=str(data["category"]),
                frequency=int(data["frequency"]),
            )
        except jsonschema.exceptions.ValidationError as ex:
            logging.debug(
                "Invalid JSON data received while parsing CategoryFrequency",
                exc_info=ex
            )
            raise
    
    def to_json(self) -> dict:
        """Serialise this instance as JSON.
        
        Returns:
            Data ready to serialise as JSON.
        """
        return {
            "category": str(self.category),
            "frequency": self.frequency
        }


@dataclasses.dataclass(frozen=True)
class IntegralFrequency:
    """Frequency of an individual categorical value.
    
    Args:
        category (int): A data field.
        frequency (int): A data field.
    """
    
    category: int
    frequency: int
    
    @classmethod
    def json_schema(cls) -> dict:
        """Return the JSON schema for IntegralFrequency data.
        
        Returns:
            A Python dictionary describing the JSON schema.
        """
        return {
            "type": "object",
            "properties": {
                "category": {
                    "type": "integer"
                },
                "frequency": {
                    "type": "integer"
                }
            },
            "required": [
                "category",
                "frequency",
            ]
        }
    
    @classmethod
    def from_json(cls, data: dict) -> IntegralFrequency:
        """Validate and parse JSON data into an instance of IntegralFrequency.
        
        Args:
            data (dict): JSON data to validate and parse.
        
        Returns:
            An instance of IntegralFrequency.
        
        Raises:
            ValidationError: When schema validation fails.
            KeyError: When a required field is missing from the JSON.
        """
        try:
            jsonschema.validate(data, cls.json_schema())
            return IntegralFrequency(
                category=int(data["category"]),
                frequency=int(data["frequency"]),
            )
        except jsonschema.exceptions.ValidationError as ex:
            logging.debug(
                "Invalid JSON data received while parsing IntegralFrequency",
                exc_info=ex
            )
            raise
    
    def to_json(self) -> dict:
        """Serialise this instance as JSON.
        
        Returns:
            Data ready to serialise as JSON.
        """
        return {
            "category": self.category,
            "frequency": self.frequency
        }
