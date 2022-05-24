from PyQt5 import QtWidgets, QtCore


class FileSelector(QtWidgets.QWidget):
    """Widget to select a file"""
    
    fileSelected = QtCore.pyqtSignal(str)
    
    def __init__(self, parent=None, filter=None):
        super().__init__(parent)
        
        self.filter = filter
        
        self.line_edit = QtWidgets.QLineEdit()
        self.line_edit.setReadOnly(True)
        self.line_edit.setPlaceholderText('Select a file')
        
        self.browse_button = QtWidgets.QPushButton('Browse')
        self.browse_button.clicked.connect(self.browse)
        
        self.arrange()
    
    def arrange(self):
        """Arrange the widget"""
        # Set horizontal layout
        self.setLayout(QtWidgets.QHBoxLayout())
        
        # Set zero margins
        self.layout().setContentsMargins(0, 0, 0, 0)
        
        # Arrange line edit and browse button
        self.layout().addWidget(self.line_edit, stretch=1)
        self.layout().addWidget(self.browse_button)
    
    def browse(self):
        """Browse for a file using a file selection dialog"""
        file_name = QtWidgets.QFileDialog.getOpenFileName(self, 'Select a file', filter=self.filter)
        if file_name[0]:
            self.line_edit.setText(file_name[0])
            self.fileSelected.emit(file_name[0])
    