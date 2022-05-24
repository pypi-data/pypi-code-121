from PyQt5 import QtWidgets, QtCore

from boxjelly.ui.track.Timeline import Timeline
from boxjelly.ui.track.TrackHeadersView import TrackHeadersView
from boxjelly.ui.track.TrackGraphicsView import TrackGraphicsView
from boxjelly.models.TrackListModel import TrackListModel


class TrackPanel(QtWidgets.QWidget):
    """Track panel widget"""
    
    frameSelected = QtCore.pyqtSignal(int)
    
    def __init__(self, parent, track_model: TrackListModel, selection_model: QtCore.QItemSelectionModel):
        super().__init__(parent)
        
        self._track_model = track_model
        self._selection_model = selection_model
        
        # Set minimum size
        self.setMinimumSize(800, 0)
        
        # Set default size
        self.setGeometry(0, 0, 800, 100)
        
        # Create timeline
        self.timeline = Timeline(self, 300)
        
        # Create track view
        self.track_view = TrackGraphicsView(self, self._track_model, self._selection_model)
        
        # Create track headers view
        self.track_headers_view = TrackHeadersView(self)
        self.track_headers_view.setModel(self._track_model)
        self.track_headers_view.setSelectionModel(self._selection_model)
        
        # Connect signals and slots
        self.track_view.frameScrolled.connect(self.timeline.set_frame)
        self.track_view.verticalScrollBarChanged.connect(self.track_headers_view.set_vertical_scroll)
        self.track_view.scaleChanged.connect(lambda x_scale, y_scale: self.timeline.set_frame_scale(x_scale))
        self.timeline.frameSelected.connect(self.frameSelected.emit)
        
        self.arrange()
    
    def arrange(self):
        """Arrange the track panel"""
        # Set vertical layout
        self.setLayout(QtWidgets.QGridLayout())
        
        # Arrange timeline
        self.layout().addWidget(self.timeline, 0, 1, 1, 1)
        
        # Arrange track headers list view
        self.layout().addWidget(self.track_headers_view, 1, 0, 1, 1)
        
        # Arrange track view
        self.layout().addWidget(self.track_view, 1, 1, 1, 1)
        
        self.layout().setRowStretch(0, 0)
        self.layout().setRowStretch(1, 1)
        self.layout().setColumnStretch(0, 0)
        self.layout().setColumnStretch(1, 1)
    
    def show_frame(self, frame: int):
        """Show data corresponding to a particular frame number"""
        self.track_view.show_frame(frame)
