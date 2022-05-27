from PyQt5.QtCore import pyqtSlot, pyqtSignal
from PyQt5.QtWidgets import QWidget
from typing import Any

from kamzik3.constants import *
from kamzik3.devices.attribute import Attribute
from kamzik3.gui.attributeWidgets.attributeUnitWidget import AttributeUnitWidget


class AttributeWidget(QWidget):
    input_widget = None
    unit_widget = None
    unit = None
    font_color = "black"
    background_color = "white"
    attribute = None
    attribute_type_cast: Any = str
    sig_unit_changed = pyqtSignal("QString", "QString")

    def __init__(self, attribute, config=None, parent=None):
        assert isinstance(attribute, Attribute)
        self.attribute = attribute
        self.config = config
        if self.config is None:
            self.config = {}
        QWidget.__init__(self, parent=parent)
        self.setupUi()

    def _set_unit_widget(self):
        self.unit_widget = AttributeUnitWidget(self.attribute)
        self.unit_widget.sig_unit_changed.connect(self.set_unit)

    def set_tooltip(self, value=None):
        tooltip_value = self.attribute[DESCRIPTION]
        if tooltip_value is not None:
            tooltip_value += "\n" + value
        else:
            tooltip_value = value

        if tooltip_value is not None:
            self.input_widget.setToolTip(tooltip_value)

    def update_value(self):
        self.set_value(self.attribute.value())

    @pyqtSlot("PyQt_PyObject")
    def _set_input_widget(self):
        raise NotImplementedError("Has to be implemented")

    def get_attribute_value(self):
        raise NotImplementedError("Has to be implemented")

    def get_widget_value(self):
        raise NotImplementedError("Has to be implemented")

    def set_value(self, value):
        raise NotImplementedError("Has to be implemented")

    @pyqtSlot("QString")
    def set_unit(self, unit=None, reset=False):
        return

    def get_unit(self):
        return self.unit

    def setDisabled(self, bool):
        self.input_widget.setDisabled(bool)
        super().setDisabled(bool)

    def setupUi(self, parent=None):
        self.unit = self.attribute[UNIT]
        self._set_input_widget()
        self._set_unit_widget()

        if self.config is not None and self.config.get("unit") is not None:
            # self.unit_widget.current_unit can be different from config.get("unit")
            # if that unit is not in the possible units defined by the limits
            # see snippetsUnits.get_attribute_unit_range
            self.unit_widget.set_unit(self.config.get("unit"))

        if self.attribute[VALUE] is not None:
            widget_unit = self.unit_widget.current_unit
            if widget_unit is not None:
                self.set_value(self.attribute.value().to(widget_unit))
                self.unit = widget_unit
            else:
                self.set_value(self.attribute.value())

        self.input_widget.__dict__["update_value"] = self.update_value

    def close(self):
        if self.input_widget is not None:
            self.input_widget.setParent(None)
            del self.input_widget
        if self.unit_widget is not None:
            self.unit_widget.close()

        self.attribute = None
        self.config = None
        return super().close()
