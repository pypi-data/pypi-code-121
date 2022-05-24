import os

from pydmt.api.feature import Feature
from pydmt.builders.mako import BuilderMako
from pydmt.core.pydmt import PyDMT
from pydmt.utils.filesystem import files_under_folder


class FeatureMako(Feature):
    def __init__(
        self,
        data=None,
        templates_folder: str = "templates",
        config_folder: str = "config",
        snipplet_folder: str = "snipplets",
    ):
        self.data = data
        self.templates_folder = templates_folder
        self.config_folder = config_folder
        self.snipplet_folder = snipplet_folder

    def setup(self, pydmt: PyDMT) -> None:
        if not os.path.isdir(self.templates_folder):
            return
        for root, _, filenames in os.walk(self.templates_folder):
            for filename in filenames:
                source = os.path.join(root, filename)
                target_base, ext = os.path.splitext(source)
                if ext == '.mako':
                    target = os.sep.join(target_base.split(os.sep)[1:])
                    builder = BuilderMako(
                        source=source,
                        target=target,
                        data=self.data,
                        config_files=files_under_folder(self.config_folder, suffix=".py"),
                        snipplet_files=files_under_folder(self.snipplet_folder, suffix=".mako"),
                    )
                    pydmt.add_builder(builder)
