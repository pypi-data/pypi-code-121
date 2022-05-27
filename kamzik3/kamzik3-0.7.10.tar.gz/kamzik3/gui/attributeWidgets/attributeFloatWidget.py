import pint
from math import inf

from PyQt5.QtCore import pyqtSlot
from PyQt5.QtWidgets import QSizePolicy, QAbstractSpinBox
from pint import UndefinedUnitError, DimensionalityError
from typing import Any

from kamzik3 import units
from kamzik3.constants import *
from kamzik3.gui.attributeWidgets.attributeWidget import AttributeWidget
from kamzik3.snippets.snippetsUnits import get_decimals_diff
from kamzik3.snippets.snippetsWidgets import CustomDoubleSpinBox


class AttributeFloatWidget(AttributeWidget):
    attribute_type_cast: Any = float

    def _set_input_widget(self):
        self.input_widget = CustomDoubleSpinBox()
        self.input_widget.setDecimals(
            self.config.get("max-decimals", self.attribute[DECIMALS])
        )
        self.input_widget.valueChanged.connect(self.on_numerical_value_set)
        self.input_widget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.input_widget.setMinimum(-inf)
        self.input_widget.setMaximum(inf)

        if self.attribute[READONLY]:
            self.input_widget.setReadOnly(True)
            self.input_widget.setButtonSymbols(QAbstractSpinBox.NoButtons)
        else:
            self.background_color = "#e6ffd9"
            self.input_widget.setStyleSheet(
                ".CustomDoubleSpinBox, .CustomSpinBox {{background:{}; color:{}}}".format(
                    self.background_color, self.font_color
                )
            )
        value_min = value_max = "Not set"
        if self.attribute[MIN] is not None:
            value_min = self.attribute.minimum()

        if self.attribute[MAX] is not None:
            value_max = self.attribute.maximum()
        # ~ is a pint format specification
        self.set_tooltip("Min: {:~}\nMax: {:~}".format(value_min, value_max))  # type: ignore

    def set_value(self, value):
        if value is None or value == "None":
            self.input_widget.lineEdit().setText("None")
            return

        assert isinstance(value, units.Quantity)

        try:
            set_value = value.to(self.unit)
        except (AttributeError, pint.DefinitionSyntaxError):
            set_value = units.Quantity(value)
        self.on_numerical_value_set(set_value.m)
        self.input_widget.setValue(set_value.m)

    def get_attribute_value(self):
        try:
            return units.Quantity(self.input_widget.value(), self.unit).to(
                self.attribute[UNIT]
            )
        except (UndefinedUnitError, AttributeError):
            return units.Quantity(self.input_widget.value())

    def get_widget_value(self):
        try:
            return units.Quantity(self.input_widget.value(), self.unit)
        except (UndefinedUnitError, AttributeError):
            return units.Quantity(self.input_widget.value())

    def get_minimum(self):
        try:
            return units.Quantity(self.input_widget.minimum(), self.unit)
        except (UndefinedUnitError, AttributeError):
            return units.Quantity(self.input_widget.minimum())

    def get_maximum(self):
        try:
            return units.Quantity(self.input_widget.maximum(), self.unit)
        except (UndefinedUnitError, AttributeError):
            return units.Quantity(self.input_widget.maximum())

    def set_minimum(self, value):
        # ~ is a pint format specification
        assert isinstance(value, units.Quantity)
        self.set_tooltip(
            "Min: {:~}\nMax: {:~}".format(  # type: ignore
                self.attribute.minimum(), self.attribute.maximum()
            )
        )

    def set_maximum(self, value):
        # ~ is a pint format specification
        assert isinstance(value, units.Quantity)
        self.set_tooltip(
            "Min: {:~}\nMax: {:~}".format(  # type: ignore
                self.attribute.minimum(), self.attribute.maximum()
            )
        )

    def on_numerical_value_set(self, value):
        current_font_color = self.font_color
        try:
            min_value, max_value = (
                self.attribute.minimum().to(self.unit).m,
                self.attribute.maximum().to(self.unit).m,
            )
        except pint.DefinitionSyntaxError:
            min_value, max_value = (
                self.attribute.minimum(),
                self.attribute.maximum(),
            )
        if min_value == -inf or max_value == inf:
            if value <= min_value or value >= max_value:
                self.font_color = "red"
            else:
                self.font_color = "black"
        else:
            try:
                value_in_percent = ((value - min_value) * 100.0) / (
                    max_value - min_value
                )
            except ZeroDivisionError:
                value_in_percent = 50

            if value_in_percent >= 100 or value_in_percent <= 0:
                self.font_color = "red"
            elif value_in_percent <= 20:
                self.font_color = "purple"
            elif value_in_percent <= 80:
                self.font_color = "black"
            else:
                self.font_color = "blue"

        if current_font_color != self.font_color:
            self.input_widget.setStyleSheet(
                ".CustomDoubleSpinBox, .CustomSpinBox {{background:{}; color:{}}}".format(
                    self.background_color, self.font_color
                )
            )

    @pyqtSlot("QString")
    def set_unit(self, unit=None, reset=False):
        # Set widget to new unit
        old_unit, new_unit = self.unit, unit
        old_min, old_max = self.attribute.minimum(), self.attribute.maximum()
        self.unit = unit

        if unit is None:
            return
        try:
            new_value = units.Quantity(self.input_widget.value(), old_unit).to(new_unit)
        except AttributeError:
            return
        except DimensionalityError:
            old_unit = new_unit
            new_value = units.Quantity(self.input_widget.value(), new_unit)

        min_value = max_value = None
        # Recalculate minimum and maximum value to new unit
        try:
            min_value = old_min.to(new_unit)
        except KeyError:
            pass  # Attribute has no minimum
        try:
            max_value = old_max.to(new_unit)
        except KeyError:
            pass  # Attribute has no maximum

        self.set_tooltip("Min: {}\nMax: {}".format(min_value, max_value))

        try:
            if reset:
                decimals = self.config.get("max-decimals", self.attribute[DECIMALS])
                self.input_widget.setDecimals(decimals)
            else:
                decimals_diff = get_decimals_diff(old_unit, new_unit)
                decimals = self.config.get(
                    "max-decimals", self.input_widget.decimals() - decimals_diff
                )
                self.input_widget.setDecimals(decimals)
        except (KeyError, AttributeError):
            pass  # Attribute has no decimals

        # Update displayed value
        self.set_value(new_value)
        self.sig_unit_changed.emit(old_unit, new_unit)
