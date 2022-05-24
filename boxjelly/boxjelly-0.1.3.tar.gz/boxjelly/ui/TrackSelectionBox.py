from PyQt5 import QtWidgets

from boxjelly.ui.WidgetComboBox import WidgetComboBox
from boxjelly.ui.SourceWidgets import DeepseaTrackSourceWidget, YOLOv5DeepSortTrackSourceWidget, JSONTrackSourceWidget
from boxjelly.lib.fileio import AbstractTrackFileIO


class TrackSelectionBox(QtWidgets.QGroupBox):
    """Track selection group box"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        self.setTitle('Tracks')
        
        self.widget_combo_box = WidgetComboBox(self)
        self.widget_combo_box.add_widget(YOLOv5DeepSortTrackSourceWidget(self), 'YOLOv5-DeepSort')
        self.widget_combo_box.add_widget(DeepseaTrackSourceWidget(self), 'deepsea-track')
        self.widget_combo_box.add_widget(JSONTrackSourceWidget(self), 'JSON')
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
    def io(self) -> AbstractTrackFileIO:
        return self.widget_combo_box.widget.io