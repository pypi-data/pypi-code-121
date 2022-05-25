import os

from pydmt.api.feature import Feature
from pydmt.builders.yaml import BuilderYaml
from pydmt.core.pydmt import PyDMT


class FeatureYaml(Feature):
    def __init__(
        self,
        yaml_folder: str = "yaml",
        validation_folder: str = "out"
    ):
        self.yaml_folder = yaml_folder
        self.validation_folder = validation_folder

    def setup(self, pydmt: PyDMT) -> None:
        if not os.path.isdir(self.yaml_folder):
            return
        for root, _, filenames in os.walk(self.yaml_folder):
            for filename in filenames:
                source = os.path.join(root, filename)
                target_base, ext = os.path.splitext(source)
                if ext == ".yaml":
                    target = os.sep.join([self.validation_folder, target_base, source + ".stamp"])
                    builder = BuilderYaml(
                        source=source,
                        target=target,
                    )
                    pydmt.add_builder(builder)
