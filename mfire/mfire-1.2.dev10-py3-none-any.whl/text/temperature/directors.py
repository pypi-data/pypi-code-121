"""
Module permettant de gérer la génération de textes de synthèses.
C'est dans ce module qu'on va décider vers quel module
de génération de texte de synthèse on va s'orienter.
"""

from mfire.settings import get_logger

from mfire.text.base import BaseDirector
from mfire.text.temperature import TemperatureReducer, TemperatureBuilder


# Logging
LOGGER = get_logger(name="synthesis_manager.mod", bind="synthesis_manager")


class TemperatureDirector(BaseDirector):
    """ Module permettant de gérer la génération de textes de synthèse.
    """

    reducer: TemperatureReducer = TemperatureReducer()
    builder: TemperatureBuilder = TemperatureBuilder()
