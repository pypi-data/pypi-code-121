from PyQt5.QtWidgets import QSizePolicy

from kamzik3.constants import *
from kamzik3.gui.attributeWidgets.attributeWidget import AttributeWidget
from kamzik3.snippets.snippetsWidgets import CustomLineEdit


class AttributeStringWidget(AttributeWidget):
    def _set_input_widget(self):
        self.input_widget = CustomLineEdit()
        if self.attribute[READONLY]:
            self.input_widget.setReadOnly(True)
        else:
            self.input_widget.setStyleSheet(".CustomLineEdit {background:#e6ffd9}")
            # self.input_widget.returnPressed.connect(
            #     lambda attribute=self.input_widget: self.set_value(attribute.text()))
            if self.attribute[DESCRIPTION] is not None:
                self.input_widget.setToolTip(self.attribute[DESCRIPTION])

        self.input_widget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

    def set_value(self, value):
        self.input_widget.setText(str(value))

    def get_attribute_value(self):
        return self.input_widget.text()

    def get_widget_value(self):
        return self.input_widget.text()
