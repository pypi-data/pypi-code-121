from PyQt5.QtCore import pyqtSlot, Qt, QSize
from PyQt5.QtGui import QCursor, QIcon
from PyQt5.QtWidgets import (
    QVBoxLayout,
    QSpacerItem,
    QSizePolicy,
    QFrame,
    QMainWindow,
    QWidget,
    QDockWidget,
    QGridLayout,
    QLabel,
    QPushButton,
)

import kamzik3
from kamzik3.constants import *
from kamzik3.devices.deviceSession import DeviceSession
from kamzik3.gui.deviceGroupWidget import DeviceGroupWidget
from kamzik3.gui.templates.deviceGroupedListTemplate import Ui_MainWindow
from kamzik3.snippets.snippetsYaml import YamlSerializable


class DeviceGroupedListWidget(Ui_MainWindow, QMainWindow, YamlSerializable):
    previous_selected_tab = 0

    def __init__(self, config, parent=None):
        QMainWindow.__init__(self, parent)
        self.session = kamzik3.session
        self.config = config
        self.detached_tabs = {}
        self.setupUi(self)
        self.button_unlock_controls.hide()
        for group_title, group_config in self.config.get("groups", {}).items():
            self.add_group(
                group_title,
                group_config.get("widgets", []),
                group_config.get("model_image", None),
            )

        self.tab_changed(0)

    def yaml_mapping(self):
        mapping = super().yaml_mapping()
        del mapping["parent"]
        return mapping

    def keyPressEvent(self, key_event):
        if key_event.key() == Qt.Key_Escape:
            self.stop_all_devices()

        QMainWindow.keyPressEvent(self, key_event)

    def add_group(self, title, widgets, image=None):
        grouep_card = DeviceGroupWidget(title, image, parent=self.layout_top_controls)
        self.layout_top_controls.layout().addWidget(grouep_card)
        central_widget = QWidget()
        layout = QVBoxLayout(central_widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        for index, widget in enumerate(widgets):
            layout.addWidget(widget)
            widget.sigShowModel.connect(grouep_card.slot_show_model)
            widget.sigHideModel.connect(grouep_card.slot_hide_model)
            if index != len(widgets) - 1:
                line = QFrame()
                line.setFrameShape(QFrame.HLine)
                line.setFrameShadow(QFrame.Plain)
                line.setStyleSheet(
                    "QFrame {color: #f0f0f0; padding-left: 5px; padding-right: 5px}"
                )
                layout.addWidget(line)
            grouep_card.add_device(widget.device)

        spacer = QSpacerItem(0, 0, QSizePolicy.Minimum, QSizePolicy.Expanding)
        layout.addItem(spacer)
        self.tab_device_groups.addTab(central_widget, "  {}  ".format(title))

        def change_group(flag, index=self.tab_device_groups.count() - 1):
            self.group_checked(flag, index)

        grouep_card.button_device_group.clicked.connect(change_group)
        grouep_card.button_group_name.clicked.connect(change_group)

        grouep_card.signal_attach_request.connect(self.slot_attach_tab)
        grouep_card.signal_detach_request.connect(self.slot_detach_tab)

    def get_tab_index(self, tab_id):
        return list(self.config.get("groups", {}).keys()).index(tab_id)

    # pylint: disable=unused-argument
    def group_checked(self, flag, index):
        self.tab_changed(index)

    @pyqtSlot("QString")
    def slot_attach_tab(self, tab_id):
        tab_index = self.get_tab_index(tab_id)
        tab_widget = self.detached_tabs[tab_id]
        self.tab_device_groups.insertTab(
            tab_index, tab_widget.widget(), "  {}  ".format(tab_id)
        )
        self.tab_device_groups.setCurrentIndex(tab_index)
        self.tab_device_groups.removeTab(tab_index + 1)
        tab_widget.close()
        del self.detached_tabs[tab_id]

    @pyqtSlot("QString")
    def slot_detach_tab(self, tab_id):
        """
        Each Tab can be detached from main window.

        This method detached tab and make it as separate floating window.

        :param tab_id:
        """
        tab_index = self.get_tab_index(tab_id)
        tab_widget = self.tab_device_groups.widget(tab_index)

        title_bar_widget = QWidget()
        title_bar_widget.setLayout(QGridLayout())
        title_bar_widget.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum)
        label = QLabel(" - {}".format(tab_id))
        title_bar_widget.setStyleSheet("QWidget {background-color: #dde9ff}")
        label.setStyleSheet("QLabel {font-weight:bold; color:#003fb4}")

        tab_group_button = (
            self.layout_top_controls.layout()
            .itemAt(tab_index)
            .widget()
            .button_toggle_attach
        )
        attach_button = QPushButton("")
        attach_button.clicked.connect(tab_group_button.clicked)
        attach_button.setMaximumSize(20, 20)
        attach_button.setIconSize(QSize(20, 20))
        attach_button.setFlat(True)
        attach_button.setIcon(QIcon(":/icons/icons/attach.png"))
        attach_button.setCursor(QCursor(Qt.PointingHandCursor))
        attach_button.setToolTip(tab_group_button.toolTip())
        title_bar_widget.layout().addWidget(label, 0, 0)
        title_bar_widget.layout().addWidget(attach_button, 0, 1)

        dock_widget = QDockWidget(parent=self)
        dock_widget.setTitleBarWidget(title_bar_widget)
        dock_widget.setStyleSheet(
            "QDockWidget { font-size: 14px; font-weight: bold; background-color:#fff }"
        )
        dock_widget.setFeatures(
            QDockWidget.DockWidgetFloatable | QDockWidget.DockWidgetMovable
        )
        dock_widget.setAllowedAreas(Qt.NoDockWidgetArea)
        dock_widget.setWidget(tab_widget)
        dock_widget.adjustSize()

        dummy_tab = self.get_dummy_tab(tab_index, tab_id)
        self.tab_device_groups.insertTab(tab_index, dummy_tab, "  {}  ".format(tab_id))
        self.tab_device_groups.setCurrentIndex(tab_index)
        self.detached_tabs[tab_id] = dock_widget

        dock_widget.setFloating(True)
        dock_widget.show()

    def get_dummy_tab(self, tab_index, tab_id):
        """
        Create default dummy tab which serves as a placeholder for previously attached
        tab.

        :param tab_index:
        :param tab_id:
        :return:
        """
        dummy_widget = QWidget()
        layout = QGridLayout(dummy_widget)
        dummy_widget.setLayout(layout)
        button_attach = QPushButton("Click to attach {} group back".format(tab_id))
        button_attach.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        button_attach.setStyleSheet("font-size: 14px; font-weight: bold;")
        button_attach.setCursor(QCursor(Qt.PointingHandCursor))
        tab_group_button = (
            self.layout_top_controls.layout()
            .itemAt(tab_index)
            .widget()
            .button_toggle_attach
        )
        button_attach.clicked.connect(tab_group_button.clicked)
        layout.addWidget(button_attach)
        return dummy_widget

    @pyqtSlot(int)
    def tab_changed(self, index):
        if index < 0:
            return

        css = "QPushButton#button_device_group {{border:2px solid {0}; border-bottom:0px; border-left:2px solid {2}; border-right:2px solid {3}; background-color:{1}; margin:0px; padding:5px}}"
        top_layout = self.layout_top_controls.layout()
        top_layout.itemAt(
            self.previous_selected_tab
        ).widget().button_device_group.setStyleSheet(
            css.format("transparent", "transparent", "transparent", "transparent")
        )
        self.tab_device_groups.setCurrentIndex(index)
        if index == 0:
            style = ("#d1d1d1", "#dde9ff", "transparent", "#d1d1d1")
        elif index == len(self.tab_device_groups) - 1:
            style = ("#d1d1d1", "#dde9ff", "#d1d1d1", "transparent")
        else:
            style = ("#d1d1d1", "#dde9ff", "#d1d1d1", "#d1d1d1")

        top_layout.itemAt(index).widget().button_device_group.setStyleSheet(
            css.format(*style)
        )
        self.previous_selected_tab = index

    @pyqtSlot()
    def stop_all_devices(self):
        """Call stop method for any device in BUSY status."""
        for device in self.session.devices.values():
            try:
                if isinstance(device, DeviceSession):
                    continue
                if device.is_status(STATUS_BUSY):
                    device.stop()
            except AttributeError:
                # Ignore if device has not implemented stop method
                pass

    @pyqtSlot()
    def lock_widget(self):
        """
        Lock all control widgets.

        It's very usefull if user want to prevent any missclicks
        """
        for index in range(len(self.tab_device_groups)):
            self.tab_device_groups.widget(index).setEnabled(False)

        self.button_unlock_controls.show()
        self.button_lock_controls.hide()

    @pyqtSlot()
    def unlock_widget(self):
        """Unlock widget and make all control widgets accessible to user."""
        for index in range(len(self.tab_device_groups)):
            self.tab_device_groups.widget(index).setEnabled(True)

        self.button_unlock_controls.hide()
        self.button_lock_controls.show()
