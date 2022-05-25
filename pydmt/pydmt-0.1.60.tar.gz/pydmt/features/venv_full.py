import os

from pydmt.api.feature import Feature
from pydmt.builders.venv_full import BuilderVenvFull
from pydmt.core.pydmt import PyDMT


class FeatureVenv(Feature):
    def setup(self, pydmt: PyDMT) -> None:
        if not os.path.isfile("config/python.py"):
            return
        pydmt.add_builder(BuilderVenvFull())
