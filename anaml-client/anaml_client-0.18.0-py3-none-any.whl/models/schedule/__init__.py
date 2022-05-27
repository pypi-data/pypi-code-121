"""Generated implementation of schedule."""

# WARNING DO NOT EDIT
# This code was generated from schedule.mcn

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
class Duration:
    """A duration in ISO 8601 duration format.
    
    The "T" to separate date and time components must always be included,
    even when the string would be unambiguous without it.
    
    Example: "PT15M" for 15 minutes.
    
    Args:
        value (str): A data field.
    """
    
    value: str
    
    def __str__(self) -> str:
        """Return a str of the wrapped value."""
        return str(self.value)
    
    @classmethod
    def json_schema(cls) -> dict:
        """Return the JSON schema for Duration data.
        
        Returns:
            A Python dictionary describing the JSON schema.
        """
        return {
            "type": "string"
        }
    
    @classmethod
    def from_json(cls, data: dict) -> Duration:
        """Validate and parse JSON data into an instance of Duration.
        
        Args:
            data (dict): JSON data to validate and parse.
        
        Returns:
            An instance of Duration.
        
        Raises:
            ValidationError: When schema validation fails.
            KeyError: When a required field is missing from the JSON.
        """
        try:
            jsonschema.validate(data, cls.json_schema())
            return Duration(str(data))
        except jsonschema.exceptions.ValidationError as ex:
            logging.debug("Invalid JSON data received while parsing Duration", exc_info=ex)
            raise
    
    def to_json(self) -> dict:
        """Serialise this instance as JSON.
        
        Returns:
            Data ready to serialise as JSON.
        """
        return str(self.value)
    
    @classmethod
    def from_json_key(cls, data: str) -> Duration:
        """Parse a JSON string such as a dictionary key."""
        return Duration(str(data))
    
    def to_json_key(self) -> str:
        """Serialise as a JSON string suitable for use as a dictionary key."""
        return str(self.value)


@dataclasses.dataclass(frozen=True)
class RetryPolicy(abc.ABC):
    """Retry policy for jobs that fail."""
    
    ADT_TYPE: typing.ClassVar[str] = ""
    adt_type: str = dataclasses.field(init=False, repr=False, default=ADT_TYPE)
    
    @classmethod
    def json_schema(cls) -> RetryPolicy:
        """JSON schema for variant RetryPolicy.
        
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
    def from_json(cls, data: dict) -> RetryPolicy:
        """Validate and parse JSON data into an instance of RetryPolicy.
        
        Args:
            data (dict): JSON data to validate and parse.
        
        Returns:
            An instance of RetryPolicy.
        
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
            logging.debug("Invalid JSON data received while parsing RetryPolicy", exc_info=ex)
            raise
    
    @abc.abstractmethod
    def to_json(self) -> dict:
        """Serialise this instance as JSON.
        
        Returns:
            Data ready to serialise as JSON.
        """
        raise NotImplementedError


