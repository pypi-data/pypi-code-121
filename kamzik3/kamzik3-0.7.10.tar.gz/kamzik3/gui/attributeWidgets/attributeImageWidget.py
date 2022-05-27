import time

from PyQt5.QtCore import QSize
from PyQt5.QtWidgets import QSizePolicy
from pyqtgraph.widgets.RawImageWidget import RawImageWidget

from kamzik3.constants import *
from kamzik3.gui.attributeWidgets.attributeWidget import AttributeWidget
from kamzik3.gui.fastDisplay.imageView import ImageView


class AttributeImageWidget(AttributeWidget):
    lt = time.perf_counter_ns()

    def _set_input_widget(self):
        self.input_widget = ImageView()
        if self.attribute[DESCRIPTION] is not None:
            self.input_widget.setToolTip(self.attribute[DESCRIPTION])
        self.input_widget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

    def set_value(self, value):
        self.input_widget.slot_new_frame(value)

    def get_attribute_value(self):
        return None

    def get_widget_value(self):
        return None
