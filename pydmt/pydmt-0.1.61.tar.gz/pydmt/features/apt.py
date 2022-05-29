from pydmt.api.feature import Feature
from pydmt.builders.apt import BuilderApt
from pydmt.core.pydmt import PyDMT


class FeatureApt(Feature):
    def __init__(
        self,
    ):
        self.packages = None
        # pylint: disable=import-outside-toplevel
        try:
            import config.deps
            self.packages = config.deps.packages
        except ModuleNotFoundError:
            pass

    def setup(self, pydmt: PyDMT) -> None:
        if self.packages is not None:
            pydmt.add_builder(BuilderApt(
                source="config/deps.py",
                target="out/deps.stamp",
                packages=self.packages
            ))
