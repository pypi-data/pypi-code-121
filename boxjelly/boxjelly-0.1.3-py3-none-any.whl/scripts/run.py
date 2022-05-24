"""
Entry point for the BoxJelly application.
"""

import sys

from PyQt5 import QtWidgets, QtGui, QtCore

from boxjelly.lib.constants import APP_NAME, APP_ORGANIZATION, CONTROL_PORT_DEFAULT, FRAME_RATE_DEFAULT, INCOMING_PORT_DEFAULT, INCOMING_TOPIC_DEFAULT, OUTGOING_PORT_DEFAULT, OUTGOING_TOPIC_DEFAULT
from boxjelly.lib.settings import SettingsManager
from boxjelly.ui.MainWindow import MainWindow


def start(argv):
    """Start the application"""
    # Create the application
    app = QtWidgets.QApplication(argv)
    
    QtCore.QSettings.setDefaultFormat(QtCore.QSettings.Format.IniFormat)
    init_settings()
    
    app.setApplicationName(APP_NAME)
    app.setOrganizationName(APP_ORGANIZATION)
    
    # Create the splash screen
    splash_logo = QtGui.QIcon(':icons/boxjelly_logo.svg').pixmap(256, 256)
    splash = QtWidgets.QSplashScreen(splash_logo)
    splash.show()
    
    # Create the main window
    window = MainWindow()
    window.show()
    splash.finish(window)
    
    # Start the application
    app.exec_()


def init_settings():
    """Initialize settings"""
    settings = SettingsManager.get_instance()
    
    settings.control_port = ('network/control_port', int, CONTROL_PORT_DEFAULT)
    settings.incoming_port = ('network/incoming_port', int, INCOMING_PORT_DEFAULT)
    settings.incoming_topic = ('network/incoming_topic', str, INCOMING_TOPIC_DEFAULT)
    settings.outgoing_port = ('network/outgoing_port', int, OUTGOING_PORT_DEFAULT)
    settings.outgoing_topic = ('network/outgoing_topic', str, OUTGOING_TOPIC_DEFAULT)
    
    settings.frame_rate = ('video/frame_rate', float, FRAME_RATE_DEFAULT)


def main():
    """Parse command line arguments and start"""
    start(sys.argv)


if __name__ == "__main__":
    main()
