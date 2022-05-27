from PyQt5.QtCore import pyqtSignal, pyqtSlot, QSize
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QWidget, QPushButton

from kamzik3.constants import *
from kamzik3.devices.observer import Observer
from kamzik3.gui.deviceWidget import DeviceWidget
from kamzik3.gui.templates.deviceGroupTemplate import Ui_Form
from kamzik3.snippets.snippetsYaml import YamlSerializable


class DeviceGroupWidget(Ui_Form, QWidget, Observer, YamlSerializable):
    sig_set_status_color = pyqtSignal("QString")
    model_image = None
    signal_detach_request = pyqtSignal("QString")
    signal_attach_request = pyqtSignal("QString")
    attached = True

    def __init__(self, title, model_image=None, config=None, parent=None):
        QWidget.__init__(self, parent)
        self.devices = []
        self.config = config
        if model_image is not None:
            self.model_image = QIcon(model_image)
        self.title = title
        self.setupUi(self)
        self.sig_set_status_color.connect(self.set_status_color)
        self.button_group_name.setText("{}  ".format(title))

    def yaml_mapping(self):
        mapping = super().yaml_mapping()
        del mapping["parent"]
        return mapping

    def setupUi(self, Form):
        super().setupUi(Form)
        if self.model_image is not None:
            self.button_device_group.setIcon(self.model_image)
        self.button_device_group.resizeEvent = self.button_resized_event

    def add_device(self, device):
        """
        Add new device into group.

        :param device:
        """
        self.devices.append(device)
        self.attach_to_subject(device)

    def subject_update(self, key, value, subject):
        """
        Check all statuses if only one status changed.

        This way we ensure that group status represents all device statuses.

        :param key:
        :param value:
        :param subject:
        """
        if key == ATTR_STATUS:
            status_priorities = []
            for device in self.devices:
                priority = STATUSES_PRIORITY.index(device[ATTR_STATUS][VALUE])
                status_priorities.append(priority)

            group_status = STATUSES_PRIORITY[min(status_priorities)]
            status_color = DeviceWidget.status_colors.get(group_status, "blue")
            self.sig_set_status_color.emit(status_color)

    @pyqtSlot("QString")
    def set_status_color(self, color):
        self.frame_label_area.setStyleSheet(
            "QFrame {{background-color:{}}}".format(color)
        )

    def close(self):
        for device in self.devices:
            self.detach_subject(device)

    @pyqtSlot("QIcon")
    def slot_show_model(self, model_image):
        self.button_device_group.setIcon(model_image)

    @pyqtSlot("QIcon")
    # pylint: disable=unused-argument
    def slot_hide_model(self, model_image):
        self.button_device_group.setIcon(self.model_image)

    def button_resized_event(self, QResizeEvent):
        """
        This method resize group to max of 200 pixels width.

        :param QResizeEvent:
        :return:
        """
        w, h = QResizeEvent.size().width(), QResizeEvent.size().height()
        if w >= 200:
            h = w = 200
        else:
            h = w
        self.button_device_group.setIconSize(QSize(w, h))
        return QPushButton.resizeEvent(self.button_device_group, QResizeEvent)

    def toggle_attach(self):
        """Toggle tab attachment."""
        self.attached = not self.attached
        if self.attached:
            self.button_toggle_attach.setIcon(QIcon(":/icons/icons/detach.png"))
            self.signal_attach_request.emit(self.title)
        else:
            self.button_toggle_attach.setIcon(QIcon(":/icons/icons/attach.png"))
            self.signal_detach_request.emit(self.title)
