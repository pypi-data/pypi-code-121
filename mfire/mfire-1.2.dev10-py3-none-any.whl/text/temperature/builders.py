from mfire.settings import get_logger
from mfire.text.base import BaseBuilder
from mfire.text.common import (
    SynonymeBuilder,
    ZoneBuilder,
    PeriodBuilder,
    TemplateBuilder,
)

# from mfire.text.template import read_file
# from mfire.settings import TEMPLATES_FILENAMES
# from mfire.text.temperature import TemperatureSelector


# Logging
LOGGER = get_logger(name="temperature_builder.mod", bind="temperature_builder")


# TEMPE_TPL_RETRIEVER = read_file(TEMPLATES_FILENAMES["fr"]["synthesis"]["temperature"])


class TemperatureBuilder(
    TemplateBuilder, SynonymeBuilder, PeriodBuilder, ZoneBuilder, BaseBuilder,
):
    """ Builder spécifique pour gérer les textes de sythèse pour la température

    Args:
        Objet qui est capable de trouver et de et de fournir un modèle
        correspondant à self.reducer.

    Inheritance:
        BaseBuilder
        SynonymeBuilder
        ZoneBuilder
        PeriodBuilder
    """

    def process(self) -> str:
        pass

    def compute(self, reduction: dict) -> None:
        self.reset()
        self.reduction = reduction
        # selector = TemperatureSelector()
        # key = self.find_template_key(selector)
        # self.retrieve_template(key, TEMPE_TPL_RETRIEVER)
        self.process()
        self.build_period()
        self.build_zone()
        self.find_synonyme()
        self._text = self._text.capitalize()
