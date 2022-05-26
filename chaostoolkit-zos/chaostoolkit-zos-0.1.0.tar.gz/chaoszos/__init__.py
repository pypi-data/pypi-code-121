# -*- coding: utf-8 -*-

"""Top-level package for chaostoolkit-zos."""

from typing import Dict, List

from chaoslib.discovery.discover import (discover_actions, discover_probes)
from chaoslib.types import (DiscoveredActivities, Secrets)


__version__ = '0.1.0'
__all__ = ["__version__", "get_connection_information", "load_exported_activities"]


def get_connection_information(secrets: Secrets = None) -> Dict[str, str]:
    """
    If connection information and credentials are specified in via secrets,
    load them here

    :param secrets:
    :return:
    """

    connection_information = dict(zos_console=None)

    if secrets():
        connection_information['zos_console'] = secrets.get("zos_console")

    return connection_information


def load_exported_activities() -> List[DiscoveredActivities]:
    """
    Extract information from zos actions and probes
    :return:
    """

    activities = list()

    activities.extend(discover_actions("chaoszos.zos.actions"))
    activities.extend(discover_probes("chaoszos.zos.probes"))

    return activities
