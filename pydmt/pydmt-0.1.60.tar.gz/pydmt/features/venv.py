import os

from pydmt.api.feature import Feature
from pydmt.builders.venv import BuilderVenv
from pydmt.core.pydmt import PyDMT


class FeatureVenv(Feature):
    def setup(self, pydmt: PyDMT) -> None:
        if os.path.isfile("config/python.py"):
            pydmt.add_builder(BuilderVenv(
                source="config/python.py",
                target="out/python.stamp",
            ))
