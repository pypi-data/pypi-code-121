"""
@package lib.text.pheno.wwmf

WWMF text module
"""

# Own package
from mfire.text.pheno.pheno import Pheno
from mfire.utils.my_profile import logwrap
from mfire.settings import get_logger

# Logging
LOGGER = get_logger(name="text.wwmf.mod", bind="text.wwmf")


class WWMFGeneric(Pheno):
    def __init__(self, geos, wwmf, precip, rain, snow, lpn, *args, **kwargs):
        super().__init__(geos, *args, **kwargs)
        self.wwmf = wwmf
        self.precip = precip
        self.rain = rain
        self.snow = snow
        self.lpn = lpn

    @logwrap(logger=LOGGER)
    def generate(self):
        return "Temps sensible : "
