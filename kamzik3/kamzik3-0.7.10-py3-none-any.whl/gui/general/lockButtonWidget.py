from PyQt5.QtCore import QSize, Qt
from PyQt5.QtGui import QCursor, QIcon, QPixmap
from PyQt5.QtWidgets import QPushButton, QSizePolicy


class LockButton(QPushButton):
    def __init__(self, *__args):
        super().__init__(*__args)
        size_policy = QSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        size_policy.setHorizontalStretch(0)
        size_policy.setVerticalStretch(0)
        size_policy.setHeightForWidth(self.sizePolicy().hasHeightForWidth())
        self.setSizePolicy(size_policy)
        self.setMaximumSize(QSize(16, 16))
        self.setCursor(QCursor(Qt.OpenHandCursor))
        self.setStyleSheet("QPushButton:flat {   border: none; }")
        self.setText("")
        icon = QIcon()
        icon.addPixmap(QPixmap(":/icons/icons/radio_off.png"), QIcon.Normal, QIcon.Off)
        icon.addPixmap(QPixmap(":/icons/icons/radio_on.png"), QIcon.Normal, QIcon.On)
        self.setIcon(icon)
        self.setIconSize(QSize(16, 16))
        self.setCheckable(True)
        self.setChecked(False)
        self.setDefault(False)
        self.setAutoExclusive(True)
        self.setFlat(True)
