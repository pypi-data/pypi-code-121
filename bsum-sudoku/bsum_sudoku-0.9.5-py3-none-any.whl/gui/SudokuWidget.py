from sudoku.core import sudoku_grid

from math import floor
from PyQt5 import QtCore, QtGui, QtWidgets

class SudokuWidget(QtWidgets.QWidget):
    solved = QtCore.pyqtSignal(bool)

    def __init__(
        self,
        parent: QtWidgets.QWidget = None,
        grid = sudoku_grid()
    ) -> None:

        super(SudokuWidget, self).__init__(parent)
        self.grid = grid

        self.grid_widget = \
            [[QtWidgets.QLineEdit(self) for _ in range(9)] for _ in range(9)]

        self.setMinimumSize(500, 500)

        for (i, r) in enumerate(self.grid_widget):
            for (j, w) in enumerate(r):
                w.setAlignment(QtCore.Qt.AlignCenter)
                w.setMaxLength(1)
                w.setProperty("my_position", 9 * i + j)
                w.setValidator(QtGui.QIntValidator(1, 9, self))

                font = w.font()
                font.setBold(True)
                font.setPointSize(floor(font.pointSize() * 1.6))

                w.setFont(font)

                w.textEdited.connect(self.on_text_edit)

        self.update_widget_content()

    def update_widget_content(self) -> None:
        for (i, r) in enumerate(self.grid_widget):
            for (j, w) in enumerate(r):
                val = self.grid.grid[9 * i + j]

                if val != 0:
                    w.setText(str(val))
                else:
                    w.clear()

    def paintEvent(self, _: QtGui.QPaintEvent) -> None:
        margin = 3

        hoffset     = 0
        woffset     = 0
        square_size = 0

        main_rect = self.rect() \
            - QtCore.QMargins(4 * margin, 4 * margin, 4 * margin, 4 * margin)

        if self.height() < self.width():
            square_size = main_rect.height() // 9
            woffset     = (self.width() - 9 * square_size) // 2
        else:
            square_size = main_rect.width() // 9
            hoffset     = (self.height() - 9 * square_size) // 2

        painter = QtGui.QPainter(self)
        painter.setRenderHint(QtGui.QPainter.Antialiasing)

        pen = painter.pen()
        pen.setWidth(margin)
        painter.setPen(pen)

        for i in range(3):
            for j in range(3):
                painter.drawRect(
                    3 * j * square_size + j * margin + woffset + margin,
                    3 * i * square_size + i * margin + hoffset + margin,
                    3 * square_size + margin,
                    3 * square_size + margin
                )

        for (i, r) in enumerate(self.grid_widget):
            for (j, w) in enumerate(r):
                w.setGeometry(
                    j * square_size + (j // 3) * margin + woffset + margin,
                    i * square_size + (i // 3) * margin + hoffset + margin,
                    square_size,
                    square_size
                )

        self.updateGeometry()

    @QtCore.pyqtSlot(str)
    def on_text_edit(self, string: str) -> None:
        i = self.sender().property("my_position")

        if string:
            self.grid.grid[i] = int(string)
        else:
            self.grid.grid[i] = 0

    @QtCore.pyqtSlot()
    def clear(self) -> None:
        self.grid = sudoku_grid([0] * 81)
        self.update_widget_content()

    @QtCore.pyqtSlot()
    def solve(self) -> None:
        try:
            self.grid.solve()
            self.solved.emit(True)
        except RuntimeError:
            self.solved.emit(False)

        self.update_widget_content()
