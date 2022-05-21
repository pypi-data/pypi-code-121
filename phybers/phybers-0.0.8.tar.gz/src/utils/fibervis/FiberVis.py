import sys
from PyQt5 import QtGui, QtWidgets, uic, QtCore
import WindowController

app = QtWidgets.QApplication(sys.argv)
fiber = WindowController.WindowController()
fiber.show()

sys.exit(app.exec_())


