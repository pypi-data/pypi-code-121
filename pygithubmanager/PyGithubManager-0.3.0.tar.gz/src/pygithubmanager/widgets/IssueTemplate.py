from PySide6.QtCore import QSize
from PySide6.QtWidgets import QWidget, QLabel
from github.Issue import Issue

from ui.widgets import Ui_IssueTemplate
from utils import time_formatter


class IssueTemplate(QWidget):
    def __init__(self, issue: Issue):
        """
        IssueTemplate is a widget that shows the information of an issue.

        Parameters
        ----------
        issue : Issue
            The issue to show.
        """
        super(IssueTemplate, self).__init__()
        self.ui = Ui_IssueTemplate()
        self.ui.setupUi(self)

        self.issue: Issue = issue

        self.fill()

    def fill(self):
        """
        Fills the widget with the information of the issue.
        """
        self.ui.statusNameWidget.setText(self.issue.title)
        self.ui.statusNameWidget.set_text_style(bold=True)
        self.ui.statusNameWidget.set_icon("msc.issues", "green", QSize(20, 20))

        self.ui.commentsWidget.setText(str(self.issue.comments))
        self.ui.commentsWidget.set_icon("fa5.comment-alt")

        for label in self.issue.labels:
            label_label = QLabel(label.name)
            label_label.setStyleSheet(
                "border: 1px solid #{color}; border-radius: 10px; padding: 1px;".format(color=label.color))
            self.ui.labelsLayout.addWidget(label_label)

        self.ui.issueNumberLabel.setText("#" + str(self.issue.number))
        self.ui.openedLabel.setText(time_formatter("opened", time2=self.issue.created_at))
        self.ui.byLabel.setText("by " + self.issue.user.login)
