"""Generated implementation of roles."""

# WARNING DO NOT EDIT
# This code was generated from roles.mcn

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


class Role(enum.Enum):
    """Roles/permissions."""
    Author = "author"
    """Grants permission to create and manage feature definitions."""
    AdminBranchPerms = "adminbranchperms"
    """Grants permission to manage branch permissions."""
    AdminGroups = "admingroups"
    """Grants permission to manage user groups."""
    AdminSystem = "adminsystem"
    """Grants permission to manage Source + Destination configuration."""
    AdminAttributes = "adminattributes"
    """Grants permission to manage Label + Attribute configuration."""
    AdminSchedules = "adminschedules"
    """Grants permission to manage feature run scheduling."""
    AdminUsers = "adminusers"
    """Grants permission to manage users."""
    AdminWebhooks = "adminwebhooks"
    """Grants permission to manage webhooks."""
    RunCaching = "runcaching"
    """Grants permission to run caching jobs."""
    RunFeatureGen = "runfeaturegen"
    """Grants permission to run feature generation jobs."""
    RunEventStore = "runeventstore"
    """Grants permission to run event store jobs."""
    RunMonitoring = "runmonitoring"
    """Grants permission to run table monitoring jobs."""
    SuperUser = "superuser"
    """Grants full access."""
    ViewReports = "viewreports"
    """Grants permission to view reports."""
    
    @classmethod
    def json_schema(cls) -> dict:
        """JSON schema for 'Role'.
        
        Returns:
            A Python dictionary describing the JSON schema.
        """
        return {
            "type": "object",
            "properties": {
                "adt_type": {
                    "type": "string",
                    "enum": [
                        "author",
                        "adminbranchperms",
                        "admingroups",
                        "adminsystem",
                        "adminattributes",
                        "adminschedules",
                        "adminusers",
                        "adminwebhooks",
                        "runcaching",
                        "runfeaturegen",
                        "runeventstore",
                        "runmonitoring",
                        "superuser",
                        "viewreports",
                    ]
                }
            },
            "required": [
                "adt_type",
            ]
        }
    
    @classmethod
    def from_json(cls, data: dict) -> Role:
        """Validate and parse JSON data into an instance of Role.
        
        Args:
            data (dict): JSON data to validate and parse.
        
        Returns:
            An instance of Role.
        
        Raises:
            ValidationError: When schema validation fails.
            KeyError: When a required field is missing from the JSON.
        """
        try:
            jsonschema.validate(data, cls.json_schema())
            return Role(str(data['adt_type']))
        except jsonschema.exceptions.ValidationError as ex:
            logging.debug("Invalid JSON data received while parsing Role", exc_info=ex)
            raise
    
    def to_json(self) -> dict:
        """Serialise this instance as JSON.
        
        Returns:
            JSON data ready to be serialised.
        """
        return {'adt_type': self.value}
    
    @classmethod
    def from_json_key(cls, data: str) -> Role:
        """Validate and parse a value from a JSON dictionary key.
        
        Args:
            data (str): JSON data to validate and parse.
        
        Returns:
            An instance of Role.
        """
        return Role(str(data))
    
    def to_json_key(self) -> str:
        """Serialised this instanse as a JSON string for use as a dictionary key.
        
        Returns:
            A JSON string ready to be used as a key.
        """
        return str(self.value)
