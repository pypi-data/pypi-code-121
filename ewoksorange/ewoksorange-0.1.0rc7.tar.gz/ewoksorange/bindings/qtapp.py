import gc
import sys
import time
import signal
import logging
from typing import Optional
from contextlib import contextmanager
from AnyQt import QtCore
from AnyQt.QtWidgets import QApplication


_APP = None
_OLD_HANDLERS = None

logger = logging.getLogger(__name__)


def ensure_qtapp() -> Optional[QApplication]:
    """Create a Qt application without event loop when no application is running"""
    global _APP
    if _APP is not None:
        return

    # GUI application
    _APP = QApplication.instance()
    if _APP is not None:
        return _APP

    # Install signal, exception and Qt message handlers
    _install_handlers()

    # Application without event loop (_APP.exec() is not called)
    _APP = QApplication([])
    return _APP


def _install_handlers():
    """Install signal, exception and Qt message handlers"""
    global _OLD_HANDLERS
    if _OLD_HANDLERS is not None:
        return
    # Allow termination with CTRL + C
    old_signal = signal.signal(signal.SIGINT, signal.SIG_DFL)

    # Redirect Qt logs
    old_qtmsg_handler = QtCore.qInstallMessageHandler(qt_message_handler)

    # Log unhandled exceptions, otherwise qFatal will be called
    old_ex_handler = sys.excepthook
    sys.excepthook = absorb_nonbase_exception

    _OLD_HANDLERS = old_signal, old_qtmsg_handler, old_ex_handler


def _remove_handlers():
    """Undo _install_handlers"""
    global _OLD_HANDLERS
    if _OLD_HANDLERS is None:
        return

    old_signal, old_qtmsg_handler, old_ex_handler = _OLD_HANDLERS

    signal.signal(signal.SIGINT, old_signal)

    QtCore.qInstallMessageHandler(old_qtmsg_handler)

    sys.excepthook = old_ex_handler

    _OLD_HANDLERS = None


def close_qtapp():
    """Close the Qt application created by ensure_qtapp"""
    global _APP
    if _APP is None:
        return
    _APP.processEvents()
    while gc.collect():
        _APP.processEvents()
    _APP.exit()
    _APP = None
    _remove_handlers()


@contextmanager
def qtapp_context():
    qtapp = ensure_qtapp()
    try:
        yield qtapp
    finally:
        close_qtapp()


def get_qtapp() -> Optional[QApplication]:
    return QApplication.instance()


def process_qtapp_events():
    """Process all pending Qt events when a Qt event loop is running"""
    global _APP
    if _APP is None:
        return
    while _APP.hasPendingEvents():
        _APP.processEvents()


class QtEvent:
    """Event that also works for Qt applications with an event loop
    that need to run manually"""

    def __init__(self):
        self.__flag = False

    def wait(self, timeout=None):
        """Processes events associated to the calling thread while waiting"""
        global _APP
        if timeout is not None:
            t0 = time.time()
        while not self.__flag:
            if _APP is None:
                time.sleep(0.1)
            else:
                _APP.processEvents(QtCore.QEventLoop.AllEvents, 100)
            if timeout is not None:
                secs = time.time() - t0
                if secs <= 0:
                    return False
        return True

    def set(self):  # noqa A003
        self.__flag = True

    def clear(self):
        self.__flag = False


def get_all_qtwidgets():
    app = get_qtapp()
    if app is None:
        return list()

    sapp = str(type(app))
    if "PyQt5" in sapp:
        from PyQt5.sip import ispycreated as createdByPython  # noqa
    elif "PySide2" in sapp:
        from PySide2.shiboken2 import createdByPython  # noqa
    else:
        raise RuntimeError(f"'{sapp}' not supported")

    return [widget for widget in app.allWidgets() if createdByPython(widget)]


def qt_message_handler(level, context, message):
    if level == QtCore.QtInfoMsg:
        log = logger.info
    elif level == QtCore.QtWarningMsg:
        log = logger.warning
    elif level == QtCore.QtCriticalMsg:
        log = logger.error
    elif level == QtCore.QtFatalMsg:
        log = logger.fatal
    else:
        log = logger.debug
    log(
        "line: %d, func: %s(), file: %s\nQT MESSAGE: %s\n",
        context.line,
        context.function,
        context.file,
        message,
    )


def absorb_nonbase_exception(exc_type, exc_value, exc_traceback):
    if not issubclass(exc_type, Exception):
        sys.__excepthook__(exc_type, exc_value, exc_traceback)
        return

    logger.error("Uncaught exception", exc_info=(exc_type, exc_value, exc_traceback))
