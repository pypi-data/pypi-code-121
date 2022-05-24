"""
@package lib.text.pheno.abstract

Abstract class for phenomenon description
"""

# Own package
from mfire.utils.my_profile import logwrap
from mfire.settings import get_logger

# Logging
LOGGER = get_logger(name="text.pheno.mod", bind="text.pheno")


class Pheno:
    def __init__(self, geos, *args, **kwargs):
        self.geos = geos
        self.args = args
        self.kwargs = kwargs

    @logwrap(logger=LOGGER)
    def generate(self):
        return "C'est le pheno !"
