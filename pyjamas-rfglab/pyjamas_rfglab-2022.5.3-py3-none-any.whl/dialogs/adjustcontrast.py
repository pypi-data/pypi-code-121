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

from matplotlib.figure import Figure
from matplotlib.axes import Axes
import numpy
from PyQt5 import QtCore, QtWidgets

from pyjamas.dialogs.matplotlibdialog import MatplotlibDialog
from pyjamas.pjscore import PyJAMAS
from pyjamas.rimage.rimutils import rimutils


class AdjustContrastDialog(object):
    min_pix_percentile: int = 0
    max_pix_percentile: int = 100

    def __init__(self, pjs: PyJAMAS):
        super().__init__()

        self.pjs = pjs
        self.histogram_window: MatplotlibDialog = None

        self.prev_min_pix_percentile: int = self.pjs.min_pix_percentile
        self.prev_max_pix_percentile: int = self.pjs.max_pix_percentile

    def setupUi(self, Dialog, min_percentile=None, max_percentile=None):

        if min_percentile is None or min_percentile is False:
            min_percentile = AdjustContrastDialog.min_pix_percentile

        if max_percentile is None or max_percentile is False:
            max_percentile = AdjustContrastDialog.max_pix_percentile

        self.dialog = Dialog
        self.dialog.setObjectName("Dialog")
        self.dialog.resize(221, 245)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Ignored, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.dialog.sizePolicy().hasHeightForWidth())
        self.dialog.setSizePolicy(sizePolicy)
        self.buttonBox = QtWidgets.QDialogButtonBox(self.dialog)
        self.buttonBox.setGeometry(QtCore.QRect(-150, 200, 341, 32))
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.Cancel | QtWidgets.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName("buttonBox")
        self.groupBox_3 = QtWidgets.QGroupBox(self.dialog)
        self.groupBox_3.setGeometry(QtCore.QRect(20, 110, 181, 91))
        self.groupBox_3.setObjectName("groupBox_3")
        self.sbmin = QtWidgets.QSpinBox(self.groupBox_3)
        self.sbmin.setGeometry(QtCore.QRect(5, 60, 48, 24))
        self.sbmin.setObjectName("sbmin")
        self.sbmin.setMinimum(0)
        self.sbmin.setMaximum(100)
        self.sbmin.setValue(min_percentile)
        self.sbmax = QtWidgets.QSpinBox(self.groupBox_3)
        self.sbmax.setGeometry(QtCore.QRect(130, 60, 48, 24))
        self.sbmax.setObjectName("sbmax")
        self.sbmax.setMinimum(0)
        self.sbmax.setMaximum(100)
        self.sbmax.setValue(max_percentile)
        self.pushButton = QtWidgets.QPushButton(self.groupBox_3)
        self.pushButton.setGeometry(QtCore.QRect(55, 57, 71, 32))
        self.pushButton.setObjectName("pushButton")
        self.minSlider = QtWidgets.QSlider(self.groupBox_3)
        self.minSlider.setOrientation(QtCore.Qt.Horizontal)
        self.minSlider.setGeometry(QtCore.QRect(4, 20, 171, 22))
        self.minSlider.setObjectName("minSlider")
        self.minSlider.setRange(0, 100)
        self.minSlider.setValue(min_percentile)
        self.minSlider.setStyleSheet("""
                                        QSlider::groove:horizontal {
                                        border: 1px solid #bbb;
                                        background: white;
                                        height: 10px;
                                        border-radius: 4px;
                                        }

                                        QSlider::sub-page:horizontal {
                                        background: qlineargradient(x1: 0, y1: 0,    x2: 0, y2: 1,
                                            stop: 0 #66e, stop: 1 #bbf);
                                        background: qlineargradient(x1: 0, y1: 0.2, x2: 1, y2: 1,
                                            stop: 0 #bbf, stop: 1 #55f);
                                        border: 1px solid #777;
                                        height: 10px;
                                        border-radius: 4px;
                                        }

                                        QSlider::add-page:horizontal {
                                        background: #fff;
                                        border: 1px solid #777;
                                        height: 10px;
                                        border-radius: 4px;
                                        }

                                        QSlider::handle:horizontal {
                                        background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                                            stop:0 #eee, stop:1 #ccc);
                                        border: 1px solid #777;
                                        width: 13px;
                                        margin-top: -2px;
                                        margin-bottom: -2px;
                                        border-radius: 4px;
                                        }

                                        QSlider::handle:horizontal:hover {
                                        background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                                            stop:0 #fff, stop:1 #ddd);
                                        border: 1px solid #444;
                                        border-radius: 4px;
                                        }

                                        QSlider::sub-page:horizontal:disabled {
                                        background: #bbb;
                                        border-color: #999;
                                        }

                                        QSlider::add-page:horizontal:disabled {
                                        background: #eee;
                                        border-color: #999;
                                        }

                                        QSlider::handle:horizontal:disabled {
                                        background: #eee;
                                        border: 1px solid #aaa;
                                        border-radius: 4px;
                                        }
                                    """)

        self.maxSlider = QtWidgets.QSlider(self.groupBox_3)
        self.maxSlider.setOrientation(QtCore.Qt.Horizontal)
        self.maxSlider.setGeometry(QtCore.QRect(4, 40, 171, 22))
        self.maxSlider.setObjectName("maxSlider")
        self.maxSlider.setRange(0, 100)
        self.maxSlider.setValue(max_percentile)
        self.maxSlider.setStyleSheet("""
                                        QSlider::groove:horizontal {
                                        border: 1px solid #bbb;
                                        background: white;
                                        height: 10px;
                                        border-radius: 4px;
                                        }
                                        
                                        QSlider::sub-page:horizontal {
                                        background: qlineargradient(x1: 0, y1: 0,    x2: 0, y2: 1,
                                            stop: 0 #e66, stop: 1 #fbb);
                                        background: qlineargradient(x1: 0, y1: 0.2, x2: 1, y2: 1,
                                            stop: 0 #fbb, stop: 1 #f55);
                                        border: 1px solid #777;
                                        height: 10px;
                                        border-radius: 4px;
                                        }
                                        
                                        QSlider::add-page:horizontal {
                                        background: #fff;
                                        border: 1px solid #777;
                                        height: 10px;
                                        border-radius: 4px;
                                        }
                                        
                                        QSlider::handle:horizontal {
                                        background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                                            stop:0 #eee, stop:1 #ccc);
                                        border: 1px solid #777;
                                        width: 13px;
                                        margin-top: -2px;
                                        margin-bottom: -2px;
                                        border-radius: 4px;
                                        }
                                        
                                        QSlider::handle:horizontal:hover {
                                        background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                                            stop:0 #fff, stop:1 #ddd);
                                        border: 1px solid #444;
                                        border-radius: 4px;
                                        }
                                        
                                        QSlider::sub-page:horizontal:disabled {
                                        background: #bbb;
                                        border-color: #999;
                                        }
                                        
                                        QSlider::add-page:horizontal:disabled {
                                        background: #eee;
                                        border-color: #999;
                                        }
                                        
                                        QSlider::handle:horizontal:disabled {
                                        background: #eee;
                                        border: 1px solid #aaa;
                                        border-radius: 4px;
                                        }
                                    """)

        self.histogram_window = MatplotlibDialog(self.dialog, self.generate_figure(), '', False)
        self.histogram_window.setGeometry(QtCore.QRect(10, 10, 201, 91))
        self.histogram_window.setObjectName("histogram")

        self.retranslateUi()
        self.pushButton.pressed.connect(self._auto_adjust)
        self.buttonBox.rejected.connect(self.reject)
        self.buttonBox.accepted.connect(self.accept)
        self.sbmin.valueChanged.connect(self._update_min_sb)
        self.sbmax.valueChanged.connect(self._update_max_sb)
        self.minSlider.valueChanged.connect(self._update_min_slider)
        self.maxSlider.valueChanged.connect(self._update_max_slider)
        QtCore.QMetaObject.connectSlotsByName(self.dialog)

    def accept(self):
        AdjustContrastDialog.min_pix_percentile = self.sbmin.value()
        AdjustContrastDialog.max_pix_percentile = self.sbmax.value()

        self.dialog.accept()

    def reject(self):
        self.pjs.min_pix_percentile = self.prev_min_pix_percentile
        self.pjs.max_pix_percentile = self.prev_max_pix_percentile

        self.pjs.displayData()

        self.dialog.reject()

    def retranslateUi(self):
        _translate = QtCore.QCoreApplication.translate
        self.dialog.setWindowTitle(_translate("Dialog", "Adjust contrast"))
        self.groupBox_3.setTitle(_translate("Dialog", "Min and max percentile"))
        self.pushButton.setText(_translate("Dialog", "Auto"))

    def _update_min_sb(self) -> bool:
        self.minSlider.valueChanged.disconnect()
        self.maxSlider.valueChanged.disconnect()
        self.sbmin.valueChanged.disconnect()
        self.sbmax.valueChanged.disconnect()

        v = self.sbmin.value()

        if self.sbmax.value() < v:
            self.sbmax.setValue(v)
            self.maxSlider.setValue(v)
        self.minSlider.setValue(v)

        self.minSlider.valueChanged.connect(self._update_min_slider)
        self.maxSlider.valueChanged.connect(self._update_max_slider)
        self.sbmin.valueChanged.connect(self._update_min_sb)
        self.sbmax.valueChanged.connect(self._update_max_sb)

        self.update_curslice()
        self._update_histogram()
        self.dialog.raise_()
        self.dialog.activateWindow()

        return True

    def _update_max_sb(self) -> bool:
        self.minSlider.valueChanged.disconnect()
        self.maxSlider.valueChanged.disconnect()
        self.sbmin.valueChanged.disconnect()
        self.sbmax.valueChanged.disconnect()

        v = self.sbmax.value()

        if self.sbmin.value() > v:
            self.sbmin.setValue(v)
            self.minSlider.setValue(v)
        self.maxSlider.setValue(v)

        self.minSlider.valueChanged.connect(self._update_max_slider)
        self.maxSlider.valueChanged.connect(self._update_max_slider)
        self.sbmin.valueChanged.connect(self._update_min_sb)
        self.sbmax.valueChanged.connect(self._update_max_sb)

        self.update_curslice()
        self._update_histogram()
        self.dialog.raise_()
        self.dialog.activateWindow()

        return True

    def _update_min_slider(self) -> bool:
        self.minSlider.valueChanged.disconnect()
        self.maxSlider.valueChanged.disconnect()
        self.sbmin.valueChanged.disconnect()
        self.sbmax.valueChanged.disconnect()

        v = self.minSlider.value()

        if self.maxSlider.value() >= v:
            self.sbmin.setValue(v)

        else:
            self.maxSlider.setValue(v)
            self.sbmin.setValue(v)
            self.sbmax.setValue(v)

        self.minSlider.valueChanged.connect(self._update_min_slider)
        self.maxSlider.valueChanged.connect(self._update_max_slider)
        self.sbmin.valueChanged.connect(self._update_min_sb)
        self.sbmax.valueChanged.connect(self._update_max_sb)

        self.update_curslice()
        self._update_histogram()
        self.dialog.raise_()
        self.dialog.activateWindow()

        return True

    def _update_max_slider(self) -> bool:
        self.minSlider.valueChanged.disconnect()
        self.maxSlider.valueChanged.disconnect()
        self.sbmin.valueChanged.disconnect()
        self.sbmax.valueChanged.disconnect()

        v = self.maxSlider.value()

        if self.minSlider.value() <= v:
            self.sbmax.setValue(v)

        else:
            self.minSlider.setValue(v)
            self.sbmax.setValue(v)
            self.sbmin.setValue(v)

        self.minSlider.valueChanged.connect(self._update_min_slider)
        self.maxSlider.valueChanged.connect(self._update_max_slider)
        self.sbmin.valueChanged.connect(self._update_min_sb)
        self.sbmax.valueChanged.connect(self._update_max_sb)

        self.update_curslice()
        self._update_histogram()
        self.dialog.raise_()
        self.dialog.activateWindow()

        return True

    def _auto_adjust(self) -> bool:
        self.sbmin.setValue(50)
        self.sbmax.setValue(99)

        return True

    def parameters(self) -> dict:
        # AdjustContrastDialog.min_pix_percentile = self.sbmin.value()
        # AdjustContrastDialog.max_pix_percentile = self.sbmax.value()

        return {'min_percentile': self.sbmin.value(),
                         'max_percentile': self.sbmax.value()}

    def update_curslice(self) -> bool:
        parameters = self.parameters()

        self.pjs.min_pix_percentile = parameters.get('min_percentile', 0)
        self.pjs.max_pix_percentile = parameters.get('max_percentile', 100)

        self.pjs.displayData()

        return True

    def _update_histogram(self) -> bool:
        if self.line_min is not None and self.line_max is not None:
            self.line_min.pop(0).remove()
            self.line_max.pop(0).remove()

            ax = self.histogram_window.figure.gca()

            self._paint_lines(ax)

            self.histogram_window.canvas.draw()

        return True

    def generate_figure(self) -> Figure:
        figure = rimutils.histogram_figure(self.pjs.imagedata, False)
        ax = figure.gca()

        ylimits = ax.get_ylim()

        self._paint_lines(ax)

        #ax.set_xlim((0, self.pjs.imagedata.max()))

        ax.set_ylim(ylimits)

        ax.get_xaxis().set_visible(False)
        ax.get_yaxis().set_visible(False)

        ax.spines['right'].set_visible(False)
        ax.spines['top'].set_visible(False)

        return figure

    def _paint_lines(self, ax: Axes) -> bool:
        min_val = numpy.percentile(self.pjs.imagedata, self.pjs.min_pix_percentile)
        max_val = numpy.percentile(self.pjs.imagedata, self.pjs.max_pix_percentile)

        self.line_min = ax.plot((min_val, min_val), (0, 1), 'b')
        self.line_max = ax.plot((max_val, max_val), (0, 1), 'r')

        return True