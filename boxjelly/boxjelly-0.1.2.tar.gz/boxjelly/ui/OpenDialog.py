from PyQt5 import QtWidgets, QtGui

from boxjelly.ui.MediaSelectionBox import MediaSelectionBox
from boxjelly.ui.TrackSelectionBox import TrackSelectionBox


class OpenDialog(QtWidgets.QDialog):
    """Dialog to get a video and track source."""
    
    def __init__(self, parent):
        super().__init__(parent)
        
        # Style
        self.setWindowTitle('Open')
        self.setWindowIcon(QtGui.QIcon(':/icons/boxjelly_logo.svg'))
        self.setModal(True)
        self.resize(500, 0)
        
        # Create the selection boxes
        self._media_selection_box = MediaSelectionBox()
        self._track_selection_box = TrackSelectionBox()
        
        # Create the dialog buttons
        self._button_box = QtWidgets.QDialogButtonBox(QtWidgets.QDialogButtonBox.Ok | QtWidgets.QDialogButtonBox.Cancel)
        self._button_box.accepted.connect(self.accept)
        self._button_box.rejected.connect(self.reject)
        
        # Arrange the widgets
        self._arrange()
        
    def _arrange(self):
        self.setLayout(QtWidgets.QVBoxLayout())
        
        self.layout().addWidget(self._media_selection_box)
        self.layout().addWidget(self._track_selection_box)
        self.layout().addWidget(self._button_box)
    
    @property
    def media_content(self):
        return self._media_selection_box.media_content
    
    @property
    def track_io(self):
        return self._track_selection_box.io
