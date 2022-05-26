from dataclasses import dataclass
from typing import List

from mlflow.entities import Metric


@dataclass
class Event(object):
    """
    Base Event type
    """

    producer: str


@dataclass
class LogMetricsEvent(Event):
    """
    Metrics Event
    """

    metrics: List[Metric]
