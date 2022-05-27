from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QCheckBox, QSizePolicy
from typing import Any

from kamzik3.constants import *
from kamzik3.gui.attributeWidgets.attributeWidget import AttributeWidget


class AttributeBoolWidget(AttributeWidget):
    attribute_type_cast: Any = bool

    def _set_input_widget(self):
        self.input_widget = QCheckBox()
        self.input_widget.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.input_widget.setStyleSheet(
            "QCheckBox:checked {color: green} QCheckBox:unchecked {color: red}"
        )
        self.input_widget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.input_widget.clicked.connect(self.clicked)
        if self.attribute[READONLY]:
            self.input_widget.setAttribute(Qt.WA_TransparentForMouseEvents)
            self.input_widget.setFocusPolicy(Qt.NoFocus)

    def clicked(self, flag):
        self.input_widget.setText("On" if flag else "Off")

    def set_value(self, value):
        if value is None:
            return
        self.input_widget.blockSignals(True)
        self.input_widget.setText("On" if value else "Off")
        self.input_widget.setChecked(value)
        self.input_widget.blockSignals(False)

    def get_attribute_value(self):
        return self.input_widget.isChecked()

    def get_widget_value(self):
        return self.input_widget.isChecked()
