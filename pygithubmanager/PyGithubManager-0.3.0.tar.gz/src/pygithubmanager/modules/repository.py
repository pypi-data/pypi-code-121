import sys
import traceback

import qtawesome as qta
import requests
from PySide6.QtCore import QUrl, QSize, QRunnable, Signal, Slot, QObject, QThreadPool
from PySide6.QtGui import QPixmap, QDesktopServices, QIcon, QImage
from PySide6.QtWidgets import QWidget, QListWidgetItem
from github import GithubException
from github.AuthenticatedUser import AuthenticatedUser
from github.Commit import Commit

from modules import User
from ui.widgets import Ui_repository
from utils import time_formatter, message
from widgets import CloneTemplate, FileTemplate, RepositoryListWidgetItem, EditRepository, IssueTemplate


class WorkerSignals(QObject):
    file = Signal(str, bool, str, int, str)
    finished = Signal()
    error = Signal(tuple)


class Worker(QRunnable):
    def __init__(self, content):
        """
        Worker to get the content of a repository

        Parameters
        ----------
        content
            The content of the repository
        """
        super(Worker, self).__init__()
        self.content = content
        self.signals = WorkerSignals()

    @Slot(str)
    def run(self):
        """
        Run the worker to get the content of a repository and emit the signals to update the UI
        """
        try:
            while self.content:
                file_content = self.content.pop(0)
                if file_content.type == "dir":
                    self.signals.file.emit(file_content.name, True, file_content.type, file_content.size, "")
                else:
                    self.signals.file.emit(file_content.name, False, file_content.type, file_content.size,
                                           file_content.html_url)
        except Exception:
            traceback.print_exc()
            exctype, value = sys.exc_info()[:2]
            self.signals.error.emit((exctype, value, traceback.format_exc()))
        finally:
            self.signals.finished.emit()


