"""
@package lib.text.pheno.factory

Phenonmenon factory for synthesis text generation
"""
# Standard packages

# Own package

from mfire.text.pheno.pheno import Pheno
from mfire.composite.events import EventComposite
from mfire.text.pheno.temperature import TemperatureGeneric
from mfire.text.pheno.wind import WindGeneric
from mfire.text.pheno.snow import SnowGeneric
from mfire.text.pheno.wwmf import WWMFGeneric
from mfire.settings import get_logger

# Logging
LOGGER = get_logger(name="text.pheno.factory.mod", bind="text_pheno_factory")


class PhenoFactory:
    def __init__(
        self, geos, id, condition, params, altitude, localisation, algo="generic"
    ):
        self.id = id
        self.algo = algo
        self.condition = condition
        self.geos = geos
        self.params = params
        self.altitude = altitude
        self.localisation = localisation
        self.pheno = self.get_pheno()

    def get_pheno(self):
        pheno = Pheno
        if self.id == "temperature":
            pheno = TemperatureGeneric
        elif self.id == "wind":
            pheno = WindGeneric
        elif self.id == "snow":
            pheno = SnowGeneric
        elif self.id == "wwmf":
            pheno = WWMFGeneric
        else:
            pheno = Pheno
        return pheno(self.geos, **self.params)

    def satisfy_condition(self):
        if not self.condition:
            # Cas où il n'y a pas de condition à remplir
            return True

        params = self.condition["field"]
        if not params:
            return True

        flist = []
        for field in params:
            try:
                # à corriger

                element_event = EventComposite(**self.condition)
                cval = element_event.compute().values.any()
            except BaseException:
                LOGGER.error(
                    "Unitary event failed.",
                    field=field["file"],
                    func="statisfy_condition",
                    pheno_id=self.id,
                    exc_info=True,
                )
                cval = True

            flist += [cval]

        return any(flist)

    def generate(self):
        return self.pheno.generate()
