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

from typing import Optional

import numpy
import copy
from PyQt5 import QtCore, QtGui, QtWidgets

import pyjamas.dialogs as dialogs
from pyjamas.pjscore import PyJAMAS
from pyjamas.pjscore import undo_modes
from pyjamas.pjsthreads import ThreadSignals
from pyjamas.rcallbacks.rcallback import RCallback
from pyjamas.rutils import RUtils


class RCBAnnotations(RCallback):
    PIX_SHIFT: int = 2  # x, y shift to use when pasting polylines with a shift with respect to original position.

    def cbNoAnn(self) -> bool:
        """
        Reset annotation mode: no action upon mouse click.

        :return: True.
        """

        self.pjs.annotation_mode = PyJAMAS.no_annotations
        QtWidgets.QApplication.setOverrideCursor(QtCore.Qt.ArrowCursor)

        return True

    def cbHideAnn(self) -> bool:
        """
        Toggle annotations off/on the screen.

        :return: True.
        """

        if self.pjs.show_annotations:
            self.pjs.eraseAnnotations()
        else:
            self.pjs.paintAnnotations()

        self.pjs.show_annotations = not self.pjs.show_annotations

        return True

    def cbFiducials(self) -> bool:
        """
        Set annotation mode to add/remove fiducials.

        :return: True.
        """

        self.pjs.annotation_mode = PyJAMAS.fiducial_annotations
        QtWidgets.QApplication.setOverrideCursor(QtCore.Qt.CrossCursor)

        return True

    def cbRectangles(self) -> bool:
        """
        Set annotation mode to add/remove rectangles (a specific type of polyline).

        :return: True.
        """

        self.pjs.annotation_mode = PyJAMAS.rectangle_annotations
        self.pjs._poly_ = []
        QtWidgets.QApplication.setOverrideCursor(QtCore.Qt.CrossCursor)

        return True

    def cbPolylines(self) -> bool:
        """
        Set annotation mode to add/remove polylines.

        :return: True.
        """

        self.pjs.annotation_mode = PyJAMAS.polyline_annotations
        self.pjs._poly_ = []
        QtWidgets.QApplication.setOverrideCursor(QtCore.Qt.CrossCursor)

        return True

    def cbLiveWire(self) -> bool:
        """
        Set annotation mode to add/remove polylines using the LiveWire algorithm for semi-automated object delineation.

        :return: True.
        """

        self.pjs.annotation_mode = PyJAMAS.livewire_annotations
        QtWidgets.QApplication.setOverrideCursor(QtCore.Qt.CrossCursor)

        return True

    def cbInflateBalloon(self) -> bool:
        """
        Set annotation mode to add/remove polylines using active contours for semi-automated object delineation.

        :return: True.
        """

        self.pjs.annotation_mode = PyJAMAS.inflate_balloon
        QtWidgets.QApplication.setOverrideCursor(QtCore.Qt.CrossCursor)

        return True

    def cbCopyPolyline(self) -> bool:
        """
        Set annotation mode to copy the polyline clicked on (stored in pjs._copied_poly_).

        :return: True.
        """

        self.pjs.annotation_mode = PyJAMAS.copy_polyline
        QtWidgets.QApplication.setOverrideCursor(QtCore.Qt.CrossCursor)

        return True

    def cbPastePolyline(self, paste_shifted: bool = False) -> object:
        """
        Paste the polyline previously copied (stored in pjs._copied_poly_).

        :return: True if polyline was copied, False otherwise.
        """

        if self.pjs._copied_poly_ is None or self.pjs._copied_poly_ == []:
            return False

        if paste_shifted:
            copied_poly = (RUtils.qpolygonf2ndarray(self.pjs._copied_poly_) + RCBAnnotations.PIX_SHIFT).tolist()
        else:
            copied_poly = RUtils.qpolygonf2list(self.pjs._copied_poly_)

        self.pjs.addPolyline(copied_poly, self.pjs.curslice, pushundo=True)

        return True

    def cbMovePolyline(self) -> bool:
        """
        Set annotation mode to move the polyline clicked on.

        :return: True.
        """

        self.pjs.annotation_mode = PyJAMAS.move_polyline
        QtWidgets.QApplication.setOverrideCursor(QtCore.Qt.CrossCursor)

        return True

    def cbTrackFiducials(self, firstSlice: Optional[int] = None, lastSlice: Optional[int] = None, wait_for_thread: bool = False) -> bool:
        """
        Match fiducials across slices in a stack based on minimum distance. Requires a constant number of fiducials. Runs in a different thread.

        :param firstSlice: start slice (>=1).
        :param lastSlice: final slice.
        :param wait_for_thread: True if PyJAMAS should wait for the function to finish before returning control to the user, False otherwise.
        :return: True if tracking finished correctly, False otherwise.
        """

        # If not enough parameters, open a dialog.
        if (firstSlice is False or firstSlice is None or lastSlice is False or lastSlice is None) \
                and self.pjs is not None:
            dialog = QtWidgets.QDialog()
            ui = dialogs.timepoints.TimePointsDialog()

            firstSlice = self.pjs.curslice + 1
            lastSlice = 1 if self.pjs.n_frames == 1 else self.pjs.slices.shape[0]

            ui.setupUi(dialog, firstslice=firstSlice, lastslice=lastSlice)
            dialog.exec_()
            dialog.show()
            # If the dialog was closed by pressing OK, then run the measurements.
            continue_flag = dialog.result() == QtWidgets.QDialog.Accepted
            theparameters_tuple = ui.parameters()
            theparameters = {'first': theparameters_tuple[0], 'last': theparameters_tuple[1]}

            dialog.close()

        else:
            theparameters = {'first': firstSlice, 'last': lastSlice}
            continue_flag = True

        # When you have the input parameters:
        if continue_flag:
            # Track forward.
            if theparameters['first'] <= theparameters['last']:
                theslicenumbers = numpy.arange(theparameters['first'] - 1, theparameters['last'])

            # Track backwards.
            else:
                theslicenumbers = numpy.arange(theparameters['first'] - 1, theparameters['last'] - 2, -1)

            # But DO track (in a thread)!!
            self.launch_thread(self.track_fiducials, {'theslices': theslicenumbers, 'progress': True, 'stop': True},
                               finished_fn=self.finished_fn, stop_fn=self.stop_fn, progress_fn=self.progress_fn,
                               wait_for_thread=wait_for_thread)

            return True
        else:
            return False

    def track_fiducials(self, theslices: numpy.ndarray, progress_signal: ThreadSignals, stop_signal: ThreadSignals) -> bool:

        #Requires a constant number of fiducials.

        #:param theslices: indeces of the slices in which fiducials will be tracked. They do not need to be consecutive.
        #:return:

        # Make sure that the slices are in a 1D numpy array.
        theslices = numpy.atleast_1d(theslices)
        num_slices = theslices.size

        # For every slice ...
        for i in range(num_slices-1):
            if len(self.pjs.fiducials[theslices[i]]) == 0:
                if stop_signal is not None:
                    stop_signal.emit(f"Stopping at slice {theslices[i]+1}: there are no fiducials to track there!")
                return True

            if len(self.pjs.fiducials[theslices[i+1]]) == 0:
                if stop_signal is not None:
                    stop_signal.emit(f"Stopping at slice {theslices[i+1]+1}: there are no fiducials to track there!")
                return True

            if len(self.pjs.fiducials[theslices[i]]) != len(self.pjs.fiducials[theslices[i+1]]):
                if stop_signal is not None:
                    stop_signal.emit(f"Error: slices {theslices[i]+1} and {theslices[i + 1] + 1} have a different number of fiducials.")
                return False

            fiducials_orig = numpy.array(self.pjs.fiducials[theslices[i]])
            fiducials_dest = numpy.array(self.pjs.fiducials[theslices[i + 1]])

            # Find distance between all pairs of fiducials.
            distance_matrix: numpy.ndarray = RUtils.point2point_distances(fiducials_orig, fiducials_dest)
            sorted_indices: numpy.ndarray = distance_matrix.argsort()

            # For each fiducials_orig[ii] select the closest fiducials_dest[jj].
            closest_fiducial_index: numpy.ndarray = sorted_indices[:, 0]

            # Deal with cases in which more than one fiducial maps to another.
            # bincount is WAY faster than unique.
            #theindex, counts = numpy.unique(closest_fiducial_index, return_counts=True)
            #conflictive_indeces = theindex[counts > 1]
            counts: int = numpy.bincount(closest_fiducial_index)

            if any(counts > 1):
                conflictive_indeces = numpy.arange(counts.shape[0])[counts > 1]
                original_fiducials = numpy.arange(closest_fiducial_index.shape[0])[closest_fiducial_index == conflictive_indeces[0]]

                if stop_signal is not None:
                    stop_signal.emit(f"Error in slice {theslices[i + 1]+1}, fiducial {conflictive_indeces[0]+1}: fiducials {original_fiducials+1} from slice {theslices[i]+1} map here.")
                return False

            else:
                self.pjs.fiducials[theslices[i+1]] = fiducials_dest[closest_fiducial_index].tolist()

            if progress_signal is not None:
                progress_signal.emit(int((100*(i+1))/(num_slices-1)))

        return True

    def cbUndo(self) -> bool:
        """
        Undo the most recent action: individual fiducials added or deleted; polylines added, deleted or moved; or multiple fiducials or polylines added or deleted simultaneously (e.g. after finding seeds, segmenting cells, or deleting all annotations). Also, image projections, inversion, smoothing, gradient, registration, crop or kymograph.

        :return: True if undo finished correctly, False if there was an error.
        """

        undoInfo = self.pjs.undo_stack.pop()
        if undoInfo is None:
            return False

        changetype = undoInfo.get("changetype")
        frame = undoInfo.get("frame")
        index = undoInfo.get("index")
        details = undoInfo.get("details")

        try:
            if changetype == undo_modes.FIDUCIAL_ADDED:
                self.pjs.fiducials[frame].pop(index)
            elif changetype == undo_modes.FIDUCIAL_DELETED:
                self.pjs.fiducials[frame].insert(index, details)
            elif changetype == undo_modes.POLYLINE_ADDED:
                self.pjs.polylines[frame].pop(index)
            elif changetype == undo_modes.POLYLINE_DELETED:
                self.pjs.polylines[frame].insert(index, details)
            elif changetype == undo_modes.POLYLINE_MOVED:
                curcoords = self.pjs.polylines[frame][index][0]
                shift = QtCore.QPointF(details.x() - curcoords.x(), details.y() - curcoords.y())
                for i in range(self.pjs.polylines[frame][index].size()):
                    self.pjs.polylines[frame][index][i] += shift
            elif changetype == undo_modes.MULTI:
                if index[0]:
                    self.pjs.fiducials[frame[0]:frame[1]] = details[0]
                if index[1]:
                    self.pjs.polylines[frame[0]:frame[1]] = details[1]
            elif changetype == undo_modes.IMAGE:
                self.pjs.io.cbLoadArray(frame)
                self.pjs.fiducials = details[0]
                self.pjs.polylines = details[1]
                self.pjs.image.cbGoTo(index)

            if changetype == undo_modes.IMAGE or changetype == undo_modes.MULTI or frame == self.pjs.curslice:
                self.pjs.repaint()

        except Exception as an_exception:
            print(an_exception)
            self.pjs.undo_stack.clear()
            self.pjs.statusbar.showMessage("Something went wrong with the undo function. Undo stack cleared.")

            return False

        return True

    def cbDeleteAllAnn(self) -> bool:
        """
        Delete annotations from all image slices.

        :return: True.
        """
        self.pjs.undo_stack.push({'changetype': undo_modes.MULTI, 'frame': (0, self.pjs.n_frames), 'index': (True, True), 'details': self.pjs.copy_annotations()})
        self.pjs.fiducials = [[] for _ in range(self.pjs.n_frames)]
        self.pjs.polylines = [[] for _ in range(self.pjs.n_frames)]

        self.pjs.repaint()

        return True

    def cbDeleteSliceAnn(self, index: Optional[int] = None) -> bool:
        """
        Delete annotations from a specific slice.

        :param index: index of the slice in which annotations will be deleted (>=0). Defaults to the current slice (pjs.curslice).
        :return: True.
        """

        if index is None or index is False:
            index = self.pjs.curslice

        self.pjs.undo_stack.push({'changetype': undo_modes.MULTI, 'frame': (index, index + 1), 'index': (True, True), 'details': self.pjs.copy_annotations((index, index+1))})
        self.pjs.fiducials[index] = []
        self.pjs.polylines[index] = []

        self.pjs.repaint()

        return True

    def cbDeleteSlicePoly(self, index: Optional[int] = None) -> bool:
        """
        Delete polylines from a specific slice.

        :param index: index of the slice in which polylines will be deleted (>=0). Defaults to the current slice (pjs.curslice).
        :return: True.
        """

        if index is None or index is False:
            index = self.pjs.curslice

        self.pjs.undo_stack.push({'changetype': undo_modes.MULTI, 'frame': (index, index + 1), 'index': (False, True), 'details': self.pjs.copy_annotations((index, index+1))})
        self.pjs.polylines[index] = []

        self.pjs.repaint()

        return True

    def cbDeleteFiducialsOutsidePoly(self) -> bool:
        """
        Set annotation mode to remove fiducials outside the polyline clicked on.

        :return: True.
        """

        self.pjs.annotation_mode = PyJAMAS.delete_fiducials_outside_polyline
        QtWidgets.QApplication.setOverrideCursor(QtCore.Qt.CrossCursor)

        return True

    def cbDeleteFiducialsInsidePoly(self) -> bool:
        """
        Set annotation mode to remove fiducials inside the polyline clicked on.

        :return: True.
        """

        self.pjs.annotation_mode = PyJAMAS.delete_fiducials_inside_polyline
        QtWidgets.QApplication.setOverrideCursor(QtCore.Qt.CrossCursor)

        return True



