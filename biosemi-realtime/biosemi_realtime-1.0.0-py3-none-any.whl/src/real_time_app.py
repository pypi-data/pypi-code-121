import src.main.main_window as btmw
from PyQt5 import QtWidgets
from PyQt5.QtCore import QObject
import sys
__author__ = 'jaime undurraga'


class UserInterface(QObject):
    def __init__(self, _reactor):
        super(UserInterface, self).__init__()
        self.main_window = btmw.BiosemiRealTimeMainWindow(_reactor)
        self.bio_reader = Brt.BiosemiFactory(_reactor)
        self.initialize()

    def initialize(self):
        pb_start = self.main_window.findChild(QtWidgets.QPushButton, 'pb_start')
        pb_start.clicked.connect(self.start)

        pb_stop = self.main_window.findChild(QtWidgets.QPushButton, 'pb_stop')
        pb_stop.clicked.connect(self.stop)

        sb_input_offset = self.main_window.findChild(QtWidgets.QLineEdit, 'qt_spin_box_channel_offset')
        sb_input_offset.textChanged.connect(self.send_input_offset)

        sb_average_offset = self.main_window.findChild(QtWidgets.QLineEdit, 'qt_spin_box_channel_average_offset')
        sb_average_offset.textChanged.connect(self.send_average_offset)

    def send_input_offset(self):
        sb_input_offset = self.main_window.findChild(QtWidgets.QLineEdit, 'qt_spin_box_channel_offset')
        self.bio_reader.update_input_offset(float(sb_input_offset.text()))

    def send_average_offset(self):
        sb_average_offset = self.main_window.findChild(QtWidgets.QLineEdit, 'qt_spin_box_channel_average_offset')
        self.bio_reader.update_average_offset(float(sb_average_offset.text()))

    def start(self):
        settings = self.main_window.get_current_settings()
        text_edit = self.main_window.findChild(QtWidgets.QTextEdit, 'console')
        text_edit.clear()
        self.bio_reader.start(settings)

    def stop(self):
        self.bio_reader.stop()


def close_main_window():
    reactor.stop()


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    app.setStyle(QtWidgets.QStyleFactory.create('Fusion'))
    app.setStyleSheet('QWidget{border: 1px solid gray; background-color: black; color: white}')
    import qt5reactor
    if 'twisted.internet.reactor' in sys.modules:
        del sys.modules['twisted.internet.reactor']
    qt5reactor.install()
    from twisted.internet import reactor
    import src.main.biosemiTcpRealTime as Brt
    reactor.suggestThreadPoolSize(30)
    ui = UserInterface(reactor)
    reactor.run()