@dataclasses.dataclass(frozen=True)
class FixedRetryPolicy(RetryPolicy):
    """Retry a failed job after a fixed backoff.
    
    Args:
        backoff (Duration): A data field.
        maxAttempts (int): A data field.
    """
    
    ADT_TYPE: typing.ClassVar[str] = "fixed"
    adt_type: str = dataclasses.field(init=False, repr=False, default=ADT_TYPE)
    
    backoff: Duration
    maxAttempts: int
    
    @classmethod
    def json_schema(cls) -> dict:
        """Return the JSON schema for FixedRetryPolicy data.
        
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
                "backoff": Duration.json_schema(),
                "maxAttempts": {
                    "type": "integer"
                }
            },
            "required": [
                "adt_type",
                "backoff",
                "maxAttempts",
            ]
        }
    
    @classmethod
    def from_json(cls, data: dict) -> FixedRetryPolicy:
        """Validate and parse JSON data into an instance of FixedRetryPolicy.
        
        Args:
            data (dict): JSON data to validate and parse.
        
        Returns:
            An instance of FixedRetryPolicy.
        
        Raises:
            ValidationError: When schema validation fails.
            KeyError: When a required field is missing from the JSON.
        """
        try:
            jsonschema.validate(data, cls.json_schema())
            return FixedRetryPolicy(
                backoff=Duration.from_json(data["backoff"]),
                maxAttempts=int(data["maxAttempts"]),
            )
        except jsonschema.exceptions.ValidationError as ex:
            logging.debug(
                "Invalid JSON data received while parsing FixedRetryPolicy",
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
            "backoff": self.backoff.to_json(),
            "maxAttempts": int(self.maxAttempts)
        }


@dataclasses.dataclass(frozen=True)
class NeverRetryPolicy(RetryPolicy):
    """Never retry a failed job."""
    
    ADT_TYPE: typing.ClassVar[str] = "never"
    adt_type: str = dataclasses.field(init=False, repr=False, default=ADT_TYPE)
    
    @classmethod
    def json_schema(cls) -> dict:
        """Return the JSON schema for NeverRetryPolicy data.
        
        Returns:
            A Python dictionary describing the JSON schema.
        """
        return {
            "type": "object",
            "properties": {
                "adt_type": {
                    "type": "string",
                    "enum": [cls.ADT_TYPE]
                }
            },
            "required": [
                "adt_type",
            ]
        }
    
    @classmethod
    def from_json(cls, data: dict) -> NeverRetryPolicy:
        """Validate and parse JSON data into an instance of NeverRetryPolicy.
        
        Args:
            data (dict): JSON data to validate and parse.
        
        Returns:
            An instance of NeverRetryPolicy.
        
        Raises:
            ValidationError: When schema validation fails.
            KeyError: When a required field is missing from the JSON.
        """
        try:
            jsonschema.validate(data, cls.json_schema())
            return NeverRetryPolicy(
                
            )
        except jsonschema.exceptions.ValidationError as ex:
            logging.debug(
                "Invalid JSON data received while parsing NeverRetryPolicy",
                exc_info=ex
            )
            raise
    
    def to_json(self) -> dict:
        """Serialise this instance as JSON.
        
        Returns:
            Data ready to serialise as JSON.
        """
        return {
            "adt_type": self.ADT_TYPE
        }


@dataclasses.dataclass(frozen=True)
class Schedule(abc.ABC):
    """Schedule specification for a job."""
    
    ADT_TYPE: typing.ClassVar[str] = ""
    adt_type: str = dataclasses.field(init=False, repr=False, default=ADT_TYPE)
    
    @classmethod
    def json_schema(cls) -> Schedule:
        """JSON schema for variant Schedule.
        
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
    def from_json(cls, data: dict) -> Schedule:
        """Validate and parse JSON data into an instance of Schedule.
        
        Args:
            data (dict): JSON data to validate and parse.
        
        Returns:
            An instance of Schedule.
        
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
            logging.debug("Invalid JSON data received while parsing Schedule", exc_info=ex)
            raise
    
    @abc.abstractmethod
    def to_json(self) -> dict:
        """Serialise this instance as JSON.
        
        Returns:
            Data ready to serialise as JSON.
        """
        raise NotImplementedError


@dataclasses.dataclass(frozen=True)
class DailySchedule(Schedule):
    """Execute the job daily.
    
    Args:
        startTimeOfDay (typing.Optional[str]): A data field.
        retryPolicy (RetryPolicy): A data field.
    """
    
    ADT_TYPE: typing.ClassVar[str] = "daily"
    adt_type: str = dataclasses.field(init=False, repr=False, default=ADT_TYPE)
    
    startTimeOfDay: typing.Optional[str]
    retryPolicy: RetryPolicy
    
    @classmethod
    def json_schema(cls) -> dict:
        """Return the JSON schema for DailySchedule data.
        
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
                "startTimeOfDay": {
                    "oneOf": [
                        {"type": "null"},
                        {"type": "string"},
                    ]
                },
                "retryPolicy": RetryPolicy.json_schema()
            },
            "required": [
                "adt_type",
                "retryPolicy",
            ]
        }
    
    @classmethod
    def from_json(cls, data: dict) -> DailySchedule:
        """Validate and parse JSON data into an instance of DailySchedule.
        
        Args:
            data (dict): JSON data to validate and parse.
        
        Returns:
            An instance of DailySchedule.
        
        Raises:
            ValidationError: When schema validation fails.
            KeyError: When a required field is missing from the JSON.
        """
        try:
            jsonschema.validate(data, cls.json_schema())
            return DailySchedule(
                startTimeOfDay=(lambda v: v and str(v))(data.get("startTimeOfDay", None)),
                retryPolicy=RetryPolicy.from_json(data["retryPolicy"]),
            )
        except jsonschema.exceptions.ValidationError as ex:
            logging.debug(
                "Invalid JSON data received while parsing DailySchedule",
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
            "startTimeOfDay": (lambda v: v and str(v))(self.startTimeOfDay),
            "retryPolicy": self.retryPolicy.to_json()
        }


