"""
@package lib.text.generator

Synthesis text generator
"""

# Standard packages

# Own package
from mfire.utils.date import Datetime
from mfire.text.pheno.factory import PhenoFactory
from mfire.utils.my_profile import logwrap
from mfire.settings import get_logger

# Logging
LOGGER = get_logger(name="text.generator.mod", bind="text_generator")


class TextGenerator:
    def __init__(self, id, name, production_datetime, period, geos, weathers, **kwargs):
        self.id = id
        self.name = name
        self.production_datetime = Datetime(production_datetime)
        self.geos = geos
        self.period = {
            "id": period.get("id", ""),
            "name": period.get("name", ""),
            "start": Datetime(period["start"]),
            "stop": Datetime(period["stop"]),
        }
        self.weathers = weathers
        self.kwargs = kwargs
        self.time_dimension = kwargs.pop("time_dimension", "step")
        if self.time_dimension == "step":
            LOGGER.info(
                "Time dimension has been set to default. "
                "Please check if this is correct.",
                time_dimension=self.time_dimension,
                text_id=self.id,
                period_id=self.period.get("id"),
                func="__init__",
            )

    def generate_weather(self, weather_idx):
        pheno_factory = PhenoFactory(**self.weathers[weather_idx])
        if pheno_factory.satisfy_condition():
            return pheno_factory.generate()
        return ""

    @logwrap(logger=LOGGER)
    def generate(self):
        my_text = ""
        for weather_idx in range(len(self.weathers)):
            my_text += self.generate_weather(weather_idx) + "\n"

        return my_text
