# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'mainwindow.ui'
##
## Created by: Qt User Interface Compiler version 6.3.0
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (QCoreApplication, QMetaObject, QRect,
                            QSize, Qt)
from PySide6.QtGui import (QAction, QFont, QIcon)
from PySide6.QtWidgets import (QHBoxLayout, QLabel, QLayout,
                               QMenu, QMenuBar, QPushButton,
                               QSizePolicy, QSpacerItem, QStatusBar, QTabWidget,
                               QVBoxLayout, QWidget)

from widgets.IconLabel import IconLabel


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        if not MainWindow.objectName():
            MainWindow.setObjectName(u"MainWindow")
        MainWindow.resize(1020, 677)
        self.actionAbout = QAction(MainWindow)
        self.actionAbout.setObjectName(u"actionAbout")
        self.actionAyuda = QAction(MainWindow)
        self.actionAyuda.setObjectName(u"actionAyuda")
        self.actionExit = QAction(MainWindow)
        self.actionExit.setObjectName(u"actionExit")
        self.actionReload = QAction(MainWindow)
        self.actionReload.setObjectName(u"actionReload")
        self.centralwidget = QWidget(MainWindow)
        self.centralwidget.setObjectName(u"centralwidget")
        self.horizontalLayout = QHBoxLayout(self.centralwidget)
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.verticalLayout_2 = QVBoxLayout()
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.verticalLayout_2.setSizeConstraint(QLayout.SetFixedSize)
        self.profileImageLabel = QLabel(self.centralwidget)
        self.profileImageLabel.setObjectName(u"profileImageLabel")
        sizePolicy = QSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.profileImageLabel.sizePolicy().hasHeightForWidth())
        self.profileImageLabel.setSizePolicy(sizePolicy)

        self.verticalLayout_2.addWidget(self.profileImageLabel)

        self.nameLabel = QLabel(self.centralwidget)
        self.nameLabel.setObjectName(u"nameLabel")
        font = QFont()
        font.setPointSize(11)
        font.setBold(True)
        self.nameLabel.setFont(font)
        self.nameLabel.setAlignment(Qt.AlignLeading | Qt.AlignLeft | Qt.AlignVCenter)

        self.verticalLayout_2.addWidget(self.nameLabel)

        self.userNameLabel = QLabel(self.centralwidget)
        self.userNameLabel.setObjectName(u"userNameLabel")
        sizePolicy1 = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)
        sizePolicy1.setHorizontalStretch(0)
        sizePolicy1.setVerticalStretch(0)
        sizePolicy1.setHeightForWidth(self.userNameLabel.sizePolicy().hasHeightForWidth())
        self.userNameLabel.setSizePolicy(sizePolicy1)
        self.userNameLabel.setAlignment(Qt.AlignLeading | Qt.AlignLeft | Qt.AlignVCenter)

        self.verticalLayout_2.addWidget(self.userNameLabel)

        self.bioLabel = QLabel(self.centralwidget)
        self.bioLabel.setObjectName(u"bioLabel")
        sizePolicy1.setHeightForWidth(self.bioLabel.sizePolicy().hasHeightForWidth())
        self.bioLabel.setSizePolicy(sizePolicy1)
        self.bioLabel.setAlignment(Qt.AlignLeading | Qt.AlignLeft | Qt.AlignVCenter)

        self.verticalLayout_2.addWidget(self.bioLabel)

        self.editProfileButton = QPushButton(self.centralwidget)
        self.editProfileButton.setObjectName(u"editProfileButton")

        self.verticalLayout_2.addWidget(self.editProfileButton)

        self.companyWidget = IconLabel(self.centralwidget)
        self.companyWidget.setObjectName(u"companyWidget")
        sizePolicy2 = QSizePolicy(QSizePolicy.Fixed, QSizePolicy.Preferred)
        sizePolicy2.setHorizontalStretch(0)
        sizePolicy2.setVerticalStretch(0)
        sizePolicy2.setHeightForWidth(self.companyWidget.sizePolicy().hasHeightForWidth())
        self.companyWidget.setSizePolicy(sizePolicy2)

        self.verticalLayout_2.addWidget(self.companyWidget)

        self.locationWidget = IconLabel(self.centralwidget)
        self.locationWidget.setObjectName(u"locationWidget")
        sizePolicy2.setHeightForWidth(self.locationWidget.sizePolicy().hasHeightForWidth())
        self.locationWidget.setSizePolicy(sizePolicy2)

        self.verticalLayout_2.addWidget(self.locationWidget)

        self.twitterWidget = IconLabel(self.centralwidget)
        self.twitterWidget.setObjectName(u"twitterWidget")
        sizePolicy2.setHeightForWidth(self.twitterWidget.sizePolicy().hasHeightForWidth())
        self.twitterWidget.setSizePolicy(sizePolicy2)

        self.verticalLayout_2.addWidget(self.twitterWidget)

        self.joinedWidget = IconLabel(self.centralwidget)
        self.joinedWidget.setObjectName(u"joinedWidget")
        sizePolicy2.setHeightForWidth(self.joinedWidget.sizePolicy().hasHeightForWidth())
        self.joinedWidget.setSizePolicy(sizePolicy2)

        self.verticalLayout_2.addWidget(self.joinedWidget)

        self.verticalSpacer = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)

        self.verticalLayout_2.addItem(self.verticalSpacer)

        self.infoButton = QPushButton(self.centralwidget)
        self.infoButton.setObjectName(u"infoButton")
        sizePolicy.setHeightForWidth(self.infoButton.sizePolicy().hasHeightForWidth())
        self.infoButton.setSizePolicy(sizePolicy)

        self.verticalLayout_2.addWidget(self.infoButton)


        self.horizontalLayout.addLayout(self.verticalLayout_2)

        self.verticalLayout = QVBoxLayout()
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.mainTabWidget = QTabWidget(self.centralwidget)
        self.mainTabWidget.setObjectName(u"mainTabWidget")
        self.mainTabWidget.setTabPosition(QTabWidget.North)
        self.mainTabWidget.setTabShape(QTabWidget.Rounded)
        self.mainTabWidget.setIconSize(QSize(16, 16))
        self.mainTabWidget.setElideMode(Qt.ElideMiddle)
        self.mainTabWidget.setDocumentMode(False)
        self.mainTabWidget.setTabsClosable(False)
        self.mainTabWidget.setMovable(False)
        self.overviewTab = QWidget()
        self.overviewTab.setObjectName(u"overviewTab")
        icon = QIcon()
        icon.addFile(u"../resources/icons/dark open book.png", QSize(), QIcon.Normal, QIcon.Off)
        self.mainTabWidget.addTab(self.overviewTab, icon, "")
        self.repositoriesTab = QWidget()
        self.repositoriesTab.setObjectName(u"repositoriesTab")
        icon1 = QIcon()
        icon1.addFile(u"../resources/icons/dark repo.png", QSize(), QIcon.Normal, QIcon.Off)
        self.mainTabWidget.addTab(self.repositoriesTab, icon1, "")
        self.localTab = QWidget()
        self.localTab.setObjectName(u"localTab")
        icon2 = QIcon()
        icon2.addFile(u"../resources/icons/dark star.png", QSize(), QIcon.Normal, QIcon.Off)
        self.mainTabWidget.addTab(self.localTab, icon2, "")

        self.verticalLayout.addWidget(self.mainTabWidget)


        self.horizontalLayout.addLayout(self.verticalLayout)

        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QMenuBar(MainWindow)
        self.menubar.setObjectName(u"menubar")
        self.menubar.setGeometry(QRect(0, 0, 1020, 22))
        self.menuHelp = QMenu(self.menubar)
        self.menuHelp.setObjectName(u"menuHelp")
        self.menuMenu = QMenu(self.menubar)
        self.menuMenu.setObjectName(u"menuMenu")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QStatusBar(MainWindow)
        self.statusbar.setObjectName(u"statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.menubar.addAction(self.menuMenu.menuAction())
        self.menubar.addAction(self.menuHelp.menuAction())
        self.menuHelp.addAction(self.actionAyuda)
        self.menuHelp.addSeparator()
        self.menuHelp.addAction(self.actionAbout)
        self.menuMenu.addAction(self.actionReload)
        self.menuMenu.addSeparator()
        self.menuMenu.addAction(self.actionExit)

        self.retranslateUi(MainWindow)

        self.mainTabWidget.setCurrentIndex(0)

        QMetaObject.connectSlotsByName(MainWindow)
    # setupUi

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QCoreApplication.translate("MainWindow", u"GitHub Manager", None))
        self.actionAbout.setText(QCoreApplication.translate("MainWindow", u"Acerca de", None))
        self.actionAyuda.setText(QCoreApplication.translate("MainWindow", u"Ayuda de GitHub Manager", None))
        self.actionExit.setText(QCoreApplication.translate("MainWindow", u"Exit", None))
        self.actionReload.setText(QCoreApplication.translate("MainWindow", u"Reload", None))
        # if QT_CONFIG(shortcut)
        self.actionReload.setShortcut(QCoreApplication.translate("MainWindow", u"Ctrl+R", None))
        # endif // QT_CONFIG(shortcut)
        self.profileImageLabel.setText("")
        self.nameLabel.setText(QCoreApplication.translate("MainWindow", u"name", None))
        self.userNameLabel.setText(QCoreApplication.translate("MainWindow", u"username", None))
        self.bioLabel.setText(QCoreApplication.translate("MainWindow", u"bio", None))
        self.editProfileButton.setText(QCoreApplication.translate("MainWindow", u"Edit profile", None))
        self.infoButton.setText("")
        self.mainTabWidget.setTabText(self.mainTabWidget.indexOf(self.overviewTab),
                                      QCoreApplication.translate("MainWindow", u"Overview", None))
        self.mainTabWidget.setTabText(self.mainTabWidget.indexOf(self.repositoriesTab),
                                      QCoreApplication.translate("MainWindow", u"Repositories", None))
        self.mainTabWidget.setTabText(self.mainTabWidget.indexOf(self.localTab),
                                      QCoreApplication.translate("MainWindow", u"Local", None))
        self.menuHelp.setTitle(QCoreApplication.translate("MainWindow", u"Help", None))
        self.menuMenu.setTitle(QCoreApplication.translate("MainWindow", u"Menu", None))
    # retranslateUi

