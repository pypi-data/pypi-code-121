"""
    PyJAMAS is Just A More Awesome Siesta
    Copyright (C) 2018  Rodrigo Fernandez-Gonzalez (rodrigo.fernandez.gonzalez@utoronto.ca)

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""

from typing import Optional, Tuple
import sys

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
from PyQt5.QtCore import Qt as Qt
from PyQt5.QtWidgets import QDialog, QApplication, QVBoxLayout


class MatplotlibDialog(QDialog):
    _ZOOM_ACTION_INDEX_ = 5  # Index of the Zoom action in the NavigationToolbar (self.toolbar.actions()).

    def __init__(self, parent=None, figure: Optional[Figure] = None, title: str = '', toolbar_flag: bool = True):
        super(MatplotlibDialog, self).__init__(parent)

        # a figure instance to plot on
        self.figure: Figure = figure

        # this is the Canvas Widget that displays the `figure`
        # it takes the `figure` instance as a parameter to __init__
        self.canvas: FigureCanvas = FigureCanvas(self.figure)
        # Event handling: https://matplotlib.org/3.2.1/users/event_handling.html
        #self.canvas.mpl_connect('motion_notify_event', self.focus_preview_window)

        self.toolbar: NavigationToolbar = None

        if toolbar_flag:
            self.toolbar = NavigationToolbar(self.canvas, self)
        else:
            plt.rcParams['toolbar'] = 'None'

        # set the layout
        self.layout = QVBoxLayout()

        if toolbar_flag:
            self.layout.addWidget(self.toolbar)

        self.layout.addWidget(self.canvas)
        self.setLayout(self.layout)

        # Add title.
        self.setWindowTitle(title)
        self.window_size: Tuple[int, int] = (self.width(), self.height())

        # Remove close/maximize/minimize buttons, and leave title bar.
        # https://doc.qt.io/archives/qtjambi-4.5.2_01/com/trolltech/qt/core/Qt.WindowType.html
        self.setWindowFlags(Qt.CustomizeWindowHint | Qt.WindowTitleHint)

    def set_figure(self, figure: Optional[Figure] = None) -> bool:
        if self.figure is not None:
            plt.close(self.figure)

        self.figure = figure
        self.canvas.figure = self.figure
        self.canvas.setParent(None)
        self.canvas = FigureCanvas(self.figure)
        self.toolbar.canvas = self.canvas
        self.layout.addWidget(self.canvas)

        return True

    def get_figure(self) -> Figure:
        return self.figure

    def update_figure(self) -> bool:
        self.canvas.draw()
        #self.canvas.flush_events()

        return True


if __name__ == '__main__':
    app = QApplication(sys.argv)

    main = MatplotlibDialog()
    main.show()

    sys.exit(app.exec_())