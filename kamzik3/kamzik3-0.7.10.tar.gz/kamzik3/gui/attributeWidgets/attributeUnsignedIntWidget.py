from kamzik3.gui.attributeWidgets.attributeFloatWidget import AttributeFloatWidget


class AttributeUnsignedIntWidget(AttributeFloatWidget):
    attribute_type_cast = int

    def _set_input_widget(self):
        super()._set_input_widget()
        self.input_widget.setDecimals(0)
        value_min = self.attribute.minimum()
        if value_min >= 0:
            self.input_widget.setMinimum(self.attribute_type_cast(value_min.m))
        else:
            self.input_widget.setMinimum(0)
