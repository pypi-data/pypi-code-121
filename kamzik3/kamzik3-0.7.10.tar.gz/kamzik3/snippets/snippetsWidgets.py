import os
import sys

from PyQt5 import QtCore
from PyQt5.QtCore import pyqtSignal, Qt
from PyQt5.QtWidgets import (
    QMessageBox,
    QInputDialog,
    QLineEdit,
    QDesktopWidget,
    QAbstractSpinBox,
    QSpinBox,
    QDoubleSpinBox,
    QApplication,
    QPlainTextEdit,
)


def clear_layout(self, layout):
    """
    Clear given QLayout of all widgets.

    Perform close method on every widget.

    :param self: QWidget
    :param layout: QLayout
    """
    if layout is not None:
        while layout.count():
            item = layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.close()
                widget.deleteLater()
            else:
                clear_layout(self, item.layout())


def show_error_message(message, parent=None):
    """
    Show error message to user.

    :param message: string
    :param parent: QWidget
    """
    error_message = QMessageBox(parent)
    error_message.setIcon(QMessageBox.Critical)
    error_message.setText("{}".format(message))
    error_message.open()


def show_info_message(message, parent=None):
    """
    Show error message to user.

    :param message: string
    :param parent: QWidget
    """
    error_message = QMessageBox(parent)
    error_message.setIcon(QMessageBox.Information)
    error_message.setText("{}".format(message))
    error_message.open()


def show_question_dialog(question, title="", parent=None, cancel=False):
    """
    Show dialog with two options. Yes or No.

    Return True or False.

    :param question:
    :param title:
    :param parent:
    :return: bool
    """
    if cancel:
        buttons = QMessageBox.Yes | QMessageBox.No | QMessageBox.Cancel
    else:
        buttons = QMessageBox.Yes | QMessageBox.No
    answer = QMessageBox.question(
        parent, title, question, buttons=buttons, defaultButton=QMessageBox.No
    )
    if answer in (QMessageBox.Yes, QMessageBox.Cancel):
        return answer
    else:
        return False


def show_prompt_dialog(prompt, title="", parent=None):
    """
    Show prompt dialog to the user.

    Return user input when Enter is pressed.
    Return False if user cancelled prompt dialog.

    :param prompt: string
    :param title: string
    :param parent: QWidget
    :return: string
    """
    user_comment, answer = QInputDialog.getText(
        parent, title, prompt, QLineEdit.Normal, ""
    )

    if answer:
        return user_comment
    else:
        return False


def show_password_dialog(prompt, title="Type password", default_text="", parent=None):
    """
    Ask user for password input.

    :param prompt: str
    :param title: str
    :param default_text: str
    :param parent: QWidget
    :return: str
    """
    answer, ok = QInputDialog.getText(
        parent, title, prompt, QLineEdit.Password, default_text
    )
    if ok:
        return answer


def show_centralized_top(widget):
    """
    Show widget in center of current screen.

    Put widget on top of others.
    Make it active even if minimized.

    :param widget: QWidget
    :return: None
    """
    fg = widget.frameGeometry()
    cp = QDesktopWidget().availableGeometry().center()
    fg.moveCenter(cp)
    widget.move(fg.topLeft())
    widget.setWindowState(Qt.WindowActive)
    widget.show()
    widget.setFocus()
    widget.activateWindow()
    widget.raise_()


def init_qt_app(enable_hd_scaling=False):
    """
    Initialize QApplication with or without hd scaling factor.

    :param enable_hd_scaling: bool
    :return: QApplication
    """
    if enable_hd_scaling:
        os.environ["QT_AUTO_SCREEN_SCALE_FACTOR"] = "1"
    else:
        os.environ["QT_AUTO_SCREEN_SCALE_FACTOR"] = "0"
        os.environ["QT_SCALE_FACTOR"] = "1"
        os.environ["QT_SCREEN_SCALE_FACTOR"] = "1"

    app = QApplication(sys.argv)
    if enable_hd_scaling:
        app.setAttribute(QtCore.Qt.AA_EnableHighDpiScaling)
    return app


class SpinBoxFeatures(QAbstractSpinBox):
    returnPressed = pyqtSignal("PyQt_PyObject")

    def __init__(self, reset_on_blur=False, parent=None):
        self.reset_on_blur = reset_on_blur
        QAbstractSpinBox.__init__(self, parent)

    def update_value(self):
        return None

    def keyPressEvent(self, event):
        """
        Set value only when user hit Enter or Return.

        :param event:
        :return:
        """
        if event.key() in (Qt.Key_Enter, Qt.Key_Return):
            self.returnPressed.emit(self.value())
            self.lineEdit().deselect()
        elif event.key() == Qt.Key_Comma:
            return
        return QAbstractSpinBox.keyPressEvent(self, event)

    def wheelEvent(self, QWheelEvent):
        """
        Prevent value change by scroll mouse wheel.

        :param QWheelEvent:
        """
        return None

    def focusOutEvent(self, QFocusEvent):
        """
        Set last known value when widget is out of focus.

        :param QFocusEvent:
        :return:
        """
        if self.reset_on_blur:
            self.update_value()
            self.lineEdit().deselect()
        return QAbstractSpinBox.focusOutEvent(self, QFocusEvent)


class CustomSpinBox(QSpinBox, SpinBoxFeatures):
    returnPressed = pyqtSignal("PyQt_PyObject")

    def update_value(self):
        return None


class CustomDoubleSpinBox(QDoubleSpinBox, SpinBoxFeatures):
    returnPressed = pyqtSignal("PyQt_PyObject")

    def update_value(self):
        return None


class CustomLineEdit(QLineEdit):
    def __init__(self, reset_on_blur=False, parent=None):
        self.reset_on_blur = reset_on_blur
        QLineEdit.__init__(self, parent)

    def update_value(self):
        return None

    def focusOutEvent(self, QFocusEvent):
        """
        Set last known value when widget is out of focus.

        :param QFocusEvent:
        :return:
        """
        if self.reset_on_blur:
            self.update_value()
            # self.lineEdit().deselect()
        return QLineEdit.focusOutEvent(self, QFocusEvent)


class CustomTextEdit(QPlainTextEdit):
    def __init__(self, reset_on_blur=False, parent=None):
        self.reset_on_blur = reset_on_blur
        QPlainTextEdit.__init__(self, parent)

    def update_value(self):
        return None

    def focusOutEvent(self, QFocusEvent):
        """
        Set last known value when widget is out of focus.

        :param QFocusEvent:
        :return:
        """
        if self.reset_on_blur:
            self.update_value()
        return QPlainTextEdit.focusOutEvent(self, QFocusEvent)
