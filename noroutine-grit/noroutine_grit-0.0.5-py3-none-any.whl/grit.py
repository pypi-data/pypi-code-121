from modulefinder import Module
from attrs import define

import importlib
import pkgutil

from .variation import VARIATION_TYPE, Variation
from .folder import Folder

@define
class Grit:

    @classmethod
    def inspect(cls, module: str) -> dict:
        grit_module = importlib.import_module(module)
        return {
            "name": grit_module.__name__,
            "folders": list(map(lambda m: m.name, pkgutil.iter_modules(grit_module.__path__))),
            "variations": Variation.find_variations_simple(grit_module)
        }

    @classmethod
    def load_with_resolutions(cls, module: str, resolutions: dict[str, str], ignore_missing: bool = False) -> dict[VARIATION_TYPE, VARIATION_TYPE]:
        """
            Import/reload dashboards module with folders using given resolutions
            returns resolved_variations

        """
        grit_module = importlib.import_module(module)
        importlib.reload(grit_module)

        resolved_variations = Variation.resolve_variations(
            grit_module,
            resolutions=resolutions,
            ignore_missing=ignore_missing
        )

        for module in pkgutil.iter_modules(grit_module.__path__):
            folder_module = importlib.import_module(
                f"{grit_module.__name__}.{module.name}")

            importlib.reload(folder_module)

            # if title is missing, assign a default one
            # TODO: make a way to create default folder without side-effect
            if not Folder.get_title(folder_module):
                Folder.set_title(folder_module, module.name)

            if not Folder.get_uid(folder_module):
                Folder.set_uid(folder_module, module.name)

        return resolved_variations

    @classmethod
    def get_folder_modules(cls, module: str) -> list[Module]:
        """
            For dashboards module returns list of dashboard folders in it
            returns list of dashboard folder modules
        """

        grit_module = importlib.import_module(module)

        folder_modules = []
        for module in pkgutil.iter_modules(grit_module.__path__):
            folder_module = importlib.import_module(
                f"{grit_module.__name__}.{module.name}")

            folder_modules.append(folder_module)

            if not Folder.get_title(folder_module):
                Folder.set_title(folder_module, module.name)

            if not Folder.get_uid(folder_module):
                Folder.set_uid(folder_module, module.name)

        return folder_modules