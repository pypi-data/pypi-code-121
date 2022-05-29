from PySide6.QtWidgets import QWidget
from github.ContentFile import ContentFile

from ui.widgets import Ui_FileTemplate
from utils import format_file_size


class FileTemplate(QWidget):
    def __init__(self, name, content_type, size):
        """
        Initialize the widget

        Parameters
        ----------
        name : str
            The name of the file
        content_type : str
            The content type of the file
        size : int
            The size of the file
        """
        super(FileTemplate, self).__init__()
        self.ui = Ui_FileTemplate()
        self.ui.setupUi(self)

        self.name = name
        self.content_type = content_type
        self.size = size

        self.fill()

    def fill(self):
        """
        Fill the widget with the data from the content file
        """
        self.ui.nameWidget.setText(self.name)
        self.ui.nameWidget.set_icon("fa5s.file-alt" if self.content_type == "file" else "fa5s.folder")
        self.ui.sizeLabel.setText(str(format_file_size(self.size, "B", "KB")) + " KB")
        if self.content_type == "dir":
            self.ui.sizeLabel.setText("")
