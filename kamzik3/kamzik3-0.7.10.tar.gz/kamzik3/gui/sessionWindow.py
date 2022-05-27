from PyQt5.QtCore import QSize
from PyQt5.QtGui import QIcon, QFont
from PyQt5.QtWidgets import QMainWindow, QPushButton

import kamzik3
from kamzik3.gui.deviceDebugWidget import DeviceDebugWidget
from kamzik3.gui.templates.sessionWindowTemplate import Ui_MainWindow
from kamzik3.snippets.snippetsWidgets import show_centralized_top
from kamzik3.snippets.snippetsYaml import YamlSerializable


class SessionWindow(Ui_MainWindow, QMainWindow, YamlSerializable):
    def __init__(self, config=None):
        super().__init__()
        self.session = kamzik3.session
        self.config = config
        self.tools = []
        self.setupUi(self)

    def setupUi(self, MainWindow):
        super().setupUi(MainWindow)

        index = 0
        columns = 2 if self.config is None else self.config.get("columns", 2)
        if self.config is not None:
            for index, (title, tool, icon) in enumerate(self.config.get("tools", [])):
                column = index % columns
                row = int(index / columns)
                self.add_tool(title, tool, row, column, icon)

        index += 1
        column = index % columns
        row = int(index / columns)
        self.add_tool(
            "Session",
            DeviceDebugWidget(self.session.device_id),
            row,
            column,
            self.config.get("icon", ":/icons/icons/kamzik.png"),
        )
        self.setWindowIcon(QIcon(self.config.get("icon", ":/icons/icons/kamzik.png")))
        self.setWindowTitle(self.session.device_id)

    def show_tool(self, flag, tool):
        show_centralized_top(tool)

    def add_tool(self, title, tool, row, column, icon=None):
        self.tools.append(tool)
        tool_button = QPushButton(" {}".format(title))
        self.layout_tool_buttons.addWidget(tool_button, row, column)
        if icon is not None:
            tool_icon = QIcon(icon)
            tool_button.setIcon(tool_icon)
            tool.setWindowIcon(tool_icon)
        tool.setWindowTitle(title)
        tool_button.setIconSize(QSize(25, 25))
        tool_button.setStyleSheet("QPushButton {padding:5px}")
        tool_button.setMinimumWidth(150)
        button_font = QFont("Lucida Sans", 8)
        button_font.setBold(True)
        tool_button.setFont(button_font)
        tool_button.clicked.connect(lambda flag, tool=tool: self.show_tool(flag, tool))

    def closeEvent(self, *args, **kwargs):
        for tool in self.tools:
            tool.hide()
            tool.close()

        self.session = None
        self.tools = []
        QMainWindow.closeEvent(self, *args, **kwargs)