@dataclasses.dataclass(frozen=True)
class CronSchedule(Schedule):
    """Execute the job according to a cron schedule string.
    
    Args:
        cronString (str): A data field.
        retryPolicy (RetryPolicy): A data field.
    """
    
    ADT_TYPE: typing.ClassVar[str] = "cron"
    adt_type: str = dataclasses.field(init=False, repr=False, default=ADT_TYPE)
    
    cronString: str
    retryPolicy: RetryPolicy
    
    @classmethod
    def json_schema(cls) -> dict:
        """Return the JSON schema for CronSchedule data.
        
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
                "cronString": {
                    "type": "string"
                },
                "retryPolicy": RetryPolicy.json_schema()
            },
            "required": [
                "adt_type",
                "cronString",
                "retryPolicy",
            ]
        }
    
    @classmethod
    def from_json(cls, data: dict) -> CronSchedule:
        """Validate and parse JSON data into an instance of CronSchedule.
        
        Args:
            data (dict): JSON data to validate and parse.
        
        Returns:
            An instance of CronSchedule.
        
        Raises:
            ValidationError: When schema validation fails.
            KeyError: When a required field is missing from the JSON.
        """
        try:
            jsonschema.validate(data, cls.json_schema())
            return CronSchedule(
                cronString=str(data["cronString"]),
                retryPolicy=RetryPolicy.from_json(data["retryPolicy"]),
            )
        except jsonschema.exceptions.ValidationError as ex:
            logging.debug(
                "Invalid JSON data received while parsing CronSchedule",
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
            "cronString": str(self.cronString),
            "retryPolicy": self.retryPolicy.to_json()
        }


@dataclasses.dataclass(frozen=True)
class NeverSchedule(Schedule):
    """Do not execute the job automatically."""
    
    ADT_TYPE: typing.ClassVar[str] = "never"
    adt_type: str = dataclasses.field(init=False, repr=False, default=ADT_TYPE)
    
    @classmethod
    def json_schema(cls) -> dict:
        """Return the JSON schema for NeverSchedule data.
        
        Returns:
            A Python dictionary describing the JSON schema.
        """
        return {
            "type": "object",
            "properties": {
                "adt_type": {
                    "type": "string",
                    "enum": [cls.ADT_TYPE]
                }
            },
            "required": [
                "adt_type",
            ]
        }
    
    @classmethod
    def from_json(cls, data: dict) -> NeverSchedule:
        """Validate and parse JSON data into an instance of NeverSchedule.
        
        Args:
            data (dict): JSON data to validate and parse.
        
        Returns:
            An instance of NeverSchedule.
        
        Raises:
            ValidationError: When schema validation fails.
            KeyError: When a required field is missing from the JSON.
        """
        try:
            jsonschema.validate(data, cls.json_schema())
            return NeverSchedule(
                
            )
        except jsonschema.exceptions.ValidationError as ex:
            logging.debug(
                "Invalid JSON data received while parsing NeverSchedule",
                exc_info=ex
            )
            raise
    
    def to_json(self) -> dict:
        """Serialise this instance as JSON.
        
        Returns:
            Data ready to serialise as JSON.
        """
        return {
            "adt_type": self.ADT_TYPE
        }


@dataclasses.dataclass(frozen=True)
class ScheduleState:
    """Current scheduling state of a job execution.
    
    Args:
        schedule (Schedule): A data field.
        scheduledStartTime (datetime.datetime): A data field.
        retryCount (int): A data field.
    """
    
    schedule: Schedule
    scheduledStartTime: datetime.datetime
    retryCount: int
    
    @classmethod
    def json_schema(cls) -> dict:
        """Return the JSON schema for ScheduleState data.
        
        Returns:
            A Python dictionary describing the JSON schema.
        """
        return {
            "type": "object",
            "properties": {
                "schedule": Schedule.json_schema(),
                "scheduledStartTime": {
                    "type": "string",
                    "format": "date-time"
                },
                "retryCount": {
                    "type": "integer"
                }
            },
            "required": [
                "schedule",
                "scheduledStartTime",
                "retryCount",
            ]
        }
    
    @classmethod
    def from_json(cls, data: dict) -> ScheduleState:
        """Validate and parse JSON data into an instance of ScheduleState.
        
        Args:
            data (dict): JSON data to validate and parse.
        
        Returns:
            An instance of ScheduleState.
        
        Raises:
            ValidationError: When schema validation fails.
            KeyError: When a required field is missing from the JSON.
        """
        try:
            jsonschema.validate(data, cls.json_schema())
            return ScheduleState(
                schedule=Schedule.from_json(data["schedule"]),
                scheduledStartTime=isodate.parse_datetime(data["scheduledStartTime"]),
                retryCount=int(data["retryCount"]),
            )
        except jsonschema.exceptions.ValidationError as ex:
            logging.debug(
                "Invalid JSON data received while parsing ScheduleState",
                exc_info=ex
            )
            raise
    
    def to_json(self) -> dict:
        """Serialise this instance as JSON.
        
        Returns:
            Data ready to serialise as JSON.
        """
        return {
            "schedule": self.schedule.to_json(),
            "scheduledStartTime": self.scheduledStartTime.strftime('%Y-%m-%dT%H:%M:%S.%f%z'),
            "retryCount": int(self.retryCount)
        }
