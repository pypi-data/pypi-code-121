import os

from pydmt.api.feature import Feature
from pydmt.builders.reqs import BuilderReqs
from pydmt.core.pydmt import PyDMT

SOURCE_FILE = "config/python.py"
TARGET_FILE = "out/reqs.stamp"


class FeatureReqs(Feature):
    def setup(self, pydmt: PyDMT) -> None:
        if not os.path.isfile(SOURCE_FILE):
            return
        builder = BuilderReqs(
            source=SOURCE_FILE,
            target=TARGET_FILE,
        )
        pydmt.add_builder(builder)
