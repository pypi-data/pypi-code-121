from PyQt5 import QtWidgets, QtMultimedia, QtCore

from boxjelly.lib.fileio import AbstractTrackFileIO, DeepseaTrackFileIO, JSONTrackFileIO, YOLOv5DeepSortTrackFileIO
from boxjelly.ui.FileSelector import FileSelector


class AbstractMediaSourceWidget(QtWidgets.QWidget):
    """Abstract media source widget"""
    
    @property
    def media_content(self) -> QtMultimedia.QMediaContent:
        raise NotImplementedError()


class AbstractTrackSourceWidget(QtWidgets.QWidget):
    """Abstract track source widget"""
    
    @property
    def io(self) -> AbstractTrackFileIO:
        raise NotImplementedError()


class LocalVideoMediaSourceWidget(AbstractMediaSourceWidget):
    """Video file media source widget. Loads local video files."""
    def __init__(self, parent):
        super().__init__(parent)
    
        self._filename = None
        
        self._selector = FileSelector(self, filter='Video files (*.mp4 *.mov *.wmv *.avi)')
        self._selector.fileSelected.connect(self._update_filename)

        self.arrange()
    
    def arrange(self):
        """Arrange the widget"""
        # Set vertical layout
        self.setLayout(QtWidgets.QVBoxLayout())
        
        # Set zero margins
        self.layout().setContentsMargins(0, 0, 0, 0)
        
        # Arrange the file selector
        self.layout().addWidget(self._selector)
    
    def _update_filename(self, filename):
        self._filename = filename
    
    @property
    def media_content(self) -> QtMultimedia.QMediaContent:
        return QtMultimedia.QMediaContent(QtCore.QUrl.fromLocalFile(self._filename))


class URLMediaSourceWidget(AbstractMediaSourceWidget):
    """URL media source widget. Loads video files from URL."""
    def __init__(self, parent):
        super().__init__(parent)
    
        self._url = None
        
        self._line_edit = QtWidgets.QLineEdit()
        self._line_edit.setPlaceholderText('URL')
        self._line_edit.textChanged.connect(self._update_url)
        
        self.arrange()
    
    def arrange(self):
        """Arrange the widget"""
        # Set vertical layout
        self.setLayout(QtWidgets.QVBoxLayout())
        
        # Set zero margins
        self.layout().setContentsMargins(0, 0, 0, 0)
        
        # Arrange the text input
        self.layout().addWidget(self._line_edit)
    
    def _update_url(self, url):
        self._url = url
    
    @property
    def media_content(self) -> QtMultimedia.QMediaContent:
        return QtMultimedia.QMediaContent(QtCore.QUrl(self._url))


class YOLOv5DeepSortTrackSourceWidget(AbstractTrackSourceWidget):
    """YOLOv5-DeepSort file track source widget. Loads tracks from a modified MOT text file."""
    def __init__(self, parent):
        super().__init__(parent)
    
        self._filename = None
        
        self._selector = FileSelector(self, filter='Text files (*.txt)')
        self._selector.fileSelected.connect(self._update_filename)
        
        self.arrange()
    
    def arrange(self):
        """Arrange the widget"""
        # Set vertical layout
        self.setLayout(QtWidgets.QVBoxLayout())
        
        # Set zero margins
        self.layout().setContentsMargins(0, 0, 0, 0)
        
        # Arrange the file selector
        self.layout().addWidget(self._selector)
    
    def _update_filename(self, filename):
        self._filename = filename
    
    @property
    def io(self) -> YOLOv5DeepSortTrackFileIO:
        return YOLOv5DeepSortTrackFileIO(self._filename)


class DeepseaTrackSourceWidget(AbstractTrackSourceWidget):
    """deepsea-track artifact track source widget. Loads tracks from a tar.gz artifact of track JSONs as output by deepsea-track."""
    def __init__(self, parent):
        super().__init__(parent)
        
        self._filename = None
        
        self._selector = FileSelector(self, filter='Tar.gz files (*.tar.gz)')
        self._selector.fileSelected.connect(self._update_filename)
        
        self.arrange()
        
    def arrange(self):
        """Arrange the widget"""
        # Set vertical layout
        self.setLayout(QtWidgets.QVBoxLayout())
        
        # Set zero margins
        self.layout().setContentsMargins(0, 0, 0, 0)
        
        # Arrange the file selector
        self.layout().addWidget(self._selector)
    
    def _update_filename(self, filename):
        self._filename = filename
    
    @property
    def io(self) -> DeepseaTrackFileIO:
        return DeepseaTrackFileIO(self._filename)


class JSONTrackSourceWidget(AbstractTrackSourceWidget):
    """JSON track source widget"""
    def __init__(self, parent):
        super().__init__(parent)
        
        self._filename = None
        
        self._selector = FileSelector(self, filter='JSON files (*.json)')
        self._selector.fileSelected.connect(self._update_filename)
        
        self.arrange()
        
    def arrange(self):
        """Arrange the widget"""
        # Set vertical layout
        self.setLayout(QtWidgets.QVBoxLayout())
        
        # Set zero margins
        self.layout().setContentsMargins(0, 0, 0, 0)
        
        # Arrange the file selector
        self.layout().addWidget(self._selector)
    
    def _update_filename(self, filename):
        self._filename = filename
    
    @property
    def io(self) -> JSONTrackFileIO:
        return JSONTrackFileIO(self._filename)
        