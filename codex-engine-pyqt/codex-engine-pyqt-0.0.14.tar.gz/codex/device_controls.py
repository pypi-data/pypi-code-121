from qtstrap import *
from codex import DeviceManager
from serial.tools.list_ports import comports

try:
    from serial_monitor import SerialMonitorWidget
    serial_monitor_available = True
except:
    serial_monitor_available = False

try:
    from command_palette import CommandPalette, Command
    command_palette_available = True
except:
    command_palette_available = False


class DeviceTreeWidgetItem(QTreeWidgetItem):
    def __init__(self, parent, device):
        super().__init__(parent)

        self.device = device
        self.guid = device.guid
        
        self.setText(0, device.profile_name)

        parts = device.port.split('link?')
        port = device.port if (len(parts) == 1) else parts[1]

        self.setText(1, port)


@DeviceManager.subscribe
class DeviceTree(QTreeWidget):
    widget_requested = Signal(object)
    settings_requested = Signal(object)
    remove_requested = Signal(object)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setUniformRowHeights(True)
        self.setExpandsOnDoubleClick(False)
        self.setItemsExpandable(False)
        self.setSelectionMode(QAbstractItemView.NoSelection)
        self.setColumnCount(2)
        self.setColumnWidth(0,150)
        self.setHeaderLabels(['Name', 'Port'])
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        self.nodes = {}
        self.local_device_root = QTreeWidgetItem(self)
        self.local_device_root.setText(0, "Local Devices")
        self.remote_device_root = QTreeWidgetItem(self)
        self.remote_device_root.setText(0, "Remote Devices")

        self.open_monitors = {}

    def device_added(self, device):
        if device.port[:5] == 'ws://':
            parent = self.remote_device_root
        else:
            parent = self.local_device_root

        self.nodes[device.guid] = DeviceTreeWidgetItem(parent, device)
        self.expandAll()

    def device_removed(self, guid):
        if guid in self.nodes:
            item = self.nodes[guid]
            parent = item.parent()
            index = parent.indexOfChild(item)
            parent.takeChild(index)

    def contextMenuEvent(self, event):
        pos = event.globalPos()
        item = self.itemAt(self.viewport().mapFromGlobal(pos))

        if item is self.local_device_root:
            menu = QMenu()
            menu.addAction(QAction('Add device', self))
            menu.addAction(QAction('Rescan ports', self))
            menu.addAction(QAction('Configure', self))
            menu.exec_(pos)

        if item is self.remote_device_root:
            menu = QMenu()
            menu.addAction(QAction('Add device', self))
            menu.addAction(QAction('Configure', self))
            menu.exec_(pos)

        if hasattr(item, 'device'):
            menu = QMenu()
            
            if hasattr(item.device, 'settings'):
                menu.addAction(QAction("Settings", self, triggered=lambda: self.open_settings(item)))

            if hasattr(item.device, 'widget'):
                menu.addAction(QAction("Open Device Controls", self, triggered=lambda: self.open_widget(item)))

            if hasattr(item.device, 'locate'):
                menu.addAction(QAction("Locate Device", self, triggered=item.device.locate))

            if serial_monitor_available:
                menu.addAction(QAction("Open Serial Monitor", self, triggered=lambda: self.open_monitor(item)))
                menu.addAction(QAction("Open Serial Port", self, triggered=lambda: self.open_serial_port(item)))
            menu.addAction(QAction("Remove", self, triggered=lambda: self.remove_clicked(item)))
            menu.exec_(pos)

    def open_settings(self, item):
        if hasattr(item, 'device'):
            if hasattr(item.device, 'widget'):
                print('settings:', item.device.profile_name)

    def open_widget(self, item):
        if hasattr(item, 'device'):
            if hasattr(item.device, 'widget'):
                print('widget:', item.device.profile_name)

    def open_monitor(self, item):
        if serial_monitor_available:
            monitor = SerialMonitorWidget()
            monitor.setWindowTitle(item.device.title)
            item.device.connect_stream(monitor)
            self.open_monitors[item.device.guid] = monitor
            monitor.show()

    def open_serial_port(self, item):
        if serial_monitor_available:
            monitor = SerialMonitorWidget()
            monitor.setWindowTitle(item.device.title)
            item.device.connect_stream(monitor, 'rejected')
            self.open_monitors[item.device.guid] = monitor
            monitor.show()

    def remove_clicked(self, item):
        if hasattr(item, 'device'):
            self.signals.remove_device.emit(item.device.guid)


