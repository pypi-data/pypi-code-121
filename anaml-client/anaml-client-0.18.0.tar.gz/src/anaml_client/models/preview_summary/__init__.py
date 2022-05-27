"""Generated implementation of preview_summary."""

# WARNING DO NOT EDIT
# This code was generated from preview-summary.mcn

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

from ..entity import EntityName
from ..summary_statistics import SummaryStatistics


@dataclasses.dataclass(frozen=True)
class PreviewSummary:
    """Preview Summary for Features.
    
    Args:
        entityName (EntityName): A data field.
        statistics (typing.List[SummaryStatistics]): A data field.
    """
    
    entityName: EntityName
    statistics: typing.List[SummaryStatistics]
    
    @classmethod
    def json_schema(cls) -> dict:
        """Return the JSON schema for PreviewSummary data.
        
        Returns:
            A Python dictionary describing the JSON schema.
        """
        return {
            "type": "object",
            "properties": {
                "entityName": EntityName.json_schema(),
                "statistics": {
                    "type": "array",
                    "item": SummaryStatistics.json_schema()
                }
            },
            "required": [
                "entityName",
                "statistics",
            ]
        }
    
    @classmethod
    def from_json(cls, data: dict) -> PreviewSummary:
        """Validate and parse JSON data into an instance of PreviewSummary.
        
        Args:
            data (dict): JSON data to validate and parse.
        
        Returns:
            An instance of PreviewSummary.
        
        Raises:
            ValidationError: When schema validation fails.
            KeyError: When a required field is missing from the JSON.
        """
        try:
            jsonschema.validate(data, cls.json_schema())
            return PreviewSummary(
                entityName=EntityName.from_json(data["entityName"]),
                statistics=[SummaryStatistics.from_json(v) for v in data["statistics"]],
            )
        except jsonschema.exceptions.ValidationError as ex:
            logging.debug(
                "Invalid JSON data received while parsing PreviewSummary",
                exc_info=ex
            )
            raise
    
    def to_json(self) -> dict:
        """Serialise this instance as JSON.
        
        Returns:
            Data ready to serialise as JSON.
        """
        return {
            "entityName": self.entityName.to_json(),
            "statistics": [v.to_json() for v in self.statistics]
        }
