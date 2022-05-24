"""
@package lib.text.pheno.snow

Snow text module
"""

# Own package
from mfire.text.pheno.pheno import Pheno
from mfire.utils.my_profile import logwrap
from mfire.settings import get_logger

# Logging
LOGGER = get_logger(name="text.snow.mod", bind="text.snow")


class SnowGeneric(Pheno):
    def __init__(self, geos, snow, lpn, *args, **kwargs):
        super().__init__(geos, *args, **kwargs)
        self.snow = snow
        self.lpn = lpn

    @logwrap(logger=LOGGER)
    def generate(self):
        return "Neige : "
