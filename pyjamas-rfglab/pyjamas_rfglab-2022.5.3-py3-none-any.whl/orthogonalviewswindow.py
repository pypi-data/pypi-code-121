from PyQt5 import QtCore, QtWidgets, QtGui
from pyjamas.rimage.rimutils import rimutils
import os
import numpy

class OrthogonalViewsWindow(object):
    def __init__(self, pjs):
        super().__init__()
        self.pjs = pjs
    
    def setupUI(self, xWid, yWid):
        self.xWindow = xWid
        self.yWindow = yWid

        self.xWindow.setObjectName("xWidget")
        self.xWindow.setWindowTitle("xz")
        self.xWindow.other = self.yWindow
        self.xWindow.setWindowModality(QtCore.Qt.WindowModal)

        self.yWindow.setObjectName("yWidget")
        self.yWindow.setWindowTitle("yz")
        self.yWindow.other = self.xWindow
        self.yWindow.setWindowModality(QtCore.Qt.WindowModal)

        self.menubarYZ = QtWidgets.QMenuBar(self.yWindow)
        self.menubarYZ.setObjectName('menubarYZ')
        self.menuYZ = QtWidgets.QMenu(self.menubarYZ)
        self.menuYZ.setObjectName('menuYZ')
        self.menuYZ.setTitle('IO')
        self.menubarYZ.addMenu(self.menuYZ)
        self.menubarYZ.setGeometry(0, 0, 1183, 22)
        self.menubarYZ.setNativeMenuBar(False)
        
        self.menubarXZ = QtWidgets.QMenuBar(self.xWindow)
        self.menubarXZ.setObjectName('menubarXZ')
        self.menuXZ = QtWidgets.QMenu(self.menubarXZ)
        self.menuXZ.setObjectName('menuXZ')
        self.menuXZ.setTitle('IO')
        self.menubarXZ.addMenu(self.menuXZ)
        self.menubarXZ.setGeometry(0, 0, 1183, 22)
        self.menubarXZ.setNativeMenuBar(False)

        actionXZ = QtWidgets.QAction('Save XZ slice', self.xWindow)
        actionXZ.triggered.connect(lambda: self.saveView(self.zx))
        actionYZ = QtWidgets.QAction('Save YZ slice', self.yWindow)
        actionYZ.triggered.connect(lambda: self.saveView(self.zy))
        self.menuXZ.addAction(actionXZ)
        self.menuYZ.addAction(actionYZ)

        self.xLabel = QtWidgets.QLabel(self.xWindow)
        self.yLabel = QtWidgets.QLabel(self.yWindow)

        mainwindow_geometry: QtCore.QRect = self.pjs.MainWindow.geometry()

        self.xWindow.setGeometry(mainwindow_geometry.x(), mainwindow_geometry.y() + mainwindow_geometry.height(), self.xWindow.width(), self.xWindow.height())
        if os.name == "posix":  # Necessary to account for native menu bar in OSX.
            self.yWindow.setGeometry(mainwindow_geometry.x() + mainwindow_geometry.width(), mainwindow_geometry.y()-6, self.yWindow.width(), self.yWindow.height())
        else:
            self.yWindow.setGeometry(mainwindow_geometry.x() + mainwindow_geometry.width(), mainwindow_geometry.y(), self.yWindow.width(), self.yWindow.height())

        return True

    def reloadViews(self):
        self.zx = self.pjs.slices[:, self.pjs.slicetracker[1], :]
        self.zy = self.pjs.slices[:, :, self.pjs.slicetracker[0]].T

        self.displayViews(self.zx, self.zy)
        self.pjs.repaint()

        return True

    def displayViews(self, zx, zy):
        # Avoiding code repetition.
        # Alternatively, one could have a single input parameter to this function and call it twice for XZ and YZ views.
        images = [zx, zy]
        windows = [self.xWindow, self.yWindow]
        labels = [self.xLabel, self.yLabel]

        for anim, awin, alab in zip(images, windows, labels):
            awin.resize(anim.shape[1], anim.shape[0] + 22)
            alab.setGeometry(0, 22, anim.shape[1], anim.shape[0])
            img_16bit_to_8bit = rimutils.stretch(anim, self.pjs.min_pix_percentile, self.pjs.max_pix_percentile)
            img_16bit_to_8bit = numpy.array(img_16bit_to_8bit, dtype=numpy.uint8)
            qImg = QtGui.QImage(bytes(img_16bit_to_8bit), anim.shape[1], anim.shape[0], anim.shape[1], QtGui.QImage.Format_Grayscale8)
            pixmap = QtGui.QPixmap.fromImage(qImg)
            alab.setPixmap(pixmap)

        # These four lines return keyboard "sensitivity" to main window.
        self.xWindow.raise_()
        self.xWindow.activateWindow()
        self.pjs.MainWindow.raise_()
        self.pjs.MainWindow.activateWindow()

        return True
    
    def saveView(self, image_stack):
        fname: tuple = QtWidgets.QFileDialog.getSaveFileName(None, 'Save YZ slice ...', self.pjs.cwd,
                                                             filter='TIFF files (*.tif *.tiff)')
        if fname[0] == "":
            return False
        rimutils.write_stack(fname[0], image_stack)
        return True

class MyWidget(QtWidgets.QWidget):
    def __init__(self, pjs, parent=None):
        super(MyWidget, self).__init__(parent)
        self.pjs = pjs
        self.other = None

    def closeEvent(self, evnt):
        self.pjs.slicetracker = None
        self.pjs.repaint()

        super(MyWidget, self).closeEvent(evnt)
        
        if self.other is not None:
            self.other.close()

