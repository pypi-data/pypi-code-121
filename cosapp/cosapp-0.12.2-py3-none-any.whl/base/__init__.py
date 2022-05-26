"""Module containing base classes for user-defined classes.
"""

from cosapp.ports import Port, Scope
from cosapp.systems import System
from cosapp.drivers import Driver
from cosapp.core.connectors import BaseConnector
from cosapp.utils.surrogate_models import SurrogateModel

# Custom exceptions
from cosapp.ports import ScopeError, UnitError
from cosapp.core.connectors import ConnectorError
