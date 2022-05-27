"""Generated implementation of feature_run_summaries."""

# WARNING DO NOT EDIT
# This code was generated from feature-run-summaries.mcn

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

from ..feature_store import FeatureStoreId
from ..jobs import FeatureStoreRunId
from ..summary_statistics import SummaryStatistics


@dataclasses.dataclass(frozen=True)
class FeatureRunSummary:
    """Data describing a feature store run and summarising the generated features.
    
    Args:
        featureStore (FeatureStoreId): A data field.
        featureRun (FeatureStoreRunId): A data field.
        runStartDate (datetime.date): A data field.
        runEndDate (datetime.date): A data field.
        runTime (datetime.datetime): A data field.
        stats (SummaryStatistics): A data field.
    """
    
    featureStore: FeatureStoreId
    featureRun: FeatureStoreRunId
    runStartDate: datetime.date
    runEndDate: datetime.date
    runTime: datetime.datetime
    stats: SummaryStatistics
    
    @classmethod
    def json_schema(cls) -> dict:
        """Return the JSON schema for FeatureRunSummary data.
        
        Returns:
            A Python dictionary describing the JSON schema.
        """
        return {
            "type": "object",
            "properties": {
                "featureStore": FeatureStoreId.json_schema(),
                "featureRun": FeatureStoreRunId.json_schema(),
                "runStartDate": {
                    "type": "string",
                    "format": "date"
                },
                "runEndDate": {
                    "type": "string",
                    "format": "date"
                },
                "runTime": {
                    "type": "string",
                    "format": "date-time"
                },
                "stats": SummaryStatistics.json_schema()
            },
            "required": [
                "featureStore",
                "featureRun",
                "runStartDate",
                "runEndDate",
                "runTime",
                "stats",
            ]
        }
    
    @classmethod
    def from_json(cls, data: dict) -> FeatureRunSummary:
        """Validate and parse JSON data into an instance of FeatureRunSummary.
        
        Args:
            data (dict): JSON data to validate and parse.
        
        Returns:
            An instance of FeatureRunSummary.
        
        Raises:
            ValidationError: When schema validation fails.
            KeyError: When a required field is missing from the JSON.
        """
        try:
            jsonschema.validate(data, cls.json_schema())
            return FeatureRunSummary(
                featureStore=FeatureStoreId.from_json(data["featureStore"]),
                featureRun=FeatureStoreRunId.from_json(data["featureRun"]),
                runStartDate=datetime.date.fromisoformat(data["runStartDate"]),
                runEndDate=datetime.date.fromisoformat(data["runEndDate"]),
                runTime=isodate.parse_datetime(data["runTime"]),
                stats=SummaryStatistics.from_json(data["stats"]),
            )
        except jsonschema.exceptions.ValidationError as ex:
            logging.debug(
                "Invalid JSON data received while parsing FeatureRunSummary",
                exc_info=ex
            )
            raise
    
    def to_json(self) -> dict:
        """Serialise this instance as JSON.
        
        Returns:
            Data ready to serialise as JSON.
        """
        return {
            "featureStore": self.featureStore.to_json(),
            "featureRun": self.featureRun.to_json(),
            "runStartDate": self.runStartDate.isoformat(),
            "runEndDate": self.runEndDate.isoformat(),
            "runTime": self.runTime.strftime('%Y-%m-%dT%H:%M:%S.%f%z'),
            "stats": self.stats.to_json()
        }
