"""
This module imports the right Qt bindings, which are compatible 
with the version of the Qt framework OVITO has been built against.
"""

import os

# Value of the OVITO_QT_MAJOR_VERSION CMake variable at build time:
_ovito_qt_version = 'Qt6'

# The following condition depends on the value of the OVITO_QT_MAJOR_VERSION CMake variable,
# which was specified at configuration time when building the OVITO Python module.
# If OVITO was built against Qt6, we should import the PySide6 bindings; otherwise, when using the old Qt5 
# framework, we should import the matching PySide2 bindings.
if _ovito_qt_version == 'Qt6':
    
    from PySide6 import QtCore, QtGui, QtWidgets, QtNetwork, QtXml
    
    # The QtOpenGLWidgets module is not included in the embedded PySide6 installation of OVITO Pro 3.7,
    # but it should be loaded when using the PyPI version of PySide6.
    try:
        from PySide6 import QtOpenGLWidgets
        from PySide6 import QtOpenGL
    except ImportError: pass

    import shiboken6 as shiboken

    # Try to tell other Python modules (e.g. matplotlib) to use the same Qt bindings as OVITO.
    # Typically, this is done through the environment variable QT_API.
    if not 'QT_API' in os.environ:
        os.environ['QT_API'] = 'pyside6'

    # Map DeprecationWarning methods
    QtCore.QCoreApplication.exec_ = QtCore.QCoreApplication.exec
    QtCore.QEventLoop.exec_ = QtCore.QEventLoop.exec
    QtCore.QThread.exec_ = QtCore.QThread.exec

elif _ovito_qt_version == 'Qt5':
    
    from PySide2 import QtCore, QtGui, QtWidgets, QtNetwork, QtXml
    import shiboken2 as shiboken 

    # Try to tell other Python modules (e.g. matplotlib) to use the same Qt bindings as OVITO.
    # Typically, this is done through the environment variable QT_API.
    if not 'QT_API' in os.environ:
        os.environ['QT_API'] = 'pyside2'

else:
    assert(False) # CMake variable OVITO_QT_MAJOR_VERSION is neither "Qt5" nor "Qt6".

del _ovito_qt_version
