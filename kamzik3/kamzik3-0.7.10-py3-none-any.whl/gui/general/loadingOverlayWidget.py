from PyQt5.QtCore import Qt, QPoint, QSize
from PyQt5.QtGui import QPainter, QColor, QMovie
from PyQt5.QtWidgets import QWidget

from kamzik3.gui.templates.loadingOverlayTemplate import Ui_Form


class LoadingOverlayWidget(QWidget, Ui_Form):
    overlayed_widget = None
    cancel_function = None
    canceled = False

    def __init__(self, parent):
        QWidget.__init__(self, parent)
        self.setupUi(self)

        movie = QMovie(":/icons/icons/loading.gif")
        movie.setScaledSize(QSize(128, 128))
        movie.start()
        self.image_loading.setMovie(movie)
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.hide()

    def paintEvent(self, QPaintEvent):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setPen(Qt.NoPen)
        painter.setBrush(QColor(255, 255, 255, 200))
        painter.drawRect(0, 0, self.width(), self.height())

    def set_over(self, widget, message="Loading...", cancel_function=None):
        if cancel_function is not None:
            self.button_cancel.show()
            self.button_cancel.setEnabled(True)
        else:
            self.button_cancel.hide()
        self.canceled = False
        self.overlayed_widget = widget
        self.cancel_function = cancel_function
        self.label_loading.setText(message)
        self.show()
        self.resize(widget.rect().width() + 1, widget.rect().height() + 1)

    def cancel(self):
        self.button_cancel.setEnabled(False)
        if callable(self.cancel_function):
            self.cancel_function()
        self.canceled = True

    def hide(self):
        self.overlayed_widget = None
        QWidget.hide(self)

    def set_overlay_size(self):
        if self.overlayed_widget is not None:
            widget_pos = self.overlayed_widget.mapToGlobal(
                self.overlayed_widget.rect().topLeft()
            )
            window_pos = self.window().mapToGlobal(self.window().rect().topLeft())
            rel_x = widget_pos.x() - window_pos.x()
            rel_y = widget_pos.y() - window_pos.y()
            self.setGeometry(self.overlayed_widget.geometry())
            self.move(QPoint(rel_x, rel_y))

    def resizeEvent(self, QResizeEvent):
        self.set_overlay_size()
        QWidget.resizeEvent(self, QResizeEvent)

    def slot_set_progress(self, value):
        self.label_progress.setText("{}%".format(round(value, 1)))
