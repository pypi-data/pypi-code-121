from AnyQt.QtCore import pyqtSignal as Signal
from AnyQt.QtCore import QObject

from ewokscore.progress import BasePercentageProgress

__all__ = ["QProgress"]


class QProgress(QObject, BasePercentageProgress):
    """
    Progress associated to a QObject.
    This is connected to the Orange :class:'ProgressBar' from classes:
    * :class:`OWEwoksWidgetOneThread`
    * :class:`OWEwoksWidgetWithTaskStack`
    """

    sigProgressChanged = Signal(int)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def _update(self):
        self.sigProgressChanged.emit(self._progress)
