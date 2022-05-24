from PyQt5 import QtWidgets

from boxjelly.ui.settings.tabs.AbstractSettingsTab import AbstractSettingsTab


class NetworkSettingsTab(AbstractSettingsTab):
    """
    Network settings tab.
    """
    
    def __init__(self, parent=None):
        super().__init__('Network', parent=parent)
        
        self._remote_control_section = QtWidgets.QGroupBox('Remote Control')
        
        self._control_port_edit = QtWidgets.QSpinBox()
        self._control_port_edit.setRange(0, 65535)
        self._control_port_edit.setValue(self._settings.control_port.value)
        
        self._localization_section = QtWidgets.QGroupBox('Localization')
        
        self._incoming_port_edit = QtWidgets.QSpinBox()
        self._incoming_port_edit.setRange(0, 65535)
        self._incoming_port_edit.setValue(self._settings.incoming_port.value)
        
        self._incoming_port_topic_edit = QtWidgets.QLineEdit()
        self._incoming_port_topic_edit.setText(self._settings.incoming_topic.value)
        
        self._outgoing_port_edit = QtWidgets.QSpinBox()
        self._outgoing_port_edit.setRange(0, 65535)
        self._outgoing_port_edit.setValue(self._settings.outgoing_port.value)
        
        self._outgoing_port_topic_edit = QtWidgets.QLineEdit()
        self._outgoing_port_topic_edit.setText(self._settings.outgoing_topic.value)
        
        self._control_port_edit.valueChanged.connect(self._settings_changed)
        self._incoming_port_edit.valueChanged.connect(self._settings_changed)
        self._incoming_port_topic_edit.textChanged.connect(self._settings_changed)
        self._outgoing_port_edit.valueChanged.connect(self._settings_changed)
        self._outgoing_port_topic_edit.textChanged.connect(self._settings_changed)
        
        self._arrange()
    
    def _arrange(self):
        layout = QtWidgets.QVBoxLayout()
        
        remote_control_layout = QtWidgets.QFormLayout()
        remote_control_layout.addRow('Control Port', self._control_port_edit)
        self._remote_control_section.setLayout(remote_control_layout)
        
        localization_layout = QtWidgets.QFormLayout()
        localization_layout.addRow('Incoming Port', self._incoming_port_edit)
        localization_layout.addRow('Incoming Topic', self._incoming_port_topic_edit)
        localization_layout.addRow('Outgoing Port', self._outgoing_port_edit)
        localization_layout.addRow('Outgoing Topic', self._outgoing_port_topic_edit)
        self._localization_section.setLayout(localization_layout)
        
        layout.addWidget(self._remote_control_section)
        layout.addWidget(self._localization_section)
        
        self.setLayout(layout)
    
    def apply_settings(self):
        # Remote control
        self._settings.control_port.value = self._control_port_edit.value()
        
        # Localization control
        if self._settings.incoming_port.value != self._incoming_port_edit.value():
            self._settings.incoming_port.value = self._incoming_port_edit.value()
        
        if self._settings.incoming_topic.value != self._incoming_port_topic_edit.text():
            self._settings.incoming_topic.value = self._incoming_port_topic_edit.text()
        
        if self._settings.outgoing_port.value != self._outgoing_port_edit.value():
            self._settings.outgoing_port.value = self._outgoing_port_edit.value()
        
        if self._settings.outgoing_topic.value != self._outgoing_port_topic_edit.text():
            self._settings.outgoing_topic.value = self._outgoing_port_topic_edit.text()
    