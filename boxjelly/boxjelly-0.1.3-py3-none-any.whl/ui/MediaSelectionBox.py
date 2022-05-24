from PyQt5 import QtWidgets, QtMultimedia

from boxjelly.ui.WidgetComboBox import WidgetComboBox
from boxjelly.ui.SourceWidgets import LocalVideoMediaSourceWidget, URLMediaSourceWidget


class MediaSelectionBox(QtWidgets.QGroupBox):
    """Media selection group box"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        self.setTitle('Media')
        
        self.widget_combo_box = WidgetComboBox(self)
        self.widget_combo_box.add_widget(LocalVideoMediaSourceWidget(self), 'Video file')
        self.widget_combo_box.add_widget(URLMediaSourceWidget(self), 'Video URL')
        self.widget_combo_box.refresh()
        
        self.arrange()
    
    def arrange(self):
        """Arrange the widget"""
        # Set vertical layout
        self.setLayout(QtWidgets.QVBoxLayout())
        
        # Add widget combo box
        self.layout().addWidget(self.widget_combo_box)
        
        # Add stretch
        self.layout().addStretch()
    
    @property
    def media_content(self) -> QtMultimedia.QMediaContent:
        return self.widget_combo_box.widget.media_content