class CustomListWidget(QWidget):
    list_changed = Signal(list)

    def __init__(self, title, parent=None):
        super().__init__(parent)
        self.title = QLabel(title)
        self.list = QListWidget()
        self.line = QLineEdit(self)
        self.line.returnPressed.connect(self.on_add)
        self.add = QPushButton('Add', clicked=self.on_add)

        with CVBoxLayout(self, margins=(0,0,0,0)) as layout:
            with layout.hbox(margins=(0,0,0,0)) as layout:
                layout.add(self.title)
            with layout.hbox(margins=(0,0,0,0)) as layout:
                layout.add(self.line, 1)
                layout.add(self.add)
            layout.add(self.list)

    def contextMenuEvent(self, event: QtGui.QContextMenuEvent) -> None:
        pos = event.globalPos()
        item = self.list.itemAt(self.list.viewport().mapFromGlobal(pos))
        index = self.list.indexFromItem(item).row()

        menu = QMenu()
        menu.addAction(QAction('Remove', self, triggered=lambda: self.on_remove(index)))
        menu.exec_(pos)

    def on_remove(self, index):
        self.list.takeItem(index)
        self.on_change()

    def on_add(self):
        item = self.line.text()
        self.line.clear()
        self.list.addItem(item)
        self.list.sortItems()
        self.on_change()

    def on_change(self):
        new_items = []
        for i in range(self.list.count()):
            new_items.append(self.list.item(i).text())

        self.list_changed.emit(new_items)

    def addItems(self, items):
        if items:
            self.list.addItems(items)


class DeviceManagerSettings(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.dm = QApplication.instance().device_manager

        self.starting_devices = CustomListWidget('Starting Devices:')
        self.starting_devices.addItems(self.dm.starting_devices)
        self.starting_devices.list_changed.connect(self.dm.set_starting_devices)

        self.ignored_ports = CustomListWidget('Ignored Ports:')
        self.ignored_ports.addItems(self.dm.ignored_ports)
        self.ignored_ports.list_changed.connect(self.dm.set_ignored_ports)

        with CVBoxLayout(self, margins=(0,0,0,0)) as layout:
            layout.add(self.ignored_ports)
            layout.add(self.starting_devices)


@DeviceManager.subscribe
class NewDeviceWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.profile = QComboBox()
        self.port = QComboBox()
        self.add = QPushButton('Add Device', clicked=self.add_pressed)

        names = [p for p in DeviceManager.profile_names() if p != 'no profile']
        self.profile.addItems(names)
        ports = ["DummyPort", *[port.device for port in sorted(comports())]]
        self.port.addItems(ports)

        with CVBoxLayout(self, margins=(0,0,0,0)) as layout:
            # layout.add(QLabel('Add a device:'))
            with layout.hbox(margins=(0,0,0,0)) as layout:
                with layout.vbox(margins=(0,0,0,0)) as layout:
                    layout.add(QLabel('Profiles:'))
                    layout.add(QLabel('Ports:'))
                with layout.vbox(margins=(0,0,0,0)) as layout:
                    with layout.hbox(margins=(0,0,0,0)) as layout:
                        layout.add(self.profile, 1)
                    with layout.hbox(margins=(0,0,0,0)) as layout:
                        layout.add(self.port, 1)
                        layout.add(self.add)

    def add_pressed(self):
        profile = self.profile.currentText()
        port = self.port.currentText()

        device = DeviceManager.profiles()[profile](port)
        self.signals.add_device.emit(device)


class DeviceControlsWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent=parent)

        tree = QWidget()
        with CVBoxLayout(tree) as layout:
            layout.add(NewDeviceWidget(self))
            layout.add(DeviceTree(self))

        settings = QWidget()
        with CVBoxLayout(settings) as layout:
            layout.add(DeviceManagerSettings(self))

        tabs = {'Devices':tree, 'Settings':settings, }
        with CVBoxLayout(self) as layout:
            self.tabs = layout.add(PersistentTabWidget('device_control_tabs', tabs=tabs))


class DeviceControlsDockWidget(QDockWidget):
    def __init__(self, parent=None):
        super().__init__('Device Controls', parent=parent)
        self.setObjectName('DeviceControls')

        self.setWidget(DeviceControlsWidget(self))

        if command_palette_available:
            self.commands = [
                Command("Device List: Show device list", triggered=self.show, shortcut='Ctrl+D'),
                Command("Device List: Hide device list", triggered=self.hide),
            ]

        self.setAllowedAreas(Qt.LeftDockWidgetArea | Qt.RightDockWidgetArea)
        self.setFeatures(QDockWidget.DockWidgetClosable | QDockWidget.DockWidgetMovable)

        self.starting_area = Qt.RightDockWidgetArea

        if not self.parent().restoreDockWidget(self):
            self.parent().addDockWidget(self.starting_area, self)

        self.closeEvent = lambda x: self.hide()

    def toggleViewAction(self):
        action = super().toggleViewAction()
        action.setShortcut('Ctrl+D')
        return action