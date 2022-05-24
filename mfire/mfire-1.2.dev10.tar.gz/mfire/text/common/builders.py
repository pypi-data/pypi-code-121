from mfire.settings import get_logger
from mfire.text.base import BaseBuilder


# Logging
LOGGER = get_logger(name="common_builder.mod", bind="common_builder")


class SynonymeBuilder(BaseBuilder):
    """ SynonymeBuilder qui doit construire les synonyme du texte de synthèse
    """

    def find_synonyme(self):
        self._text = ""

    def compute(self):

        self.find_synonyme()


class PeriodBuilder(BaseBuilder):
    """ PeriodBuilder qui doit construire les périodes du texte de synthèse
    """

    def build_period(self):
        self._text = ""

    def compute(self):

        self.build_period()


class ZoneBuilder(BaseBuilder):
    """ ZoneBuilder qui doit construire les zones du texte de synthèse
    """

    def build_zone(self):
        self._text = ""

    def compute(self):

        self.build_zone()
