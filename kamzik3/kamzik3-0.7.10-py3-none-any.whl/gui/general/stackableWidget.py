from PyQt5.QtWidgets import QWidget

from kamzik3.gui.deviceDebugWidget import DeviceDebugWidget
from kamzik3.snippets.snippetsWidgets import show_centralized_top


class StackableWidget(QWidget):
    debug_widget = None

    def enterEvent(self, event):
        self.setStyleSheet("QWidget#widget_holder {background:#f1f1f1}")
        if self.model_image is not None:
            self.sigShowModel.emit(self.model_image)
        QWidget.enterEvent(self, event)

    def leaveEvent(self, event):
        self.setStyleSheet("QWidget#widget_holder {background:transparent}")
        if self.model_image is not None:
            self.sigHideModel.emit(self.model_image)
        QWidget.leaveEvent(self, event)

    def show_debug_widget(self):
        if self.debug_widget is None:
            self.debug_widget = DeviceDebugWidget(self.device)

        show_centralized_top(self.debug_widget)

        def close_event(event):
            self.debug_widget.close()
            self.debug_widget.setParent(None)
            self.debug_widget.deleteLater()
            self.debug_widget = None
            event.accept()

        self.debug_widget.closeEvent = close_event
