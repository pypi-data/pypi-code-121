from typing import Dict, List

from chaoslib.exceptions import ActivityFailed
from chaoslib.types import Configuration, Secrets
from logzero import logger

from chaosreliably import get_session
from chaosreliably.types import (
    ObjectiveEntities,
    ObjectiveEntity,
    ObjectiveResult,
)

from .. import encoded_selector
from .tolerances import all_objective_results_ok

__all__ = ["get_objective_results_by_labels", "slo_is_met"]


def get_objective_by_label(
    labels: Dict[str, str],
    configuration: Configuration = None,
    secrets: Secrets = None,
) -> ObjectiveEntity:
    s = encoded_selector(labels)

    with get_session("reliably.com/v1", configuration, secrets) as session:
        resp = session.get(f"/objective?selector={s}")
        logger.debug(f"Fetched objective from: {resp.url}")
        if resp.status_code != 200:
            raise ActivityFailed(f"Failed to retrieve objective: {resp.text}")
        o = resp.json()
        logger.debug(f"Return objective: {o}")
        objectives = ObjectiveEntities.parse_list(o)
        if not objectives:
            raise ActivityFailed(
                "No objectives found to match the given labels"
            )

        return objectives[0]


def get_objective_results_by_labels(
    labels: Dict[str, str],
    limit: int = 1,
    configuration: Configuration = None,
    secrets: Secrets = None,
) -> List[ObjectiveResult]:
    """
    For a given set of Objective labels, return all of the Ojective Results

    :param labels: Dict[str, str] representing the Objective Labels for the
        Objective to retrieve results for
    :param limit: int representing how many results to retrieve - Default 1
    :param configuration: Configuration object provided by Chaos Toolkit
    :param secrets: Secret object provided by Chaos Toolkit
    :returns: List[ObjectiveResult] representing the Objective Results for the
        given Objective

    """
    o = get_objective_by_label(labels, configuration, secrets)
    s = encoded_selector(o.spec.selector)
    qs = f"selector={s}&limit={limit}"

    with get_session("reliably.com/v1", configuration, secrets) as session:
        resp = session.get(f"/objective_result?{qs}")
        logger.debug(f"Fetched objective results from: {resp.url}")
        if resp.status_code != 200:
            raise ActivityFailed(f"Failed to retrieve SLO results: {resp.text}")
        o = resp.json()
        logger.debug(f"Return objective result: {o}")
        return ObjectiveResult.parse_list(o)


def slo_is_met(
    labels: Dict[str, str],
    limit: int = 1,
    configuration: Configuration = None,
    secrets: Secrets = None,
) -> bool:
    """
    For a given set of Objective labels, return whether the Objective was met

    :param labels: Dict[str, str] representing the Objective Labels for the
        Objective to retrieve results for
    :param limit: int representing how many results to retrieve - Default 1
    :param configuration: Configuration object provided by Chaos Toolkit
    :param secrets: Secret object provided by Chaos Toolkit
    :returns: bool representing whether the SLO was met or not
    """
    results = get_objective_results_by_labels(
        labels=labels, limit=limit, configuration=configuration, secrets=secrets
    )
    return all_objective_results_ok(results)
