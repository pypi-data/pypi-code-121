from mfire.settings import get_logger
from mfire.text.base import BaseSelector

# Logging
LOGGER = get_logger(name="temperature_selector.mod", bind="temperature_selector")


class TemperatureSelector(BaseSelector):
    """ TemperatureSelector spécifique pour la temperature
    """

    pass
