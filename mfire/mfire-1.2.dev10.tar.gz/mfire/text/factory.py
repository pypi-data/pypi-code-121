"""
Choisi le type de type de texte de synthèse en fonction du paramètre (weather)
"""

from mfire.settings import get_logger

from mfire.composite import WeatherComposite
from mfire.text.temperature import TemperatureDirector


# Logging
LOGGER = get_logger(name="text_director_factory.mod", bind="text_director_factory")


class DirectorFactory:
    def compute(self, weather: WeatherComposite):
        director = None
        LOGGER.info(weather.id)
        if weather.id == "tempe":
            director = TemperatureDirector()
        else:
            raise ValueError(f"No text Director found for given Weather '{weather.id}'")

        return director.compute(component=weather)
