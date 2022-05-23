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

import numpy
from PyQt5 import QtCore, QtWidgets
import skimage.filters as skif

from pyjamas.pjscore import PyJAMAS
from pyjamas.pjscore import undo_modes
from pyjamas.rimage.rimcore import rimage
from pyjamas.rimage.rimutils import rimutils
import pyjamas.rutils as rutils

class PJSEventFilter(QtCore.QObject):
    POLYLINE_MOVE_STEP: int = 1
    INFLATE_GAUSSIAN_SIGMA: int = 2
    INITIAL_BALLOON_FORCE: float = 0.
    BALLOON_FORCE_INCREMENT: float = 0.1
    BALLOON_FORCE_INCREMENT_DELAY: float = 100  # how frequently to change the balloon force when the mouse button is pressed (in msec).

    def __init__(self, ui):
        """

        :type ui: PyJAMAS
        """
        super().__init__()

        self.pjs: PyJAMAS = ui
        self.x_prev: int = -1
        self.y_prev: int = -1
        self.x: int = -1
        self.y: int = -1
        self.balloon_timer: QtCore.QTimer = QtCore.QTimer(self)
        self.balloon_timer.timeout.connect(self.balloon_timer_function)
        self.balloon_force: float = self.INITIAL_BALLOON_FORCE

    def eventFilter(self, source, event: QtCore.QEvent):
        # sourcery skip: hoist-statement-from-if, merge-nested-ifs
        """
        Returns False for events that should not be processed, and the event itself otherwise.
        :param source:
        :param event:
        :return:
        """

        # IMPORTANT!!!!! ------------
        # CAPTURE MOUSE EVENTS HERE!!! SEE BELOW (elif) FOR KEYBOARD EVENTS.
        if type(source) == QtWidgets.QWidget:
            # Event coordinates.
            # if event.type() == QtCore.QEvent.MouseButtonPress:
            if event.type() in (QtCore.QEvent.MouseMove, QtCore.QEvent.MouseButtonPress, QtCore.QEvent.MouseButtonRelease):
                thepoint = self.pjs.gView.mapToScene(event.x(), event.y())

                # The mouse position is determined as the floor of the current floating point position
                # (using int would shift the coordinate to the one below or to the right before moving the
                # mouse into that pixel).
                self.x, self.y = (int(numpy.floor(thepoint.x())), int(numpy.floor(thepoint.y())))

                # Check for boundaries.
                if self.x < 0:
                    self.x = 0
                elif self.x >= self.pjs.width:
                    self.x = self.pjs.width - 1

                if self.y < 0:
                    self.y = 0
                elif self.y >= self.pjs.height:
                    self.y = self.pjs.height - 1

            # Mouse click: display pixel coordinates and value.
            if event.type() == QtCore.QEvent.MouseMove and 0 <= self.x < self.pjs.width and 0 <= self.y < self.pjs.height:
                self.pjs.statusbar.showMessage(
                    str(self.pjs.curslice + 1) + '/' + str(self.pjs.n_frames) + '\t(' + str(self.x) + ', ' + str(
                        self.y) + '): ' + str(self.pjs.imagedata[self.y, self.x]))

            # Orthogonal views tracker.
            if self.pjs.slicetracker is not None and event.type() == QtCore.QEvent.MouseMove and event.buttons() == QtCore.Qt.LeftButton:
                self.pjs.slicetracker = (self.x, self.y)
                self.pjs.orthogonal_views.reloadViews()

            elif self.pjs.annotation_mode == PyJAMAS.fiducial_annotations and event.type() == QtCore.QEvent.MouseButtonPress:
                if event.buttons() == QtCore.Qt.LeftButton:
                    self.pjs.addFiducial(self.x, self.y, self.pjs.curslice, pushundo=True)

                elif event.buttons() == QtCore.Qt.RightButton:
                    self.pjs.removeFiducial(self.x, self.y, self.pjs.curslice, pushundo=True)

            elif self.pjs.annotation_mode == PyJAMAS.rectangle_annotations:
                if event.type() == QtCore.QEvent.MouseButtonPress:
                    # Store first coordinate if left click ...
                    if event.buttons() == QtCore.Qt.LeftButton:
                        self.pjs._poly_ = [self.x, self.y]

                    # ... or delete polygon if right click.
                    elif event.buttons() == QtCore.Qt.RightButton:
                        self.pjs.removePolyline(self.x, self.y,
                                                self.pjs.curslice, pushundo=True)  # CAN WE JUST HAVE ONE removeAnnotationItem function?

                elif event.type() == QtCore.QEvent.MouseMove and event.buttons() == QtCore.Qt.LeftButton:  # Mouse move events will occur only when a mouse button is pressed down, unless mouse tracking has been enabled with QWidget.setMouseTracking()
                    if self.pjs._agraphicsitem_ and self.pjs._agraphicsitem_.scene():
                        self.pjs.gScene.removeItem(self.pjs._agraphicsitem_)

                    # If shift is not pressed, draw a rectangle, a square if it is pressed.
                    modifierPressed = QtWidgets.QApplication.keyboardModifiers()
                    if (modifierPressed & QtCore.Qt.ShiftModifier) != QtCore.Qt.ShiftModifier:
                        x = self.x
                        y = self.y
                    else:
                        deltaX = self.x - self.pjs._poly_[0]
                        deltaY = self.y - self.pjs._poly_[1]

                        if abs(deltaX) >= abs(deltaY):
                            x = self.x
                            y = self.pjs._poly_[1] + numpy.sign(deltaY) * abs(deltaX)
                        else:
                            y = self.y
                            x = self.pjs._poly_[0] + numpy.sign(deltaX) * abs(deltaY)

                    self.pjs._agraphicsitem_ = self.pjs.drawRectangle(self.pjs._poly_[0], self.pjs._poly_[1], x, y)
                    self.pjs.statusbar.showMessage(
                        '{0}/{1}\t({2}, {3}) -> w: {4}, h: {5}'.format(str(self.pjs.curslice + 1),
                        str(self.pjs.n_frames), str(
                        self.pjs._poly_[0]), str(
                        self.pjs._poly_[1]), str(abs(self.pjs._poly_[0] - x) + 1),
                        str(abs(self.pjs._poly_[1] - y) + 1)))

                elif event.type() == QtCore.QEvent.MouseButtonRelease and self.pjs._poly_ != []:
                    if self.pjs._agraphicsitem_ and self.pjs._agraphicsitem_.scene():
                        self.pjs.gScene.removeItem(self.pjs._agraphicsitem_)

                    x0 = self.pjs._poly_[0]
                    y0 = self.pjs._poly_[1]

                    modifierPressed = QtWidgets.QApplication.keyboardModifiers()
                    if (modifierPressed & QtCore.Qt.ShiftModifier) != QtCore.Qt.ShiftModifier:
                        x1 = self.x
                        y1 = self.y
                    else:
                        deltaX = self.x - self.pjs._poly_[0]
                        deltaY = self.y - self.pjs._poly_[1]

                        if abs(deltaX) >= abs(deltaY):
                            x1 = self.x
                            y1 = self.pjs._poly_[1] + numpy.sign(deltaY) * abs(deltaX)
                        else:
                            y1 = self.y
                            x1 = self.pjs._poly_[0] + numpy.sign(deltaX) * abs(deltaY)

                    if x0 > x1:
                        x1, x0 = x0, x1
                    if y0 > y1:
                        y1, y0 = y0, y1
                    self.pjs.addPolyline([[x0, y0], [x0, y1], [x1, y1], [x1, y0], [x0, y0]], self.pjs.curslice, pushundo=True)
                    self.pjs._poly_ = []

            elif self.pjs.annotation_mode == PyJAMAS.polyline_annotations:
                if event.type() == QtCore.QEvent.MouseButtonPress:
                    # Store coordinate if left click ...
                    if event.buttons() == QtCore.Qt.LeftButton:
                        self.pjs._poly_.append([self.x, self.y])

                        if self.pjs._agraphicsitem_ and self.pjs._agraphicsitem_.scene():
                            self.pjs.gScene.removeItem(self.pjs._agraphicsitem_)

                        self.pjs._agraphicsitem_, _ = self.pjs.drawPath(self.pjs._poly_)

                    # Delete last point if middle click
                    elif event.buttons() == QtCore.Qt.RightButton and self.pjs._poly_ != [] and len(self.pjs._poly_) >= 2:
                        self.pjs._poly_ = self.pjs._poly_[0:-1]
                        if self.pjs._agraphicsitem_ and self.pjs._agraphicsitem_.scene():
                            self.pjs.gScene.removeItem(self.pjs._agraphicsitem_)

                            apoly = self.pjs._poly_.copy()
                            apoly.append([self.x, self.y])

                            self.pjs._agraphicsitem_, _ = self.pjs.drawPath(apoly)
                    # ... or delete polygon if right click.
                    elif event.buttons() == QtCore.Qt.RightButton:
                        self.pjs.removePolyline(self.x, self.y, self.pjs.curslice, pushundo=True)

                # Redraw polyline as the user moves the cursor.
                elif event.type() == QtCore.QEvent.MouseMove and self.pjs._poly_ != []:
                    if self.pjs._agraphicsitem_ and self.pjs._agraphicsitem_.scene():
                        self.pjs.gScene.removeItem(self.pjs._agraphicsitem_)

                        apoly = self.pjs._poly_.copy()
                        apoly.append([self.x, self.y])

                        self.pjs._agraphicsitem_, _ = self.pjs.drawPath(apoly)

                # Add polyline as mouse button is released.
                elif event.type() == QtCore.QEvent.MouseButtonDblClick and self.pjs._poly_ != []:
                    if self.pjs._agraphicsitem_ and self.pjs._agraphicsitem_.scene():
                        self.pjs.gScene.removeItem(self.pjs._agraphicsitem_)

                    # Polylines need to have at least two points.
                    if len(self.pjs._poly_) <= 1:
                        self.pjs._poly_ = []
                        return False

                    apoly = self.pjs._poly_.copy()

                    # If shift is not pressed, go back to origin.
                    modifierPressed = QtWidgets.QApplication.keyboardModifiers()
                    if (modifierPressed & QtCore.Qt.ShiftModifier) != QtCore.Qt.ShiftModifier:
                        apoly.append([self.pjs._poly_[0][0], self.pjs._poly_[0][1]])

                    self.pjs.addPolyline(apoly, self.pjs.curslice, pushundo=True)
                    self.pjs._poly_ = []

            elif self.pjs.annotation_mode == PyJAMAS.delete_fiducials_outside_polyline:
                if event.type() == QtCore.QEvent.MouseButtonPress:
                    index = self.pjs.find_clicked_polyline(self.x, self.y)
                    if index < 0:
                        return False

                    # Delete every annotation outside.
                    self.pjs.undo_stack.push({'changetype': undo_modes.MULTI, 'frame': (self.pjs.curslice, self.pjs.curslice + 1), 'index': (True, False), 'details': self.pjs.copy_annotations((self.pjs.curslice, self.pjs.curslice + 1))})
                    self.pjs.removeFiducialsPolyline(self.pjs._poly_, False)
            elif self.pjs.annotation_mode == PyJAMAS.delete_fiducials_inside_polyline:
                if event.type() == QtCore.QEvent.MouseButtonPress:
                    index = self.pjs.find_clicked_polyline(self.x, self.y)
                    if index < 0:
                        return False

                    # Delete every annotation outside.
                    self.pjs.undo_stack.push({'changetype': undo_modes.MULTI, 'frame': (self.pjs.curslice, self.pjs.curslice + 1), 'index': (True, False), 'details': self.pjs.copy_annotations((self.pjs.curslice, self.pjs.curslice+1))})
                    self.pjs.removeFiducialsPolyline(self.pjs._poly_, True)
            elif self.pjs.annotation_mode == PyJAMAS.copy_polyline:
                if event.type() == QtCore.QEvent.MouseButtonPress:
                    index = self.pjs.find_clicked_polyline(self.x, self.y)

                    # Not using self.pjs._poly_ here, as other operations on the UI will overwrite it.
                    self.pjs._copied_poly_ = self.pjs.polylines[self.pjs.curslice][index]

                    if index < 0:
                        return False

            elif self.pjs.annotation_mode == PyJAMAS.livewire_annotations:
                if type(self.pjs._poly_) == list:
                    if event.type() == QtCore.QEvent.MouseButtonPress:
                        # Store coordinate if left click ...
                        if event.buttons() == QtCore.Qt.LeftButton:
                            if self.pjs._poly_ != []:
                                thesource = self.pjs._poly_[-1][::-1]
                                thedest = [self.y, self.x]
                                thepoints = rimage(self.pjs.imagedata).livewire(thesource, thedest,
                                                                                               PyJAMAS.livewire_margin, xy=True)  # Make livewire a static method?
                                self.pjs._poly_.extend(
                                    thepoints)  ### CHANGE: STORE ALL COORDINATES GENERATED BY LIVEWIRE FROM LAST CLICKED POINT

                                if self.pjs._agraphicsitem_ and self.pjs._agraphicsitem_.scene():
                                    self.pjs.gScene.removeItem(self.pjs._agraphicsitem_)

                                self.pjs._agraphicsitem_, _ = self.pjs.drawPath(self.pjs._poly_)

                            else:
                                self.pjs._poly_.append([self.x, self.y])
                                if self.pjs._agraphicsitem_ and self.pjs._agraphicsitem_.scene():
                                    self.pjs.gScene.removeItem(self.pjs._agraphicsitem_)

                                self.pjs._agraphicsitem_, _ = self.pjs.drawPath(self.pjs._poly_)
                        # Delete last point if middle click # NOT DONE YET.
                        elif event.buttons() == QtCore.Qt.RightButton and self.pjs._poly_ != [] and len(self.pjs._poly_) >= 2:
                            self.pjs._poly_ = self.pjs._poly_[0:-1]
                            if self.pjs._agraphicsitem_ and self.pjs._agraphicsitem_.scene():
                                self.pjs.gScene.removeItem(self.pjs._agraphicsitem_)

                                apoly = self.pjs._poly_.copy()
                                apoly.append([self.x, self.y])

                                self.pjs._agraphicsitem_, _ = self.pjs.drawPath(apoly)
                        # ... or delete polygon if right click.
                        elif event.buttons() == QtCore.Qt.RightButton:
                            self.pjs.removePolyline(self.x, self.y, self.pjs.curslice, pushundo=True)

                    # Redraw polyline as the user moves the cursor.
                    elif event.type() == QtCore.QEvent.MouseMove and self.pjs._poly_ != []:
                        if self.pjs._agraphicsitem_ and self.pjs._agraphicsitem_.scene():
                            self.pjs.gScene.removeItem(self.pjs._agraphicsitem_)

                            apoly = self.pjs._poly_.copy()
                            thesource = apoly.copy()[-1][::-1]
                            thedest = [self.y, self.x]
                            thepoints = rimage(self.pjs.imagedata).livewire(thesource, thedest,
                                                                            PyJAMAS.livewire_margin,
                                                                            xy=True)  # Make livewire a static method? Or make self.imagedata an RImage?
                            apoly.extend(
                                thepoints)  ### CHANGE: STORE ALL COORDINATES GENERATED BY LIVEWIRE FROM LAST CLICKED POINT

                            self.pjs._agraphicsitem_, _ = self.pjs.drawPath(apoly)
                            # self.statusbar.showMessage(str(self.curslice + 1) + '/' + str(self.n_frames) + '\t(' + str(self._poly_[0]) + ', ' + str(
                            # self._poly_[1]) + ') -> w: ' + str(abs(self._poly_[0] - self.x)) + ', h: ' + str(abs(self._poly_[1] - self.y)))

                    # Add polyline when mouse button is double-clicked.
                    elif event.type() == QtCore.QEvent.MouseButtonDblClick and self.pjs._poly_ != []:
                        if self.pjs._agraphicsitem_ and self.pjs._agraphicsitem_.scene():
                            self.pjs.gScene.removeItem(self.pjs._agraphicsitem_)

                        if len(self.pjs._poly_) <= 2:
                            self.pjs._poly_ = []
                            return False

                        # If shift is not pressed, go back to origin.
                        modifierPressed = QtWidgets.QApplication.keyboardModifiers()
                        if (modifierPressed & QtCore.Qt.ShiftModifier) != QtCore.Qt.ShiftModifier:
                            thesource = self.pjs._poly_[-1][::-1]
                            thedest = self.pjs._poly_[0][::-1]
                            thepoints = rimage(self.pjs.imagedata).livewire(thesource, thedest,
                                                                                           PyJAMAS.livewire_margin, xy=True)  # Make livewire a static method? Or make self.imagedata an RImage?
                            self.pjs._poly_.extend(thepoints)

                        self.pjs.addPolyline(self.pjs._poly_, self.pjs.curslice, pushundo=True)
                        self.pjs._poly_ = []

                else:
                    self.pjs._poly_ = []
                    return False

            elif self.pjs.annotation_mode == PyJAMAS.inflate_balloon:
                if event.type() == QtCore.QEvent.MouseButtonPress and event.buttons() == QtCore.Qt.LeftButton:
                    # If shift is not pressed, reset balloon force.
                    modifierPressed = QtWidgets.QApplication.keyboardModifiers()
                    if (modifierPressed & QtCore.Qt.ShiftModifier) != QtCore.Qt.ShiftModifier:
                        self.balloon_force = self.INITIAL_BALLOON_FORCE

                    self.balloon_timer.start(self.BALLOON_FORCE_INCREMENT_DELAY)

                if event.type() == QtCore.QEvent.MouseButtonRelease:
                    # if timer is running (event.buttons() does not seem to work with button release events).
                    if self.balloon_timer.isActive():
                        self.balloon_timer.stop()

                        self.pjs.image.inflateBalloon({'x': self.x, 'y': self.y}, self.pjs.curslice)

                    # if timer is not active (right click)
                    else:
                        self.pjs.removePolyline(self.x, self.y, self.pjs.curslice, pushundo=True)

            elif self.pjs.annotation_mode == PyJAMAS.move_polyline:
                # Select polyline with the mouse.
                if event.type() == QtCore.QEvent.MouseButtonPress:
                    index = self.pjs.find_clicked_polyline(self.x, self.y)
                    if index < 0:
                        return False
                    self.pjs.undo_stack.push({'changetype': undo_modes.POLYLINE_MOVED, 'frame': self.pjs.curslice, 'index': index, 'details': self.pjs._poly_[0]}) #push pre-move position to the stack

                # Move with the mouse.
                # Redraw polyline as the user moves the cursor.
                elif event.type() == QtCore.QEvent.MouseMove and event.buttons() == QtCore.Qt.LeftButton and self.x_prev > -1 and self.y_prev > -1:
                    if self.pjs._agraphicsitem_:
                        # self.pjs.gScene.removeItem(self.pjs._agraphicsitem_)
                        theshift = QtCore.QPointF(self.x - self.x_prev, self.y - self.y_prev)
                        for i in range(self.pjs._poly_.size()):
                            self.pjs._poly_[i] += theshift

                        # Make sure you stay within the image: first find bounding box.
                        theboundingrect = self.pjs._poly_.boundingRect()

                        thex = theboundingrect.x()
                        they = theboundingrect.y()
                        themaxx = thex + theboundingrect.width()
                        themaxy = they + theboundingrect.height()

                        # Make sure the bounding box is within the image. If not, ...
                        if thex < 0 or they < 0 or themaxx >= self.pjs.width or themaxy >= self.pjs.height:
                            theshift = QtCore.QPointF(0, 0)

                            # Shift the X and/or Y coordinates accordingly.
                            if thex < 0:
                                theshift.setX(theshift.x() - thex)
                            if themaxx >= self.pjs.width:
                                theshift.setX(theshift.x() - (themaxx - self.pjs.width + 1))
                            if they < 0:
                                theshift.setY(theshift.y() - they)
                            if themaxy >= self.pjs.height:
                                theshift.setY(theshift.y() - (themaxy - self.pjs.height + 1))

                            # This is the shift happening!
                            for i in range(self.pjs._poly_.size()):
                                self.pjs._poly_[i] += theshift

                        #self.pjs._agraphicsitem_ = self.pjs.drawPolyline(self.pjs._poly_)
                        self.pjs._agraphicsitem_.moveBy(theshift.x(), theshift.y())

                        self.pjs.repaint()

                # Update polyline as mouse button is released.
                #elif event.type() == QtCore.QEvent.MouseButtonRelease and self.pjs._poly_ != []:
                #    self.pjs._poly_ = []


            elif self.pjs.annotation_mode == PyJAMAS.export_fiducial_polyline:
                self.process_export_fiducial_polyline(event)

            elif event.type() == QtCore.QEvent.Resize:
                self.pjs.timeSlider.setGeometry(
                    QtCore.QRect(0, self.pjs.MainWindow.height() - 43, self.pjs.MainWindow.width(), 22))

            elif self.pjs.annotation_mode == PyJAMAS.select_polyline_crop and event.type() == QtCore.QEvent.MouseButtonPress:
                self.process_polyline_roi(event, self.pjs.image.cbCrop)

            elif self.pjs.annotation_mode == PyJAMAS.select_polyline_exportroi and event.type() == QtCore.QEvent.MouseButtonPress:
                self.process_polyline_roi(event, self.pjs.io.cbExportROIAndMasks)

            elif self.pjs.annotation_mode == PyJAMAS.select_polyline_kymo and event.type() == QtCore.QEvent.MouseButtonPress:
                self.process_polyline_roi(event, self.pjs.image.cbKymograph)

            # Store current position as previous (for mouse tracking).
            if event.type() in (QtCore.QEvent.MouseMove, QtCore.QEvent.MouseButtonPress, QtCore.QEvent.MouseButtonRelease):
                self.x_prev = self.x
                self.y_prev = self.y

        elif type(source) == QtWidgets.QGraphicsView:
            # Move with the keyboard.
            if event.type() == QtCore.QEvent.KeyPress and self.x_prev > -1 and self.y_prev > -1:
                if self.pjs._agraphicsitem_ and self.pjs._poly_ != []:
                    if event.key() == QtCore.Qt.Key_Left:
                        theshift = QtCore.QPointF(- PJSEventFilter.POLYLINE_MOVE_STEP, 0)
                    elif event.key() == QtCore.Qt.Key_Right:
                        theshift = QtCore.QPointF(PJSEventFilter.POLYLINE_MOVE_STEP, 0)
                    elif event.key() == QtCore.Qt.Key_Down:
                        theshift = QtCore.QPointF(0, PJSEventFilter.POLYLINE_MOVE_STEP)
                    elif event.key() == QtCore.Qt.Key_Up:
                        theshift = QtCore.QPointF(0, - PJSEventFilter.POLYLINE_MOVE_STEP)
                    else:
                        return False

                    for i in range(self.pjs._poly_.size()):
                        self.pjs._poly_[i] += theshift

                    # Make sure you stay within the image: first find bounding box.
                    theboundingrect = self.pjs._poly_.boundingRect()

                    thex = theboundingrect.x()
                    they = theboundingrect.y()
                    themaxx = thex + theboundingrect.width()
                    themaxy = they + theboundingrect.height()

                    # Make sure the bounding box is within the image. If not, ...
                    if thex < 0 or they < 0 or themaxx >= self.pjs.width or themaxy >= self.pjs.height:
                        theshift = QtCore.QPointF(0, 0)

                        # Shift the X and/or Y coordinates accordingly.
                        if thex < 0:
                            theshift.setX(theshift.x() - thex)
                        if themaxx >= self.pjs.width:
                            theshift.setX(theshift.x() - (themaxx - self.pjs.width + 1))
                        if they < 0:
                            theshift.setY(theshift.y() - they)
                        if themaxy >= self.pjs.height:
                            theshift.setY(theshift.y() - (themaxy - self.pjs.height + 1))

                        # This is the shift happening!
                        for i in range(self.pjs._poly_.size()):
                            self.pjs._poly_[i] += theshift

                    # self.pjs._agraphicsitem_ = self.pjs.drawPolyline(self.pjs._poly_)
                    self.pjs._agraphicsitem_.moveBy(theshift.x(), theshift.y())

                    self.pjs.repaint()

                    theboundingrect = self.pjs._poly_.boundingRect()
                    self.pjs.statusbar.showMessage(
                        '{0}/{1}\t({2}, {3}) -> w: {4}, h: {5}'.format(str(self.pjs.curslice + 1),
                                                                       str(self.pjs.n_frames), str(
                                int(theboundingrect.x())), str(
                                int(theboundingrect.y())), str(int(theboundingrect.width() + 1)),
                                                                       str(int(theboundingrect.height() + 1))))

        return QtCore.QObject.eventFilter(self.pjs, source, event)

    def process_export_fiducial_polyline(self, event):
        if event.type() == QtCore.QEvent.MouseButtonPress:
            theClickedItem = self.pjs.findGraphicItem(self.x, self.y, QtWidgets.QGraphicsEllipseItem)

            # If you found an ellipse:
            if type(theClickedItem) == QtWidgets.QGraphicsEllipseItem:
                # Get coordinates.
                pos = theClickedItem.scenePos()
                fiducial_coords = [int(pos.x() + PyJAMAS.fiducial_radius / 2),
                                   int(pos.y() + PyJAMAS.fiducial_radius / 2)]

                self.pjs.io.export_polyline_annotations(fiducial_coords[0], fiducial_coords[1])
        return True

    def process_polyline_roi(self, event, fn):
        """fn is one of self.pjs.image.cbCrop, self.pjs.image.cbKymograph and self.pjs.io.cbExportROIAndMasks"""
        if event.type() == QtCore.QEvent.MouseButtonPress:
            item_index = self.pjs.find_clicked_polyline(self.x, self.y)
            # ItemIndex of -1 means no polyline found, in which case, exit
            if item_index == -1:
                return False

            if fn is self.pjs.image.cbCrop and self.pjs.crop_tracked_polyline:  # Crop tracked polyline, input index to cbCrop
                thepolyline = numpy.array([item_index])
            else:  # Crop polyline on this slice, input min and max coordinates to cbCrop
                thepolyline = rutils.RUtils.qpolygonf2ndarray(self.pjs.polylines[self.pjs.curslice][item_index])
            fn(polyline=thepolyline, margin_size=self.pjs.margin_size)
        return True

    def balloon_timer_function(self):
        # If shift is not pressed ...
        modifierPressed = QtWidgets.QApplication.keyboardModifiers()
        if (modifierPressed & QtCore.Qt.ShiftModifier) != QtCore.Qt.ShiftModifier:
            self.balloon_force += self.BALLOON_FORCE_INCREMENT
        # If shift is pressed
        else:
            pass  # self.balloon_force = self.balloon_force

        self.pjs.statusbar.showMessage(f"Inflation force {self.balloon_force:.2f}.")

        return

