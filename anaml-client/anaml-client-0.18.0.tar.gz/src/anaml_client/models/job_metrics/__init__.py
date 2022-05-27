"""Generated implementation of job_metrics."""

# WARNING DO NOT EDIT
# This code was generated from job-metrics.mcn

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
class JobMetrics:
    """Execution statistics for a job run.
    
    Args:
        appId (str): A data field.
        anamlVersion (str): A data field.
        executorCores (typing.Optional[str]): A data field.
        executorMemory (typing.Optional[str]): A data field.
        executorsMax (int): A data field.
        coresMax (int): A data field.
        runTimeSeconds (int): A data field.
        cpuTimeSeconds (int): A data field.
        gcTimeSeconds (int): A data field.
        bytesRead (int): A data field.
        bytesWritten (int): A data field.
        totalTasks (int): A data field.
        failedTasks (int): A data field.
        shuffleLocalBytesRead (int): A data field.
        shuffleRemoteBytesRead (int): A data field.
        shuffleBytesWritten (int): A data field.
    """
    
    appId: str
    anamlVersion: str
    executorCores: typing.Optional[str]
    executorMemory: typing.Optional[str]
    executorsMax: int
    coresMax: int
    runTimeSeconds: int
    cpuTimeSeconds: int
    gcTimeSeconds: int
    bytesRead: int
    bytesWritten: int
    totalTasks: int
    failedTasks: int
    shuffleLocalBytesRead: int
    shuffleRemoteBytesRead: int
    shuffleBytesWritten: int
    
    @classmethod
    def json_schema(cls) -> dict:
        """Return the JSON schema for JobMetrics data.
        
        Returns:
            A Python dictionary describing the JSON schema.
        """
        return {
            "type": "object",
            "properties": {
                "appId": {
                    "type": "string"
                },
                "anamlVersion": {
                    "type": "string"
                },
                "executorCores": {
                    "oneOf": [
                        {"type": "null"},
                        {"type": "string"},
                    ]
                },
                "executorMemory": {
                    "oneOf": [
                        {"type": "null"},
                        {"type": "string"},
                    ]
                },
                "executorsMax": {
                    "type": "integer"
                },
                "coresMax": {
                    "type": "integer"
                },
                "runTimeSeconds": {
                    "type": "integer"
                },
                "cpuTimeSeconds": {
                    "type": "integer"
                },
                "gcTimeSeconds": {
                    "type": "integer"
                },
                "bytesRead": {
                    "type": "integer"
                },
                "bytesWritten": {
                    "type": "integer"
                },
                "totalTasks": {
                    "type": "integer"
                },
                "failedTasks": {
                    "type": "integer"
                },
                "shuffleLocalBytesRead": {
                    "type": "integer"
                },
                "shuffleRemoteBytesRead": {
                    "type": "integer"
                },
                "shuffleBytesWritten": {
                    "type": "integer"
                }
            },
            "required": [
                "appId",
                "anamlVersion",
                "executorsMax",
                "coresMax",
                "runTimeSeconds",
                "cpuTimeSeconds",
                "gcTimeSeconds",
                "bytesRead",
                "bytesWritten",
                "totalTasks",
                "failedTasks",
                "shuffleLocalBytesRead",
                "shuffleRemoteBytesRead",
                "shuffleBytesWritten",
            ]
        }
    
    @classmethod
    def from_json(cls, data: dict) -> JobMetrics:
        """Validate and parse JSON data into an instance of JobMetrics.
        
        Args:
            data (dict): JSON data to validate and parse.
        
        Returns:
            An instance of JobMetrics.
        
        Raises:
            ValidationError: When schema validation fails.
            KeyError: When a required field is missing from the JSON.
        """
        try:
            jsonschema.validate(data, cls.json_schema())
            return JobMetrics(
                appId=str(data["appId"]),
                anamlVersion=str(data["anamlVersion"]),
                executorCores=(lambda v: v and str(v))(data.get("executorCores", None)),
                executorMemory=(lambda v: v and str(v))(data.get("executorMemory", None)),
                executorsMax=int(data["executorsMax"]),
                coresMax=int(data["coresMax"]),
                runTimeSeconds=int(data["runTimeSeconds"]),
                cpuTimeSeconds=int(data["cpuTimeSeconds"]),
                gcTimeSeconds=int(data["gcTimeSeconds"]),
                bytesRead=int(data["bytesRead"]),
                bytesWritten=int(data["bytesWritten"]),
                totalTasks=int(data["totalTasks"]),
                failedTasks=int(data["failedTasks"]),
                shuffleLocalBytesRead=int(data["shuffleLocalBytesRead"]),
                shuffleRemoteBytesRead=int(data["shuffleRemoteBytesRead"]),
                shuffleBytesWritten=int(data["shuffleBytesWritten"]),
            )
        except jsonschema.exceptions.ValidationError as ex:
            logging.debug(
                "Invalid JSON data received while parsing JobMetrics",
                exc_info=ex
            )
            raise
    
    def to_json(self) -> dict:
        """Serialise this instance as JSON.
        
        Returns:
            Data ready to serialise as JSON.
        """
        return {
            "appId": str(self.appId),
            "anamlVersion": str(self.anamlVersion),
            "executorCores": (lambda v: v and str(v))(self.executorCores),
            "executorMemory": (lambda v: v and str(v))(self.executorMemory),
            "executorsMax": int(self.executorsMax),
            "coresMax": int(self.coresMax),
            "runTimeSeconds": self.runTimeSeconds,
            "cpuTimeSeconds": self.cpuTimeSeconds,
            "gcTimeSeconds": self.gcTimeSeconds,
            "bytesRead": self.bytesRead,
            "bytesWritten": self.bytesWritten,
            "totalTasks": int(self.totalTasks),
            "failedTasks": int(self.failedTasks),
            "shuffleLocalBytesRead": self.shuffleLocalBytesRead,
            "shuffleRemoteBytesRead": self.shuffleRemoteBytesRead,
            "shuffleBytesWritten": self.shuffleBytesWritten
        }
