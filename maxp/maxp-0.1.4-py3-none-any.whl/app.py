# Standard
import os
import sys
import importlib

# Qt
from PySide2.QtWidgets import QApplication

# Package
from bettermaxtools import maxhwnd  # noqa: E402


def launch(moduleName: str, windowName: str) -> None:
    """Launch the `module` with the given `window` class.

    Args:
        moduleName (str): The name of the module to access.
        windowName (str): The name of the window class to launch.
    """
    module = importlib.import_module(f'bettermaxtools.tools.{moduleName}')
    importlib.reload(module)
    windowClass = getattr(module, windowName)

    if maxhwnd is None:
        app = QApplication(sys.argv)

    w = windowClass(parent=maxhwnd)
    w.show()

    if maxhwnd is None:
        sys.exit(app.exec_())


if __name__ == "__main__":
    if len(sys.argv) > 1:
        moduleName = sys.argv[1]
        windowName = sys.argv[2]
    else:
        moduleName = 'gameexporter'
        windowName = 'GameExporterWindow'

    launch(moduleName, windowName)
