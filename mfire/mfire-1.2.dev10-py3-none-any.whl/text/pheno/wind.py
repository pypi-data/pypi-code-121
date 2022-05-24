"""
@package lib.text.pheno.wind

Wind text module
"""

# Own package
from mfire.text.pheno.pheno import Pheno
from mfire.utils.my_profile import logwrap
from mfire.settings import get_logger

# Logging
LOGGER = get_logger(name="text.wind.mod", bind="text.wind")


class WindGeneric(Pheno):
    def __init__(self, geos, wind, gust, direction, *args, **kwargs):
        super().__init__(geos, *args, **kwargs)
        self.wind = wind
        self.gust = gust
        self.direction = direction

    @logwrap(logger=LOGGER)
    def generate(self):
        return "Vent : "
