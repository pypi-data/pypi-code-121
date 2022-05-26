"""Helpers for interacting with the PagerDuty API."""

from enum import Enum
from typing import Any, Dict, List, Optional

from sym.sdk.errors import SymIntegrationErrorEnum
from sym.sdk.user import User


class PagerDutyError(SymIntegrationErrorEnum):
    """Raised when there is an error connecting to PagerDuty's API."""

    UNKNOWN_ERROR = ("An unexpected error occurred while trying to connect to PagerDuty.",)
    API_ERROR = ("An error occurred with the {endpoint} endpoint of the PagerDuty API: {err}",)
    API_TOKEN_ERROR = ("A PagerDuty API Token has not been set",)
    API_TOKEN_LOOKUP_ERROR = ("A PagerDuty API token could not be looked up",)


class PagerDutyStatus(str, Enum):
    """Represents possible incident statuses in PagerDuty."""

    TRIGGERED = "triggered"
    ACKNOWLEDGED = "acknowledged"
    RESOLVED = "resolved"


class PagerDutyUrgency(str, Enum):
    """Represents possible incident urgencies in PagerDuty."""

    LOW = "low"
    HIGH = "high"


def is_on_call(
    user: User,
    *,
    escalation_policy_name: Optional[str] = None,
    escalation_policy_id: Optional[str] = None,
    schedule_name: Optional[str] = None,
    schedule_id: Optional[str] = None,
) -> bool:
    """Checks if the provided user is currently on-call according to PagerDuty.

    If a name or ID is provided for either escalation policy or schedule, checks if the user is
    on-call for specified escalation policy or schedule.

    If no name or ID is provided for either escalation policy or schedule, checks if the user is
    on-call for ANY escalation policy or schedule.

    Args:
        escalation_policy_name: The name of a specific Escalation Policy to check.
        escalation_policy_id: The ID of a specific Escalation Policy to check.
        schedule_name: The name of a specific Schedule to check.
        schedule_id: The ID of a specific Schedule to check.
    """


def users_on_call(
    *,
    escalation_policy_name: Optional[str] = None,
    escalation_policy_id: Optional[str] = None,
    schedule_name: Optional[str] = None,
    schedule_id: Optional[str] = None,
) -> List[User]:
    """Get all on-call users for the specified escalation policy or schedule from PagerDuty.

    Escalation policy or schedule can be specified by name or ID. If none are provided, returns
    on-call users for ALL escalation policies + schedules.

    Args:
        escalation_policy_name: The name of a specific Escalation Policy to check.
        escalation_policy_id: The ID of a specific Escalation Policy to check.
        schedule_name: The name of a specific Schedule to check.
        schedule_id: The ID of a specific Schedule to check.
    """


def users_for_schedule(
    *,
    schedule_name: Optional[str] = None,
    schedule_id: Optional[str] = None,
) -> List[User]:
    """Get all users for the specified schedule from PagerDuty.

    Schedule can be specified by name or ID.

    Args:
        schedule_name: The name of a specific Schedule to check.
        schedule_id: The ID of a specific Schedule to check.
    """


def get_incidents(
    *,
    assignees: Optional[List[User]] = None,
    service_ids: Optional[List[str]] = None,
    statuses: Optional[List[PagerDutyStatus]] = None,
    urgencies: Optional[List[PagerDutyUrgency]] = None,
    since: Optional[str] = None,
    until: Optional[str] = None,
) -> List[Dict[str, Any]]:
    """Retrieve incidents from PagerDuty based on provided filter params.

    Args:
        assignees: When provided, only incidents assigned to one of these users will be returned.
        service_ids: When provided, only incidents in one of these services will be returned.
        statuses: When provided, only incidents with these statuses will be returned. Defaults to
            ``["TRIGGERED", "ACKNOWLEDGED"]``. Note: If ``assignees`` is provided, ``statuses`` cannot
            contain ``RESOLVED``.
        urgencies: When provided, only incidents with these urgencies will be returned. Defaults to
            ``["HIGH"]``.
        since: When provided, only incidents on or after ``since`` will be returned. Defaults to 24
            hours ago if not provided. Must be an ISO-8601 datetime.
        until: When provided, only incidents before ``until`` will be returned. Defaults to 1
            month after ``since`` if not provided. Must be an ISO-8601 datetime.

    Returns:
        A list of dictionaries, with each dictionary representing an incident in PagerDuty's
        ``incident`` structure. See
        `here <https://developer.pagerduty.com/api-reference/9d0b4b12e36f9-list-incidents#Responses>`_
        for details.
    """


def has_incident(
    *,
    assignees: Optional[List[User]] = None,
    service_ids: Optional[List[str]] = None,
    statuses: Optional[List[PagerDutyStatus]] = None,
    urgencies: Optional[List[PagerDutyUrgency]] = None,
    since: Optional[str] = None,
    until: Optional[str] = None,
) -> bool:
    """Return whether there exists an incident that matches the filters provided in the params.

    Args:
        assignees: When provided, only incidents assigned to one of these users will be returned.
        service_ids: When provided, only incidents in one of these services will be returned.
        statuses: When provided, only incidents with these statuses will be returned. Defaults to
            ``["TRIGGERED", "ACKNOWLEDGED"]``. Note: If ``assignees`` is provided, ``statuses`` cannot
            contain ``RESOLVED``.
        urgencies: When provided, only incidents with these urgencies will be returned. Defaults to
            ``["HIGH"]``.
        since: When provided, only incidents on or after ``since`` will be returned. Defaults to 24
            hours ago if not provided. Must be an ISO-8601 datetime.
        until: When provided, only incidents before ``until`` will be returned. Defaults to 1
            month after ``since`` if not provided. Must be an ISO-8601 datetime.

    Returns:
        A boolean representing whether there is an incident matching the given filter parameters.
    """
