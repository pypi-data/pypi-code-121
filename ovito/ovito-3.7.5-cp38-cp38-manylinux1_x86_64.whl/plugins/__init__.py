import sys, os, warnings

# This is the ovito.plugins Python package. It hosts the C++ extension modules of OVITO.

# First, check if the user did accidentally install the PyPI package via 'pip install'
# in an Anaconda environment. Warn the user if this is the case, because the PySide2/PySide6 loading 
# will probably fail due to conflicting versions of the Qt framework libraries.
#
# Using https://stackoverflow.com/questions/47608532/how-to-detect-from-within-python-whether-packages-are-managed-with-conda/47610844#47610844
# to detect Anaconda environment:
if os.path.exists(os.path.join(sys.prefix, 'conda-meta')):
    warnings.warn("Did you accidentally install the OVITO package from the PyPI repository in an Anaconda/Miniconda Python interpreter using the 'pip' command? "
        "Note that this will likely lead to conflicts with existing libraries in the Anaconda environment, and loading of the OVITO module may subsequently fail with an error related to the Qt framework. "
        "In such a case, please uninstall the OVITO pip package first by running 'pip uninstall -y ovito PySide2 PySide6' and then "
        "install the OVITO for Anaconda package using the correct command: \n\n    conda install --strict-channel-priority -c https://conda.ovito.org -c conda-forge ovito\n\n"
        "Visit https://www.ovito.org/python-downloads/ for further installation instructions. If you rather want to suppress this warning, insert the following code at the top of your Python script:\n\n"
        "  import warnings\n"
        "  warnings.filterwarnings('ignore', message='.*OVITO.*PyPI')\n",
        stacklevel=3)

# Check if an incompatible version of the Qt framework is already imported.
# If so, warn the user, because Qt5 and Qt6 cannot be used at the same time within the same application process.
_ovito_qt_version = 'Qt6'
if _ovito_qt_version == 'Qt6' and (sys.modules.get("PyQt5.QtCore") or sys.modules.get("PySide2.QtCore")):
    warnings.warn("Incompatible version of the Qt cross-platform framework detected!\nThis version of the OVITO Python module is based on Qt6 (loaded via the PySide6 bindings module), "
        "but bindings for old Qt5 are already loaded at this point (through PyQt5 or PySide2 imports preceding the import of OVITO). To avoid library version conflicts, please make sure the rest of "
        "your application uses Qt6 too instead of Qt5. "
        "\n\n"
        "To fix this warning, replace any PySide2 import statements in your script with PySide6 (or PyQt5 imports with PyQt6). "
        "In addition, it may help to set the environment variable QT_API=pyside6 to force third-party packages (e.g. matplotlib) to load Qt6 instead of Qt5. "
        "If you have any questions, please contact support@ovito.org.\n")
elif _ovito_qt_version == 'Qt5' and (sys.modules.get("PyQt6.QtCore") or sys.modules.get("PySide6.QtCore")):
    warnings.warn("Incompatible version of the Qt cross-platform framework detected! The OVITO Python module requires loading Qt5 (through the PySide2 bindings module), "
        "but some bindings for Qt6 have been loaded before (PyQt6/PySide6). To avoid ABI compatibility problems, please make sure the rest of your application "
        "also uses Qt5, not Qt6.")

# Load all the Qt bindings first before OVITO's own C++ modules get loaded.
# This ensures that the right Qt shared libraries needed by OVITO are already loaded into the process when running in a system Python interpreter.
from ovito.qt_compat import QtCore
from ovito.qt_compat import QtGui
from ovito.qt_compat import QtWidgets
from ovito.qt_compat import QtNetwork
from ovito.qt_compat import QtXml
if _ovito_qt_version == 'Qt6':
    from ovito.qt_compat import QtOpenGLWidgets
    from ovito.qt_compat import QtOpenGL

# Install an import hook that will guard against incompatible Qt imports.
# Loading both Qt 5.x and 6.x into the same process leads to runtime errors.
import importlib.abc
class ImportDenier(importlib.abc.MetaPathFinder):
    def find_spec(self, fullname, path, target=None):
        if path:
            return
        if _ovito_qt_version == "Qt6" and (fullname == "PySide2" or fullname == "PyQt5"):
            raise ImportError("The ovito package you imported ealier requires PySide6 (the Python bindings for Qt6). Importing {}, which provides bindings for the incompatible Qt5 framework, "
                "is forbidden, because it leads to library version conflicts. You should update the import statements in your script to load PySide6 instead. If you have any questions, please contact support@ovito.org. ".format(fullname))
        elif _ovito_qt_version == "Qt5" and (fullname == "PySide6" or fullname == "PyQt6"):
            raise ImportError("The ovito package you imported ealier requires PySide2 (the Python bindings for Qt5). Importing {}, which provides bindings for the incompatible Qt6 framework, "
                "is forbidden, because it leads to library version conflicts. You should update the import statements in your script to load PySide2 instead. If you have any questions, please contact support@ovito.org. ".format(fullname))
sys.meta_path.insert(0, ImportDenier())

# Load the C++ extension module containing the OVITO bindings.
import ovito.plugins.ovito_bindings
