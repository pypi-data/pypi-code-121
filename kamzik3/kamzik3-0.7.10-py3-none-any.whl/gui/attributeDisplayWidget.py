from typing import Optional

import numpy as np
from PyQt5.QtCore import pyqtSlot, Qt
from PyQt5.QtWidgets import QLabel, QWidget, QHBoxLayout

from kamzik3 import units
from kamzik3.constants import *
from kamzik3.gui.attributeWidgets.attributeBoolWidget import AttributeBoolWidget
from kamzik3.gui.attributeWidgets.attributeComboboxWidget import AttributeComboxWidget
from kamzik3.gui.attributeWidgets.attributeFloatWidget import AttributeFloatWidget
from kamzik3.gui.attributeWidgets.attributeImageWidget import AttributeImageWidget
from kamzik3.gui.attributeWidgets.attributeIntWidget import AttributeIntWidget
from kamzik3.gui.attributeWidgets.attributeStringWidget import AttributeStringWidget
from kamzik3.gui.attributeWidgets.attributeTextWidget import AttributeTextWidget
from kamzik3.gui.attributeWidgets.attributeUnsignedIntWidget import (
    AttributeUnsignedIntWidget,
)


class AttributeDisplayWidget(QWidget):
    attribute_widget = None
    label_widget = None
    input_widget = None
    unit_widget = None

    def __init__(self, title, attribute, config=None, parent=None):
        self.attribute = attribute
        self.config = config
        self.title = title
        self.name: Optional[str] = None
        QWidget.__init__(self, parent=parent)
        self.setupUi()

    # pylint: disable=unused-argument
    def setupUi(self, parent=None):
        if self.attribute_widget is not None:
            self.attribute_widget.attribute = self.attribute
            return

        self.label_widget = QLabel("{}:".format(self.title))
        if self.attribute[TYPE] == TYPE_LIST:
            if TYPE_LIST_VALUES in self.attribute:
                self.attribute_widget = AttributeComboxWidget(
                    self.attribute, self.config
                )
                self.attribute_widget.input_widget.activated.connect(self.on_value_set)
            else:
                self.attribute_widget = AttributeStringWidget(
                    self.attribute, self.config
                )
                self.attribute_widget.input_widget.returnPressed.connect(
                    lambda attribute=self.attribute_widget.input_widget: self.on_value_set(
                        list(attribute.text())
                    )
                )
        elif self.attribute[TYPE] == TYPE_ARRAY:
            if self.attribute.get(DISPLAY) == IMAGE:
                self.attribute_widget = AttributeImageWidget(
                    self.attribute, self.config
                )
            else:
                self.attribute_widget = AttributeTextWidget(self.attribute, self.config)
        else:
            np_type = np.dtype(self.attribute[TYPE])
            if np_type == np.str:
                self.attribute_widget = AttributeStringWidget(
                    self.attribute, self.config
                )
                self.attribute_widget.input_widget.returnPressed.connect(
                    lambda attribute=self.attribute_widget.input_widget: self.on_value_set(
                        attribute.text()
                    )
                )
            elif np_type in (np.uint8, np.uint16, np.uint32, np.uint64):
                self.attribute_widget = AttributeUnsignedIntWidget(
                    self.attribute, self.config
                )
                self.attribute_widget.input_widget.returnPressed.connect(
                    self.on_value_set
                )
            elif np_type in (np.int8, np.int16, np.int32, np.int64):
                self.attribute_widget = AttributeIntWidget(self.attribute, self.config)
                self.attribute_widget.input_widget.returnPressed.connect(
                    self.on_value_set
                )
            elif np_type in (np.float16, np.float32, np.float64):
                self.attribute_widget = AttributeFloatWidget(
                    self.attribute, self.config
                )
                self.attribute_widget.input_widget.returnPressed.connect(
                    self.on_value_set
                )
            elif np_type == np.bool:
                self.attribute_widget = AttributeBoolWidget(self.attribute, self.config)
                self.attribute_widget.input_widget.clicked.connect(self.on_value_set)
            else:
                self.logger.info(
                    f"{self.attribute_device_key}: TYPE={self.attribute[TYPE]}, "
                    "assuming this can be represented by a string"
                )
                self.attribute_widget = AttributeTextWidget(self.attribute, self.config)

        if self.config is not None and self.config.get("label_width"):
            self.label_widget.setMinimumWidth(self.config.get("label_width"))
            self.label_widget.setAlignment(
                Qt.AlignRight | Qt.AlignTrailing | Qt.AlignVCenter
            )

        self.input_widget = self.attribute_widget.input_widget
        self.unit_widget = self.attribute_widget.unit_widget

        if self.attribute.get(DESCRIPTION) is not None:
            self.label_widget.setToolTip(self.attribute[DESCRIPTION])

        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.label_widget)
        layout.addWidget(self.input_widget)
        layout.addWidget(self.unit_widget)

    def get_attribute_value(self):
        return self.attribute_widget.get_attribute_value()

    def get_widget_value(self):
        return self.attribute_widget.get_widget_value()

    def set_value(self, value):
        return self.attribute_widget.set_value(value)

    def get_minimum(self):
        return self.attribute_widget.get_minimum()

    def get_maximum(self):
        return self.attribute_widget.get_maximum()

    def set_minimum(self, value):
        return self.attribute_widget.set_minimum(value)

    def set_maximum(self, value):
        return self.attribute_widget.set_maximum(value)

    def on_value_set(self, value):
        self.attribute[VALUE] = self.attribute_widget.attribute_type_cast(value)

    def _check_value(self, new_value):
        min_value, max_value = self.attribute.minimum(), self.attribute.maximum()
        if max_value is not None and new_value > max_value:
            self.logger.info(
                f"Can't set value {new_value}, larger than the upper limit"
            )
            new_value = max_value
        elif min_value is not None and new_value < min_value:
            self.logger.info(
                f"Can't set value {new_value}, smaller than the lower limit"
            )
            new_value = min_value
        return new_value

    def __add__(self, value):
        assert isinstance(value, units.Quantity)
        current_value = self.attribute.value().to(self.get_unit())
        new_value = current_value + value
        new_value = self._check_value(new_value)
        self.on_value_set(new_value)
        return self

    def __sub__(self, value):
        assert isinstance(value, units.Quantity)
        current_value = self.attribute.value().to(self.get_unit())
        new_value = current_value - value
        new_value = self._check_value(new_value)
        self.on_value_set(new_value)
        return self

    @pyqtSlot("QString")
    # pylint: disable=unused-argument
    def set_unit(self, unit=None, reset=False):
        self.unit_widget.set_unit(unit)

    @pyqtSlot("QString")
    def get_unit(self):
        return self.attribute_widget.unit

    def close(self):
        if self.label_widget is not None:
            self.label_widget.setParent(None)
        if self.attribute_widget is not None:
            self.attribute_widget.close()
            self.attribute_widget.setParent(None)
        self.attribute_widget.deleteLater()
        self.label_widget.deleteLater()
        self.attribute = None
        self.config = None
        return QWidget(self)
