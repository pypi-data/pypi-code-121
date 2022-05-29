import os
import sys
import traceback

import qtawesome as qta
from PySide6.QtCore import QRunnable, Signal, Slot, QThreadPool, QObject
from PySide6.QtWidgets import QWidget, QFileDialog

from modules.local_repository import LocalRepository
from ui.widgets import Ui_LocalRepositories
from utils import USER_HOME_PATH
from widgets import LocalRepositoryListWidgetItem
from widgets.LocalRepositoryTemplate import LocalRepositoryTemplate


class WorkerSignals(QObject):
    repo = Signal(str, str)
    finished = Signal()
    error = Signal(tuple)


class Worker(QRunnable):
    def __init__(self, path):
        """
        Worker to find all local repositories in a given path and emit them asynchronously

        Parameters
        ----------
        path : str
            Path to search for local repositories
        """
        super(Worker, self).__init__()
        self.path = path
        self.signals = WorkerSignals()

    @Slot(str)
    def run(self):
        """
        Find all local repositories in a given path and emit them asynchronously
        """
        try:
            for root, subdirs, files in os.walk(self.path):
                for d in subdirs:
                    if os.access(root, os.R_OK):
                        if d == ".git":
                            folder_name = root.split(os.sep)[-1]
                            self.signals.repo.emit(folder_name, root)
                    else:
                        print(d + " No permission")
        except Exception:
            traceback.print_exc()
            exctype, value = sys.exc_info()[:2]
            self.signals.error.emit((exctype, value, traceback.format_exc()))
        finally:
            self.signals.finished.emit()


class LocalRepositories(QWidget):
    def __init__(self, user):
        """
        Initialize the local repositories widget

        Parameters
        ----------
        user : User
            User object
        """
        super(LocalRepositories, self).__init__()
        self.ui = Ui_LocalRepositories()
        self.ui.setupUi(self)

        self.user = user
        self.open_repo = None

        self.thread_pool = QThreadPool()

        self.config()
        self.thread_load_items()

    def load_finished(self):
        """
        Function to be executed when the thread is finished to enable some UI elements
        """
        self.ui.searchButton.setEnabled(True)
        self.ui.searchPathButton.setEnabled(True)
        self.ui.lineEdit.setEnabled(True)
        self.ui.loadingButton.hide()

    @Slot(str, str)
    def add_new_repo(self, folder_name, path):
        """
        Add a new repository to the list of local repositories

        Parameters
        ----------
        folder_name : str
            Name of the folder containing the repository
        path : str
            Path to the folder containing the repository
        """
        try:
            item = LocalRepositoryListWidgetItem(folder_name, path)
            widget = LocalRepositoryTemplate(path, self.user)
            item.setSizeHint(widget.sizeHint())
            self.ui.listWidget.addItem(item)
            self.ui.listWidget.setItemWidget(item, widget)
        except Exception:
            print("Error while adding new repo " + folder_name + " " + path)

    def thread_load_items(self):
        """
        Load all local repositories in a separate thread
        """
        self.ui.loadingButton.show()
        self.ui.searchButton.setDisabled(True)
        self.ui.searchPathButton.setDisabled(True)
        self.ui.lineEdit.setDisabled(True)
        self.ui.listWidget.clear()

        worker = Worker(self.ui.lineEdit_2.text())
        worker.signals.repo.connect(self.add_new_repo)
        worker.signals.finished.connect(self.load_finished)

        self.thread_pool.start(worker)

    def config(self):
        """
        Configures the signals of the widget
        """
        self.ui.listWidget.itemClicked.connect(self.open_repository)
        self.ui.searchPathButton.clicked.connect(self.save_path)
        self.ui.searchButton.clicked.connect(self.thread_load_items)
        self.ui.lineEdit_2.setText(str(USER_HOME_PATH))
        self.ui.lineEdit.textChanged.connect(self.on_text_changed)
        self.ui.loadingButton.setIcon(qta.icon('ri.loader-4-line', animation=qta.Pulse(self.ui.loadingButton)))
        self.ui.loadingButton.setToolTip("Searching repositories...")
        self.ui.loadingButton.hide()

    def save_path(self):
        """
        Repository save path and update a line edit
        """
        new_route = QFileDialog.getExistingDirectory(self, "Select folder", str(USER_HOME_PATH))
        if new_route:
            self.ui.lineEdit_2.setText(new_route)

    def open_repository(self, item):
        """
        Opens the repository selected in a new window
        """
        repo_name = item.path
        self.open_repo = LocalRepository(repo_name, self.user)
        self.open_repo.show()

    def on_text_changed(self, text):
        """
        Filters the repositories with the text entered the lineEdit
        """
        for row in range(self.ui.listWidget.count()):
            item = self.ui.listWidget.item(row)
            widget = self.ui.listWidget.itemWidget(item)
            if text:
                item.setHidden(not widget.repo_name.lower().startswith(text.lower()))
            else:
                item.setHidden(False)
