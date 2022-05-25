from qtpy import QtWidgets as QtW
from qtpy.QtCore import Qt
from superqt import QDoubleSlider

from . import _spacemouse as sm
from . import install, uninstall
from ._napari import CFG


class SpaceMouse(QtW.QWidget):
    def __init__(self, parent=None) -> None:
        super().__init__(parent)

        self._dev_combo = QtW.QComboBox()
        self._dev_combo.addItems(sm.list_connected_devices())

        self._on_btn = QtW.QPushButton()
        self._on_btn.setCheckable(True)
        self._on_btn.toggled.connect(self._on_btn_changed)
        self._on_btn.setChecked(True)
        self._on_btn_changed(True)
        self._gain = QDoubleSlider(Qt.Orientation.Horizontal)
        self._gain.setRange(0.5, 5)
        self._gain.setValue(2)
        self._gain.valueChanged.connect(self._on_gain_changed)

        self.setLayout(QtW.QVBoxLayout())
        self.layout().addWidget(self._dev_combo)
        self.layout().addWidget(self._on_btn)

        _gain = QtW.QWidget()
        _gain.setLayout(QtW.QHBoxLayout())
        _gain.layout().addWidget(QtW.QLabel("gain"))
        _gain.layout().addWidget(self._gain)
        self.layout().addWidget(_gain)

        # needs magicgui from pydantic model
        for name, field in CFG.__fields__.items():
            if field.type_ is bool:
                box = QtW.QCheckBox(name)
                box.setChecked(getattr(CFG, name))
                box.setObjectName(name)
                box.toggled.connect(self._cfg_toggled)
                self.layout().addWidget(box)

    def _on_btn_changed(self, state: bool):
        if state:
            self._on_btn.setText("Deactivate Mouse")
            self._on_btn.setStyleSheet("background-color: #A00")
            install(self._dev_combo.currentText())
        else:
            self._on_btn.setText("Activate Mouse")
            self._on_btn.setStyleSheet("")
            uninstall()

    def _on_gain_changed(self, value):
        CFG.gain_pitch = value
        CFG.gain_roll = value
        CFG.gain_yaw = value
        CFG.gain_zoom = value

    def _cfg_toggled(self, state):
        setattr(CFG, self.sender().objectName(), state)
