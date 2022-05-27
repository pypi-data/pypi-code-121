from PyQt5.QtWidgets import QSizePolicy, QComboBox

from kamzik3.constants import *
from kamzik3.gui.attributeWidgets.attributeWidget import AttributeWidget


class AttributeComboxWidget(AttributeWidget):
    def _set_input_widget(self):
        self.input_widget = QComboBox()
        self.input_widget.addItems(
            ["None"] + [str(i) for i in self.attribute[TYPE_LIST_VALUES]]
        )
        self.input_widget.model().item(0).setEnabled(False)
        if self.attribute[READONLY]:
            self.input_widget.setDisabled(True)

        self.input_widget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

    def set_value(self, value):
        if value is None:
            return

        value = str(value)
        index = self.input_widget.findText(value)
        if value is None or index == -1:
            self.input_widget.setCurrentIndex(0)
        else:
            self.input_widget.setCurrentIndex(index)

    def get_attribute_value(self):
        return self.input_widget.currentText()

    def get_widget_value(self):
        return self.input_widget.currentText()
