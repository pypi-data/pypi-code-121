from PyQt5 import QtWidgets

from boxjelly.ui.settings.tabs.AbstractSettingsTab import AbstractSettingsTab


class VideoSettingsTab(AbstractSettingsTab):
    """
    Video settings tab.
    """
    
    def __init__(self, parent=None):
        super().__init__('Video', parent=parent)
        
        self._frame_rate_edit = QtWidgets.QDoubleSpinBox()
        self._frame_rate_edit.setRange(0.01, 1000.0)
        self._frame_rate_edit.setDecimals(2)
        self._frame_rate_edit.setSuffix(' fps')
        self._frame_rate_edit.setSingleStep(0.01)
        self._frame_rate_edit.setStepType(QtWidgets.QAbstractSpinBox.StepType.DefaultStepType)
        self._frame_rate_edit.setValue(self._settings.frame_rate.value)
        
        self._frame_rate_edit.valueChanged.connect(self._settings_changed)
        
        self._arrange()
    
    def _arrange(self):
        layout = QtWidgets.QFormLayout()
        
        layout.addRow('Frame Rate', self._frame_rate_edit)
        
        self.setLayout(layout)
    
    def apply_settings(self):
        self._settings.frame_rate.value = self._frame_rate_edit.value()
    