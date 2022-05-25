from .Settings import Settings
from PyQt6.QtGui import QIcon
from pathlib import Path
import platform
import os


class Enviroment:
    def __init__(self):
        self.program_dir = os.path.dirname(__file__)
        self.data_dir = self._get_data_path()

        with open(os.path.join(self.program_dir, "version.txt"), encoding="utf-8") as f:
            self.version = f.read().strip()

        self.icon = QIcon(os.path.join(self.program_dir, "Icon.svg"))

        self.settings = Settings()
        self.settings.load(os.path.join(self.data_dir, "settings.json"))

    def _get_data_path(self) -> str:
        if platform.system() == "Windows":
            return os.path.join(os.getenv("appdata"), "jdDiff")
        elif platform.system() == "Darwin":
            return os.path.join(str(Path.home()), "Library", "Application Support", "jdDiff")
        elif platform.system() == "Haiku":
            return os.path.join(str(Path.home()), "config", "settings", "jdDiff")
        else:
            if os.getenv("XDG_DATA_HOME"):
                return os.path.join(os.getenv("XDG_DATA_HOME"), "jdDiff")
            else:
                return os.path.join(str(Path.home()), ".local", "share", "jdDiff")
