from sudoku.gui import MainWindow

from PyQt5 import QtWidgets
import sys

def main(argv: list[str]) -> int:
    app = QtWidgets.QApplication(argv)

    main = MainWindow()
    main.show()

    return app.exec()

sys.exit(main(sys.argv))