class Repository(QWidget):
    def __init__(self, repo, user):
        """
        Initialize the repository widget

        Parameters
        ----------
        repo : github.Repository.Repository
            The repository object
        user : User
            The user object
        """
        super(Repository, self).__init__()
        self.ui = Ui_repository()
        self.ui.setupUi(self)

        self.repository = repo

        self.user: User = user
        self.authenticated_user: AuthenticatedUser = user.get_data()

        self.clone = CloneTemplate(self.repository, self.user)
        self.edit_repo = QWidget()

        self.paths = [""]

        self.thread_pool = QThreadPool()

        self.load_data()
        self.load_code_data()
        self.load_issues()
        self.config_ui()

    def load_data(self):
        """
        Load repo data to ui widgets

        Raises
        ------
        Exception
            If there is no license
        """
        self.ui.repoLabel.setText(self.repository.full_name)
        self.watch()
        self.fork()
        self.star()

        self.ui.watchButton.clicked.connect(self.watch_button)
        self.ui.forkButton.clicked.connect(self.fork_button)
        self.ui.starButton.clicked.connect(self.star_button)

        try:
            self.ui.licenseWidget.setText(self.repository.get_license().license.name)
        except Exception:
            self.ui.licenseWidget.setText("No license")

    def config_ui(self):
        """
        Config ui widgets
        """
        self.setWindowTitle(self.repository.name)
        self.ui.tabWidget.setTabIcon(0, QIcon(qta.icon("fa5s.code").pixmap(10, 10)))
        self.ui.tabWidget.setTabIcon(1, QIcon(qta.icon("fa5s.dot-circle").pixmap(10, 10)))
        self.ui.commitsWidget.set_icon("fa5s.history")
        self.ui.licenseWidget.set_icon("fa5s.balance-scale")
        self.ui.configButton.setIcon(QIcon(qta.icon("ei.cog").pixmap(20, 20)))

        self.ui.descLabel.setText(self.repository.description)
        self.ui.codeButton.clicked.connect(lambda: self.clone.show())
        self.ui.filesListWidget.itemClicked.connect(self.on_click)
        self.ui.configButton.clicked.connect(self.edit_repo_window)
        self.ui.branchComboBox.setCurrentText(self.repository.default_branch)
        self.ui.branchComboBox.currentTextChanged.connect(self.branch_changed)
        self.branch_changed(self.repository.default_branch)

    def load_code_data(self):
        """
        Load repo data to ui widgets
        """
        self.ui.branchComboBox.clear()
        for branch in self.repository.get_branches():
            self.ui.branchComboBox.addItem(QPixmap(qta.icon("fa5s.code-branch").pixmap(10, 10)), branch.name)

        image = QImage()
        image.loadFromData(requests.get(self.repository.owner.avatar_url).content)
        self.ui.profileImageLabel.setPixmap(QPixmap(image).scaled(QSize(20, 20)))
        self.ui.usernameLabel.setText(self.repository.owner.login)
        try:
            commits = self.repository.get_commits()
            last_commit: Commit = commits[0]
            self.ui.commitLabel.setText(last_commit.commit.message)
            self.ui.numsLabel.setText(last_commit.commit.sha[:7])
            self.ui.timeLabel.setText(time_formatter("", time2=last_commit.commit.author.date))
            self.ui.commitsWidget.setText(
                str(commits.totalCount) + " commit" if commits.totalCount == 1 else str(
                    commits.totalCount) + " commits")
        except GithubException:
            print(GithubException)
            self.ui.commitLabel.setText("No commits")
            self.ui.numsLabel.setText("")
            self.ui.timeLabel.setText("")
            self.ui.commitsWidget.setText("0 commits")

    def load_issues(self):
        """
        Load issues to ui widgets
        """
        issues = self.repository.get_issues()
        for issue in issues:
            item = QListWidgetItem()
            widget = IssueTemplate(issue)
            item.setSizeHint(widget.sizeHint())
            self.ui.issuesListWidget.addItem(item)
            self.ui.issuesListWidget.setItemWidget(item, widget)

    def branch_changed(self, branch_name):
        """
        When branch changed, update files list

        Parameters
        ----------
        branch_name : str
            Branch name
        """
        content = self.repository.get_contents("/", ref=branch_name)
        self.load_content(content)

    def load_content(self, content):
        """
        Call the function to load content to ui widgets asynchronously and disables some UI elements

        Parameters
        ----------
        content
            Content to load
        """
        self.ui.branchComboBox.setDisabled(True)
        self.ui.configButton.setDisabled(True)
        self.ui.filesListWidget.clear()

        try:
            worker = Worker(content)
            worker.signals.file.connect(self.add_file)
            worker.signals.finished.connect(self.load_finished)

            if len(self.paths) > 1:
                item = RepositoryListWidgetItem("..", True, "", path=self.paths[-2],
                                                contents=self.repository.get_contents(
                                                    self.paths[-2], ref=self.ui.branchComboBox.currentText()))
                item.setText("..")
                item.setIcon(QIcon(qta.icon("fa5s.arrow-up").pixmap(10, 10)))
                self.ui.filesListWidget.addItem(item)

            self.thread_pool.start(worker)
        except GithubException as e:
            print(e)
            message('error', e.data['message'])

    def add_file(self, file_name, is_directory, content_type, content_size, url):
        """
        Add file to ui widgets

        Parameters
        ----------
        file_name : str
            File name
        is_directory : bool
            True if file is directory else False
        content_type : str
            File content type (e.g. dir, file, symlink)
        content_size : int
            File content size
        url : str
            GitHub file url

        Raises
        ------
        Exception
            If there is an error loading file
        """
        try:
            if is_directory:
                path = self.paths[-1] + "/" + file_name
                item = RepositoryListWidgetItem(
                    name=file_name, is_directory=True, url="", path=path,
                    contents=self.repository.get_contents(path, ref=self.ui.branchComboBox.currentText()))
            else:
                item = RepositoryListWidgetItem(name=file_name, is_directory=False, url=url)
            widget = FileTemplate(file_name, content_type, content_size)
            item.setSizeHint(widget.sizeHint())
            self.ui.filesListWidget.addItem(item)
            self.ui.filesListWidget.setItemWidget(item, widget)
        except Exception as e:
            message('error', e)

    def load_finished(self):
        """
        When loading finished, enables some UI elements
        """
        self.ui.branchComboBox.setDisabled(False)
        self.ui.configButton.setDisabled(False)

    def on_click(self, item):
        """
        When item clicked, update content if it is directory or open file if it is file

        Parameters
        ----------
        item : RepositoryListWidgetItem
            Item clicked
        """
        if item.isDirectory:
            if item.name == "..":
                self.paths.pop()
                self.load_content(item.contents)
            else:
                self.paths.append(item.path)
                self.load_content(item.contents)
        else:
            QDesktopServices.openUrl(QUrl(item.url))

    def edit_repo_window(self):
        """
        Open edit repository window
        """
        self.edit_repo = EditRepository(self.repository, self)
        self.edit_repo.show()

    def watch(self):
        """
        People subscribed to this repo
        """
        self.ui.watchButton.setText("Unwatch " + str(self.repository.subscribers_count)
                                    if self.repository in self.authenticated_user.get_watched()
                                    else "Watch " + str(self.repository.subscribers_count))
        self.ui.watchButton.setIcon(qta.icon("ei.eye-close") if self.repository in self.authenticated_user.get_watched()
                                    else qta.icon("ei.eye-open"))

        self.ui.watchingWidget.setText(str(self.repository.subscribers_count) + " watching")
        self.ui.watchingWidget.set_icon("fa5s.eye")

    def watch_button(self):
        """
        Watch/Unwatch repository
        """
        if self.repository in self.authenticated_user.get_watched():
            self.authenticated_user.remove_from_watched(self.repository)
        else:
            self.authenticated_user.add_to_watched(self.repository)
        self.watch()

    def fork(self):
        """
        Fork repository and forks count
        """
        if self.repository in self.authenticated_user.get_repos():
            self.ui.forkButton.setDisabled(True)
            self.ui.forkButton.setToolTip("You own this repository")

        self.ui.forkButton.setText("Fork " + str(self.repository.forks_count))
        self.ui.forkButton.setIcon(QPixmap(qta.icon("fa5s.code-branch").pixmap(15, 15)))

        self.ui.forksWidget.setText(
            str(self.repository.forks_count) + " fork" if self.repository.forks_count == 1 else
            str(self.repository.forks_count) + " forks")
        self.ui.forksWidget.set_icon("fa5s.code-branch")

    def fork_button(self):
        """
        Fork repository
        """
        self.authenticated_user.create_fork(self.repository)
        self.fork()

    def star(self):
        """
        Star repository and stars count
        """
        self.ui.starButton.setText("Starred " + str(self.repository.stargazers_count)
                                   if self.repository in self.authenticated_user.get_starred()
                                   else "Star " + str(self.repository.stargazers_count))
        self.ui.starButton.setIcon(QPixmap(
            qta.icon("fa5s.star", color='orange').pixmap(15, 15)
            if self.repository in self.authenticated_user.get_starred()
            else qta.icon("fa5s.star").pixmap(15, 15)))

        self.ui.starWidget.setText(
            str(self.repository.stargazers_count) + " star" if self.repository.stargazers_count == 1 else str(
                self.repository.stargazers_count) + " stars")
        self.ui.starWidget.set_icon("fa5s.star")

    def star_button(self):
        """
        Star repository
        """
        if self.repository in self.authenticated_user.get_starred():
            self.authenticated_user.remove_from_starred(self.repository)
        else:
            self.authenticated_user.add_to_starred(self.repository)
        self.star()
