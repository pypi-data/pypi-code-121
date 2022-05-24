"""mfire.composite module

This module handles everything related to the Config Handling

"""

from mfire.composite.operators import LogicalOperator, ComparisonOperator
from mfire.composite.periods import Period, PeriodCollection
from mfire.composite.aggregations import AggregationType, AggregationMethod, Aggregation

from mfire.composite.base import BaseComposite
from mfire.composite.fields import FieldComposite
from mfire.composite.geos import GeoComposite, AltitudeComposite
from mfire.composite.events import Threshold, EventComposite, EventBertrandComposite

from mfire.composite.levels import LevelComposite, LocalisationConfig
from mfire.composite.weather import WeatherComposite
from mfire.composite.components import (
    AbstractComponentComposite,
    RiskComponentComposite,
    TextComponentComposite,
)
from mfire.composite.productions import ProductionComposite

__all__ = [
    "LogicalOperator",
    "ComparisonOperator",
    "Period",
    "PeriodCollection",
    "AggregationType",
    "AggregationMethod",
    "Aggregation",
    "BaseComposite",
    "FieldComposite",
    "GeoComposite",
    "AltitudeComposite",
    "Threshold",
    "EventComposite",
    "EventBertrandComposite",
    "LevelComposite",
    "LocalisationConfig",
    "WeatherComposite",
    "AbstractComponentComposite",
    "RiskComponentComposite",
    "TextComponentComposite",
    "ProductionComposite",
]
