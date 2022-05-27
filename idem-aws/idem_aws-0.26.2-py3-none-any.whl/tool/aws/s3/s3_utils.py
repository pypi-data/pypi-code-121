from typing import Dict
from typing import List

from dict_tools import data


def get_notification_configuration_diff(
    hub, new_notifications: Dict[str, List], old_state: Dict[str, List]
) -> Dict[str, List]:
    """
    This functions helps in comparing two dicts.
    It compares each key value in both the dicts and return diff notifications configuration

    Returns:
        {Resultant notifications dictionary}

    """

    old_state_notification = old_state.get("notifications")

    old_state_notification = (
        old_state_notification if old_state_notification is not None else {}
    )

    return data.recursive_diff(
        new_notifications, old_state_notification, ignore_order=True
    )
