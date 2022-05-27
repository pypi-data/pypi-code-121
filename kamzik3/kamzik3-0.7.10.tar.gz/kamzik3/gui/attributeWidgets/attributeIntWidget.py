from typing import Any

from kamzik3.gui.attributeWidgets.attributeFloatWidget import AttributeFloatWidget


class AttributeIntWidget(AttributeFloatWidget):
    attribute_type_cast: Any = int

    def _set_input_widget(self):
        super()._set_input_widget()
        self.input_widget.setDecimals(0)
