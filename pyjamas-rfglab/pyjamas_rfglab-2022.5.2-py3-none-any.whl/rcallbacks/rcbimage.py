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

# todo:
# move gaussian filtering INSIDE the rimutils functions (find_seeds or waterseed)?

from enum import IntEnum
import time
from typing import List, Optional, Tuple

import numpy
from PyQt5 import QtCore, QtWidgets, QtGui
from shapely.geometry import Point
from scipy import ndimage
from scipy.spatial import ConvexHull
import skimage.filters

import pyjamas.dialogs as dialogs
from pyjamas.pjscore import PyJAMAS
from pyjamas.pjscore import undo_modes
from pyjamas.pjsthreads import Thread
from pyjamas.pjsthreads import ThreadSignals
from pyjamas.rannotations.rpolyline import RPolyline
from pyjamas.rcallbacks.rcallback import RCallback
from pyjamas.rimage.rimutils import rimutils
from pyjamas.rutils import RUtils
import pyjamas.orthogonalviewswindow as orthogonalViews

class projection_types(IntEnum):
    MAX: int = 0
    SUM: int = 1


class RCBImage(RCallback):
    CW: int = 90
    CCW: int = -90
    UP_DOWN: int = 1
    LEFT_RIGHT: int = 2

    DEFAULT_WINDOW_SZ: int = 64
    DEFAULT_SMOOTHING_SIGMA: float = 0.8
    DEFAULT_BINARY_DILATIONS: int = 4  # positive to segment dark objects with brigh background, negative for the opposite.
    DEFAULT_MINIMUM_DISTANCE_TRANSFORM: float = -1.0
    DEFAULT_MAX_SEED_NUMBER: int = 100
    DEFAULT_PREVIEW: bool = False
    DEFAULT_ALPHA_CONCAVE_HULL: int = 25  # Trial and error ...
    _MIN_CELL_AREA: int = 10
    _MAX_CELL_AREA: int = 10000
    CENTER_SEEDS_CLOSER_TO_THE_EDGE: float = 6.0

    def cbAdjustContrast(self, min_percentile=None, max_percentile=None) -> bool:
        """
        Stretch the displayed pixel values between a certain minimum and maximum percentiles.

        :param min_percentile: lower percentile of existing image intensities to map to black; a dialog appears if this is None.
        :param max_percentile: higher percentile of existing image intensities to map to white; a dialog appears if this is None.
        :return: True if the contrast was adjusted, False otherwise.
        """

        continue_flag = True

        if min_percentile is None or min_percentile is False or max_percentile is None or max_percentile is False:
            dialog = QtWidgets.QDialog()
            ui = dialogs.adjustcontrast.AdjustContrastDialog(self.pjs)
            ui.setupUi(dialog, self.pjs.min_pix_percentile, self.pjs.max_pix_percentile)
            dialog.exec_()
            dialog.show()

            continue_flag = dialog.result() == QtWidgets.QDialog.Accepted

            if continue_flag:
                parameters = ui.parameters()
                min_percentile = parameters.get('min_percentile', 0)
                max_percentile = parameters.get('max_percentile', 100)

            dialog.close()

        if continue_flag:

            self.pjs.min_pix_percentile = min_percentile
            self.pjs.max_pix_percentile = max_percentile

            self.pjs.displayData()

            return True

        else:
            return False

    def cbRotateImage(self, direction: int = CW) -> bool:
        """
        Rotate image and image annotations by 90 degrees.

        :param direction: one of pjs.image.CW (clockwise) or pjs.image.CCW (counterclockwise).
        :return: True.
        """
        transform = QtGui.QTransform()

        if direction == self.CW:
            # self.pjs.slices = numpy.asarray([numpy.rot90(x, -1) for x in self.pjs.slices]) # An order of magnitude slower than below.
            transform.rotate(90)
            transform.translate(0, -self.pjs.height)
            self.pjs.slices = numpy.rot90(self.pjs.slices, -1, (1, 2))
        elif direction == self.CCW:
            # self.pjs.slices = numpy.asarray([numpy.rot90(x) for x in self.pjs.slices]) # An order of magnitude slower than below.
            transform.rotate(-90)
            transform.translate(-self.pjs.width, 0)
            self.pjs.slices = numpy.rot90(self.pjs.slices, 1, (1, 2))

        new_fiducials, new_polylines = self.transform_annotations(transform, (self.pjs.height, self.pjs.width))
        self.pjs.initImage()
        self.pjs.polylines = new_polylines
        self.pjs.fiducials = new_fiducials
        self.pjs.repaint()

        return True

    def cbFlipImage(self, direction: int = LEFT_RIGHT) -> bool:
        """
        Flip image and image annotations left/right or up/down.

        :param direction: one of pjs.image.LEFT_RIGHT or pjs.image.UP_DOWN.
        :return: True.
        """
        transform = QtGui.QTransform()

        if direction == self.LEFT_RIGHT:
            transform.scale(-1,1)
            transform.scale(-1,1)
            transform.translate(-self.pjs.width,0)
            # self.pjs.slices = numpy.flip(self.pjs.slices, 2)  # Order or magnitude slower than the code below.
            self.pjs.slices = self.pjs.slices[..., ::-1]
        elif direction == self.UP_DOWN:
            transform = QtGui.QTransform()
            transform.scale(1, -1)
            transform.translate(0, -self.pjs.height)
            # self.pjs.slices = numpy.fliplr(self.pjs.slices)  # Could have used flip with parameter 1, but this is faster. Unfortunately, there is no fast function to flip with parameter 2. Still, slower than below.
            self.pjs.slices = self.pjs.slices[..., ::-1, :]

        new_fiducials, new_polylines = self.transform_annotations(transform)
        self.pjs.initImage()
        self.pjs.polylines = new_polylines
        self.pjs.fiducials = new_fiducials
        self.pjs.repaint()

        return True

    def cbProjectImage(self, slice_list: Optional[List[int]] = None, projection_type: projection_types = projection_types.MAX) -> bool:
        """
        Intensity projection of the open image.

        :param slice_list: list of slice indexes to project (e.g. 0, 1, 4-8, 15); if None, a dialog is opened; if empty, all slices are used.
        :return: True if the maximum intensity projection was created, False if not.
        """

        if slice_list is False or slice_list is None:
            slice_list_str, ok_pressed = QtWidgets.QInputDialog.getText(None, "Project image",
                                                                        "Enter a range of slices (e.g. 1, 4-8, 15): ",
                                                                        QtWidgets.QLineEdit.Normal, "")

            if not ok_pressed:
                return False

            if slice_list_str == '':
                slice_list = list(range(self.pjs.n_frames))
            else:
                slice_list = [x-1 for x in RUtils.parse_range_list(slice_list_str)]
        elif slice_list == []:
            slice_list = list(range(self.pjs.n_frames))

        # Projection function is determined by the type of projection.
        if projection_type == projection_types.MAX:
            proj_fn = rimutils.mip
        elif projection_type == projection_types.SUM:
            proj_fn = rimutils.sip

        # This line here is necessary: for some mysterious reason, if doing an MIP from a slice
        # other than the first one, there is an error that I was unable to debug, but seemed related
        # to the Qt backend based on the debugger error.
        """/Users/rodrigo/src/pyjamas/pyjamas/rimage/rimutils.py:641: RuntimeWarning: divide by zero encountered in true_divide
            sc = (maximum - minimum) / (high - low)
            /Users/rodrigo/src/pyjamas/pyjamas/rimage/rimutils.py:648: RuntimeWarning: invalid value encountered in multiply
            image_out = image_out * sc"""
        self.pjs.image.cbGoTo(0)

        self.pjs.undo_stack.push(
            {'changetype': undo_modes.IMAGE, 'frame': self.pjs.slices,
             'index': self.pjs.curslice,
             'details': self.pjs.copy_annotations()})

        self.pjs.slices = proj_fn(self.pjs.slices[slice_list])

        self.pjs.initImage()

        return True

    def cbInvertImage(self) -> bool:
        """
        Invert image.

        :return: True.
        """
        self.pjs.undo_stack.push(
            {'changetype': undo_modes.IMAGE, 'frame': self.pjs.slices,
             'index': self.pjs.curslice,
             'details': self.pjs.copy_annotations()})

        working_slice = self.pjs.curslice

        self.pjs.slices = rimutils.invert(self.pjs.slices)
        self.pjs.prepare_image()

        self.pjs.image.cbGoTo(working_slice)

        self.pjs.displayData()

        return True

    def cbGradientImage(self) -> bool:
        """
        Magnitude of the image gradient.

        :return: True.
        """
        self.pjs.undo_stack.push(
            {'changetype': undo_modes.IMAGE, 'frame': self.pjs.slices,
             'index': self.pjs.curslice,
             'details': self.pjs.copy_annotations()})

        working_slice = self.pjs.curslice

        self.pjs.slices = rimutils.gradient(self.pjs.slices)
        self.pjs.prepare_image()

        self.pjs.image.cbGoTo(working_slice)

        self.pjs.displayData()

        return True

    def cbGaussianImage(self, sigma: float = 0.0) -> bool:
        """
        Gaussian smoothing.

        :param sigma: standard deviation of the Gaussian kernel.
        :return: True if the image was smoothened, False if the value of sigma is incorrect.
        """

        thesigma: float = 0.0
        ok_flag: bool = None

        if sigma is not None and sigma is not False and sigma >= 0.0:
            thesigma = sigma
            ok_flag = True
        else:
            # Read user input for fps.
            thesigma, ok_flag = QtWidgets.QInputDialog.getDouble(None, 'Gaussian smoothing',
                                                                 'Select standard deviation: ',
                                                                 self.pjs.gaussian_sigma, 0.0)

        if ok_flag and thesigma >= 0.0:
            self.pjs.gaussian_sigma = thesigma

            self.pjs.undo_stack.push(
                {'changetype': undo_modes.IMAGE, 'frame': self.pjs.slices,
                 'index': self.pjs.curslice,
                 'details': self.pjs.copy_annotations()})

            working_slice = self.pjs.curslice

            self.pjs.slices = rimutils.gaussian_smoothing(self.pjs.slices, thesigma)
            self.pjs.prepare_image()

            self.pjs.image.cbGoTo(working_slice)

            self.pjs.displayData()

            return True

        else:
            return False

    def cbRegisterImage(self) -> bool:
        """
        Register imaage slices containing fiducial annotations that label corresponding image features.

        :return: True.
        """
        self.pjs.undo_stack.push(
            {'changetype': undo_modes.IMAGE, 'frame': self.pjs.slices,
             'index': self.pjs.curslice,
             'details': self.pjs.copy_annotations()})

        working_slice = self.pjs.curslice
        self.pjs.slices, distances = rimutils.register(self.pjs.slices,
                                                       RUtils.pjsfiducials_to_array(self.pjs.fiducials),
                                                       self.pjs.curslice)
        self.shift_annotations(distances)
        self.pjs.prepare_image()
        self.pjs.image.cbGoTo(working_slice)

        self.pjs.displayData()

        return True

    def cbRescaleImage(self, scale_factor: Tuple[float, float] = (1.0, 1.0)) -> bool:
        """
        Rescale image (and annotations) along the X, Y axes.

        :param scale_factor: scale factors for rows and columns.
        :return: True if the image was rescaled, False if the scale factor tuple is not properly formatted.
        """

        thescale: Tuple[float, float] = (0.0, 0.0)
        ok_flag: bool = None

        if scale_factor is not None and scale_factor is not False and len(scale_factor) == 2:
            thescale = scale_factor
            ok_flag = True
        else:
            # Read user input for fps.
            thescale_str, ok_flag = QtWidgets.QInputDialog.getText(None, 'Rescale',
                                                                   '(row, column) scale factor: ',
                                                                   QtWidgets.QLineEdit.Normal,
                                                                   f"{self.pjs.scale_factor}")
            if ok_flag:
                try:
                    thescale = eval(thescale_str)
                except:
                    print(f"Incorrect input tuple.")
                    ok_flag = False

        if ok_flag and len(thescale) == 2:
            self.pjs.scale_factor = thescale

            self.pjs.undo_stack.push(
                {'changetype': undo_modes.IMAGE, 'frame': self.pjs.slices,
                 'index': self.pjs.curslice,
                 'details': self.pjs.copy_annotations()})

            working_slice = self.pjs.curslice

            self.pjs.slices = rimutils.rescale(self.pjs.slices, thescale)

            self.scale_annotations(self.pjs.scale_factor)
            self.pjs.prepare_image()

            # Resizing the window.
            self.pjs.resize_window()

            self.pjs.image.cbGoTo(working_slice)

            self.pjs.displayData()

            return True

        else:
            return False

    # Inspiration for multithreading from: # Shamelessly stolen from https://www.mfitzp.com/article/multithreading-pyqt-applications-with-qthreadpool/
    def cbPlay(self) -> bool:
        """
        Play/stop playing through the image slices.

        :return: True.
        """
        # If a thread is already running, jump to the end of the movie.
        if self.pjs.threadpool.activeThreadCount() > 0:
            self.pjs.image.cbGoTo(self.pjs.n_frames - 1)

        athread = Thread(self.play_movie)
        athread.kwargs['progress_callback'] = athread.signals.progress
        # athread.signals.result.connect(self.print_output)
        athread.signals.finished.connect(self.thread_complete)
        athread.signals.progress.connect(self.progress_fn)

        self.pjs.threadpool.start(athread)

        return True

    def play_movie(self, progress_callback) -> bool:  # execute_this_fn
        start = time.time()
        period = 1.0 / self.pjs.fps

        while self.pjs.curslice < self.pjs.n_frames - 1:
            if (time.time() - start) > period:
                start += period
                # Because this is the function that will run in a thread, it cannot
                # manipulate the gui (or errors will happen - gui manipulations must
                # be in the thread that owns the gui). Instead, we can emit a signal
                # when it corresponds, and the signal can be slotted in a function
                # in the main thread that modifies the gui.
                progress_callback.emit(self.pjs.curslice)

        return True

    def progress_fn(self, n):
        self.pjs.image.cbNextFrame()

    def thread_complete(self):
        self.pjs.image.cbGoTo(0)

    def shift_annotations(self, translation_vector: numpy.ndarray) -> bool:
        if translation_vector is False or translation_vector is None:
            return False

        for slice_index in range(self.pjs.n_frames):
            theshift = translation_vector[slice_index].astype(int)

            if theshift.any():
                self.pjs.fiducials[slice_index] = (self.pjs.fiducials[slice_index] + theshift).tolist()

            for a_polyline in self.pjs.polylines[slice_index]:
                a_polyline.translate(QtCore.QPointF(theshift[0], theshift[1]))

        return True

    def scale_annotations(self, scale_factor: Tuple[float, float]) -> bool:
        if scale_factor is False or scale_factor is None or len(scale_factor) != 2:
            return False

        for slice_index in range(self.pjs.n_frames):
            fiducial_array = numpy.asarray(self.pjs.fiducials[slice_index])
            polyline_list = self.pjs.polylines[slice_index]

            if fiducial_array.size > 0:
                fiducial_array[:, 0] = (fiducial_array[:, 0] * scale_factor[1]).astype(int)
                fiducial_array[:, 1] = (fiducial_array[:, 1] * scale_factor[0]).astype(int)

                self.pjs.fiducials[slice_index] = fiducial_array.tolist()

            if len(polyline_list) > 0:
                for polyline_index, a_polyline in enumerate(polyline_list):
                    coord_array = RUtils.qpolygonf2ndarray(a_polyline)
                    coord_array[:, 0] *= scale_factor[
                        1]  # qpolygonf2ndarray returns (x, y) coordinates, and scale_factor is (row, column)
                    coord_array[:, 1] *= scale_factor[
                        0]  # qpolygonf2ndarray returns (x, y) coordinates, and scale_factor is (row, column)

                    thepolyline = QtGui.QPolygonF()

                    for thepoint in coord_array:
                        thepolyline.append(QtCore.QPointF(thepoint[0], thepoint[1]))

                    self.pjs.polylines[slice_index][polyline_index] = thepolyline

        return True

    def cbCrop(self, polyline: Optional[numpy.ndarray] = None, margin_size: int = 0, new_window: bool = False) -> bool:
        """
        Crop image.

        :param polyline: ndarray with two columns containing the x, y polyline of the region to crop; if cropping with a tracked polyline, ndarray with one element corresponding to the polyline index; if not provided, the function will prompt the user to select a polyline.
        :param margin_size: margin size in pixels for cropping around the polyline
        :param new_window: set to False.
        :return: True if the image is cropped, False otherwise.

        """

        if (polyline is None) | (polyline == []):
            thepolylines = self.pjs.polylines[self.pjs.curslice]

            if thepolylines == [] or thepolylines[0] == []:
                return False

            # prompt user to select polyline
            self.pjs.statusbar.showMessage('Select polygon for cropping.')
            self.pjs.annotation_mode = PyJAMAS.select_polyline_crop
            return True

        minx, miny, maxx, maxy = self.get_coordinate_bounds(coordinates=polyline, margin_size=margin_size)

        self.perform_crop(minx=minx, miny=miny, maxx=maxx, maxy=maxy, new_window=new_window)

        # return to previous annotation mode
        self.pjs.annotation_mode = self.pjs.no_annotations

        return True

    def perform_crop(self, minx: int = 0, miny: int = 0, maxx: int = 0, maxy: int = 0, new_window: bool = False):
        # Get cropped image
        cropped_image = self.pjs.slices[:, miny:(maxy + 1), minx:(maxx + 1)]

        # Keep fiducials/polylines within crop region
        transform = QtGui.QTransform()
        transform.translate(-minx, -miny)

        new_fiducials, new_polylines = self.transform_annotations(transform, (cropped_image.shape[2], cropped_image.shape[1]))

        # Open in current window or new window?
        if not new_window:
            self.pjs.undo_stack.push(
                {'changetype': undo_modes.IMAGE, 'frame': self.pjs.slices,
                 'index': self.pjs.curslice,
                 'details': self.pjs.copy_annotations()})

            # Crop.
            self.pjs.io.cbLoadArray(cropped_image)
            # apply transformed fiducials/polylines
            self.pjs.fiducials = new_fiducials
            self.pjs.polylines = new_polylines
            self.pjs.repaint()

        else:
            # Create new pyjamas and crop.
            new_pjs: PyJAMAS = PyJAMAS()
            new_pjs.io.cbLoadArray(cropped_image)
            # apply transformed fiducials/polylines
            new_pjs.fiducials = new_fiducials
            new_pjs.polylines = new_polylines
            new_pjs.repaint()

        return True

    def cbKymograph(self, polyline: Optional[numpy.ndarray] = None, margin_size: int = 0, new_window: bool = False) -> bool:
        """
        Kymograph of an image region.

        :param polyline: ndarray with two columns containing the x, y coordinates of the region to crop; if not provided, the function will prompt the user to select a polyline.
        :param margin_size: margin size in pixels for cropping around the polyline
        :param new_window: set to False.
        :return: True if the kymograph is created, False otherwise.
        """
        if (polyline is None) | (polyline == []):
            thepolylines = self.pjs.polylines[self.pjs.curslice]

            if thepolylines == [] or thepolylines[0] == []:
                return False

            # prompt user to select polyline
            self.pjs.statusbar.showMessage('Select polygon for kymograph.')
            self.pjs.annotation_mode = PyJAMAS.select_polyline_kymo
            return True

        minx, miny, maxx, maxy = self.get_coordinate_bounds(coordinates=polyline, margin_size=margin_size)

        # Make kymograph.
        thekymo = rimutils.kymograph(self.pjs.slices, numpy.asarray([[minx, miny], [maxx, maxy]]))

        # Open in current window or new window?
        if not new_window:
            # Save current image.
            self.pjs.undo_stack.push(
                {'changetype': undo_modes.IMAGE, 'frame': self.pjs.slices,
                 'index': self.pjs.curslice,
                 'details': self.pjs.copy_annotations()})

            self.pjs.io.cbLoadArray(thekymo)
        else:
            # Create new pyjamas and crop.
            new_pjs: PyJAMAS = PyJAMAS()
            new_pjs.io.cbLoadArray(thekymo)

        return True

    def cbZoom(self, zoom_index: int = -1):
        """
        Zoom in/out of the open image.

        :param zoom_index: index into a tuple of possible zoom factors (PyJAMAS.zoom_factors).
        :return:
        """

        # When callbacks are assigned with addMenuItem, if no parameter values are provided
        # (using partial), they are set to False if the callback is triggered by pressing on the menu option,
        # and to the default value if using the quick key. This here ensures that zoom_index is not False.
        if zoom_index is False:
            zoom_index = -1

        self.pjs.gView.scale(1. / PyJAMAS.zoom_factors[self.pjs.zoom_index],
                             1. / PyJAMAS.zoom_factors[self.pjs.zoom_index])

        if 0 <= zoom_index < len(PyJAMAS.zoom_factors):
            self.pjs.zoom_index = zoom_index
        else:
            self.pjs.zoom_index = (self.pjs.zoom_index + 1) % len(PyJAMAS.zoom_factors)

        self.pjs.gView.scale(PyJAMAS.zoom_factors[self.pjs.zoom_index], PyJAMAS.zoom_factors[self.pjs.zoom_index])
        self.pjs.MainWindow.resize(self.pjs.width * self.pjs.zoom_factors[self.pjs.zoom_index],
                                   self.pjs.height * self.pjs.zoom_factors[self.pjs.zoom_index] + 60)
        self.pjs.statusbar.showMessage(str(self.pjs.curslice + 1) + '/' + str(self.pjs.n_frames) +
                                       ' zoom: ' + str(PyJAMAS.zoom_factors[self.pjs.zoom_index]) + 'x')

        return True

    def cbNextFrame(self) -> bool:
        """
        Advance to the next slice (or move to the first slice if currently on the last one).

        :return: True.
        """
        if self.pjs.curslice < self.pjs.n_frames - 1:
            self.pjs.curslice = self.pjs.curslice + 1
        elif self.pjs.curslice == self.pjs.n_frames - 1:
            self.pjs.curslice = 0

        self.pjs.imagedata = self.pjs.slices[self.pjs.curslice]
        self.pjs.timeSlider.setValue(self.pjs.curslice + 1)

        self.pjs.displayData()

        return True

    def cbPrevFrame(self) -> bool:
        """
        Move to the previous slice (or to the last one if currently on the first one).

        :return: True.
        """
        if self.pjs.curslice > 0:
            self.pjs.curslice = self.pjs.curslice - 1
        elif self.pjs.curslice == 0:
            self.pjs.curslice = self.pjs.n_frames - 1

        self.pjs.imagedata = self.pjs.slices[self.pjs.curslice]
        self.pjs.timeSlider.setValue(self.pjs.curslice + 1)

        self.pjs.displayData()

        return True

    def cbTimeSlider(self) -> bool:
        """
        Jump to the slice indicated by the value of the time slider on the display window.

        :return: True.
        """
        self.pjs.curslice = self.pjs.timeSlider.value() - 1
        self.pjs.imagedata = self.pjs.slices[self.pjs.curslice]

        self.pjs.displayData()

        return True

    def cbGoTo(self, slice_index: int) -> bool:
        """
        Jump to a specific slice.

        :param slice_index: index (minimum value is zero) of the slice to jump to; negative values start start pointing from the last slice (-1 being the last one).
        :return: True if the jump occurred, False if the index is out of range.
        """

        if slice_index >= self.pjs.n_frames:
            return False

        if slice_index < 0:
            slice_index = self.pjs.n_frames + slice_index
        if slice_index < 0:
            return False

        self.pjs.curslice = slice_index
        self.pjs.imagedata = self.pjs.slices[self.pjs.curslice]
        self.pjs.timeSlider.setValue(slice_index + 1)

        self.pjs.displayData()

        return True

    def cbDisplayInfo(self) -> bool:
        """
        Displays information related to the image currently open in PyJAMAS.

        :return: True.
        """

        dialog = dialogs.textdialog.TextDialog(str(self.pjs), "Info")
        dialog.show()

        return True

    def cbFindSeeds(self, firstSlice: Optional[int] = None, lastSlice: Optional[int] = None,
                    sigma: Optional[float] = None, window_size: Optional[int] = None,
                    bindilation: Optional[int] = None, mindist: Optional[float] = None, preview: Optional[bool] = None,
                    wait_for_thread: bool = False) -> bool:
        """
        Find seeds for watershed-based object segmentation. Uses a combination of Gaussian blurring, adative thresholding to find object boundaries and a distance transform.

        A dialog will be opened if any parameters are set to None.

        :param firstSlice: slice number for the first slice to use (minimum is 1).
        :param lastSlice: slice number for the last slice to use.
        :param sigma: standard deviation of the Gaussian filter applied to smoothen the image.
        :param window_size: width in pixels of the window size used to calculate the local threshold (useful when segmenting objects with bright boundaries and dark interiors - e.g. cells expressing fluorescent membrane markers).
        :param bindilation: positive values conduct binary closings after local thresholding to remove discontinuities in bright features, negative values conduct binary openings (useful when segmenting bright objects separated by a dark background - e.g. fluorescent cell nuclei).
        :param mindist: minimum distance transform value to consider a pixel significantly far from edges and part of the local maxima; if negative, a local threshold of the distance transform is used to calculate its local maxima.
        :param preview: True to open a window with a preview of parameter values, False otherwise.
        :param wait_for_thread: True if PyJAMAS must wait for the thread running this operation to complete, False otherwise.
        :return: True if seed detection runs, False if the process is cancelled.
        """

        # If not enough parameters, open a dialog.
        if (firstSlice is False or firstSlice is None or lastSlice is False or lastSlice is None or
            window_size is False or window_size is None or sigma is False or sigma is None or bindilation is False or
            bindilation is None or mindist is False or mindist is None or preview is None) and self.pjs is not None:
            dialog = QtWidgets.QDialog()
            ui = dialogs.findseeds.FindSeedsDialog(self.pjs)
            lastSlice = 1 if self.pjs.n_frames == 1 else self.pjs.slices.shape[0]
            ui.setupUi(dialog, firstslice=self.pjs.curslice + 1, lastslice=lastSlice,
                       gaussian_sigma=dialogs.findseeds.FindSeedsDialog.gaussianSigma,
                       winsz=dialogs.findseeds.FindSeedsDialog.window_size,
                       bindilation=dialogs.findseeds.FindSeedsDialog.binary_dilation_number,
                       mindist=dialogs.findseeds.FindSeedsDialog.min_distance_transform,
                       preview_flag=dialogs.findseeds.FindSeedsDialog.preview)

            # If you try to make this dialog non-modal, make sure to switch from dialog to using self.dialog.
            # Otherwise, when you delete the exec line and the method ends, there are no references to the
            # dialog object and it will disappear.
            # You will also need to comment out the dialog.close() below.
            dialog.exec_()
            dialog.show()

            # If the dialog was closed by pressing OK, then run the measurements.
            continue_flag = dialog.result() == QtWidgets.QDialog.Accepted
            theparameters = ui.parameters()

            dialog.close()

        else:
            theparameters = {'first': firstSlice, 'last': lastSlice, 'window_size': window_size, 'sigma': sigma,
                             'binary_dilation_number': bindilation,
                             'min_distance_transform': mindist, 'preview': preview}
            continue_flag = True

        # When you have the input parameters:
        if continue_flag:
            # Propagate forward.
            if theparameters['first'] <= theparameters['last']:
                theslicenumbers = numpy.arange(theparameters['first'] - 1, theparameters['last'])

            # Propagate backwards.
            else:
                theslicenumbers = numpy.arange(theparameters['first'] - 1, theparameters['last'] - 2, -1)

            # But DO propagate!!
            """if run_in_thread:
                self.launch_thread(self.findSeeds, {'parameters': theparameters, 'theslices': theslicenumbers, 'progress': True}, finished_fn=self.finished_fn, progress_fn=self.progress_fn)
            else:
                self.findSeeds(theparameters, theslicenumbers)
                self.pjs.repaint()
            """
            start = min(theparameters['first'], theparameters['last'])
            end = max(theparameters['first'], theparameters['last'])
            self.pjs.undo_stack.push({'changetype': undo_modes.MULTI, 'frame': (start - 1, end), 'index': (True, False), 'details': self.pjs.copy_annotations((start-1, end))})

            self.launch_thread(self.findSeeds,
                               {'parameters': theparameters, 'theslices': theslicenumbers, 'progress': True},
                               finished_fn=self.finished_fn, progress_fn=self.progress_fn,
                               wait_for_thread=wait_for_thread)

        return continue_flag

    def cbSegmentDetectedObjects(self, firstSlice: Optional[int] = None, lastSlice: Optional[int] = None,
                                 sigma: Optional[float] = None,
                                 wait_for_thread: bool = False) -> bool:
        """
        Segment individual objects included within polylines. Places a seed in the centre of each polyline and a second one in the dimmest corner, and runs a watershed-based segmentation.

        A dialog will be opened if any parameters are set to None.

        :param firstSlice: slice number for the first slice to use (minimum is 1).
        :param lastSlice: slice number for the last slice to use.
        :param sigma: standard deviation of the Gaussian filter applied to smoothen the image.
        :param wait_for_thread: True if PyJAMAS must wait for the thread running this operation to complete, False otherwise.
        :return: True if the segmentation runs, False if the process is cancelled.
        """

        continue_flag: bool = False

        # If not enough parameters, open a dialog.
        if (firstSlice is False or firstSlice is None or lastSlice is False or lastSlice is None or
            sigma is False or sigma is None) and self.pjs is not None:

            firstSlice = self.pjs.curslice + 1

            lastSlice = 1 if self.pjs.n_frames == 1 else self.pjs.slices.shape[0]
            dialog = QtWidgets.QDialog()
            ui = dialogs.expandseeds.ExpandSeedsDialog()

            ui.setupUi(dialog, firstslice=firstSlice, lastslice=lastSlice,
                       gaussian_sigma=dialogs.expandseeds.ExpandSeedsDialog.gaussianSigma)
            dialog.exec_()
            dialog.show()
            # If the dialog was closed by pressing OK, then run the measurements.
            continue_flag = dialog.result() == QtWidgets.QDialog.Accepted
            theparameters = ui.parameters()

            dialog.close()

        else:
            theparameters = {'first': firstSlice, 'last': lastSlice, 'sigma': sigma}
            continue_flag = True

        # When you have the input parameters:
        if continue_flag:
            # Propagate forward.
            if theparameters['first'] <= theparameters['last']:
                theslicenumbers = numpy.arange(theparameters['first'] - 1, theparameters['last'])

            # Propagate backwards.
            else:
                theslicenumbers = numpy.arange(theparameters['first'] - 1, theparameters['last'] - 2, -1)

            # But DO propagate!!
            """if run_in_thread:
                self.launch_thread(self.segmentROIs, {'parameters': theparameters, 'theslices': theslicenumbers, 'progress': True}, finished_fn=self.finished_fn, stop_fn=self.stop_fn, progress_fn=self.progress_fn)
            else:
            self.segmentROIs(theparameters, theslicenumbers)
            self.pjs.repaint()
            """
            self.launch_thread(self.segmentROIs,
                               {'parameters': theparameters, 'theslices': theslicenumbers, 'progress': True},
                               finished_fn=self.finished_fn, stop_fn=self.stop_fn, progress_fn=self.progress_fn,
                               wait_for_thread=wait_for_thread)

        return continue_flag

    def cbPropagateSeeds(self, firstSlice: Optional[int] = None, lastSlice: Optional[int] = None,
                         xcorrWindowSize: Optional[int] = None,
                         wait_for_thread: bool = False) -> bool:
        """
        Transfer fiducials to subsequent slices. The displacement across slices is quantified based on the local cross-correlation and applied to the seeds.

        A dialog will be opened if any parameters are set to None.

        :param firstSlice: slice number for the first slice to use (minimum is 1).
        :param lastSlice: slice number for the last slice to use.
        :param xcorrWindowSize: width in pixels of the window size used to calculate the local cross-correlation.
        :param wait_for_thread: True if PyJAMAS must wait for the thread running this operation to complete, False otherwise.
        :return: True if seed propagation runs, False if the process is cancelled.
        """
        # If not enough parameters, open a dialog.
        if (
                firstSlice is False or firstSlice is None or lastSlice is False or lastSlice is None or xcorrWindowSize is False or xcorrWindowSize is None) and self.pjs is not None:
            dialog = QtWidgets.QDialog()
            ui = dialogs.propagateseeds.PropagateSeedsDialog()
            lastSlice = 1 if self.pjs.n_frames == 1 else self.pjs.slices.shape[0]
            ui.setupUi(dialog, firstslice=self.pjs.curslice + 1, lastslice=lastSlice,
                       xcorrwinsz=dialogs.propagateseeds.PropagateSeedsDialog.window_size)
            dialog.exec_()
            dialog.show()
            # If the dialog was closed by pressing OK, then run the measurements.
            continue_flag = dialog.result() == QtWidgets.QDialog.Accepted
            theparameters = ui.parameters()

            dialog.close()

        else:
            theparameters = {'first': firstSlice, 'last': lastSlice, 'xcorr_win_sz': xcorrWindowSize}
            continue_flag = True

        # When you have the input parameters:
        if continue_flag:
            # Propagate forward.
            if theparameters['first'] <= theparameters['last']:
                theslicenumbers = numpy.arange(theparameters['first'] - 1, theparameters['last'])

            # Propagate backwards.
            else:
                theslicenumbers = numpy.arange(theparameters['first'] - 1, theparameters['last'] - 2, -1)

            # But DO propagate!!
            """if run_in_thread:
                self.launch_thread(self.propagateSeeds, {'parameters': theparameters, 'theslices': theslicenumbers, 'progress': True, 'stop': True}, finished_fn=self.finished_fn, stop_fn=self.stop_fn, progress_fn=self.progress_fn)
            else:
                self.propagateSeeds(theparameters, theslicenumbers)
                self.pjs.repaint()
            """

            start = min(theparameters['first'], theparameters['last'])
            end = max(theparameters['first'], theparameters['last'])
            self.pjs.undo_stack.push({'changetype': undo_modes.MULTI, 'frame': (start - 1, end), 'index': (True, False), 'details': self.pjs.copy_annotations((start-1, end))})

            self.launch_thread(self.propagateSeeds,
                               {'parameters': theparameters, 'theslices': theslicenumbers, 'progress': True,
                                'stop': True}, finished_fn=self.finished_fn, stop_fn=self.stop_fn,
                               progress_fn=self.progress_fn, wait_for_thread=wait_for_thread)

        return continue_flag

    def cbCentroidSeeds(self, firstSlice: Optional[int] = None, lastSlice: Optional[int] = None,
                        wait_for_thread: bool = False) -> bool:
        """
        Add one fiducial at the centroid of each polyline.

        A dialog will be opened if any parameters are set to None.

        :param firstSlice: slice number for the first slice to use (minimum is 1).
        :param lastSlice: slice number for the last slice to use.
        :param wait_for_thread: True if PyJAMAS must wait for the thread running this operation to complete, False otherwise.
        :return: True if centroid fiducials are added, False if the process is cancelled.
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
            # Propagate forward.
            if theparameters['first'] <= theparameters['last']:
                theslicenumbers = numpy.arange(theparameters['first'] - 1, theparameters['last'])

            # Propagate backwards.
            else:
                theslicenumbers = numpy.arange(theparameters['first'] - 1, theparameters['last'] - 2, -1)

            # But DO propagate!!
            """if run_in_thread:
                self.launch_thread(self.centroidSeeds,
                                   {'theslices': theslicenumbers, 'progress': True},
                                   finished_fn=self.finished_fn, stop_fn=self.stop_fn, progress_fn=self.progress_fn)
            else:
                self.centroidSeeds(theslicenumbers)
                self.pjs.repaint()
            """

            start = min(theparameters['first'], theparameters['last'])
            end = max(theparameters['first'], theparameters['last'])
            self.pjs.undo_stack.push({'changetype': undo_modes.MULTI, 'frame': (start - 1, end), 'index': (True, False), 'details': self.pjs.copy_annotations((start-1, end))})

            self.launch_thread(self.centroidSeeds,
                               {'theslices': theslicenumbers, 'progress': True},
                               finished_fn=self.finished_fn, stop_fn=self.stop_fn, progress_fn=self.progress_fn,
                               wait_for_thread=wait_for_thread)

        return continue_flag

    def cbExpandSeeds(self, firstSlice: Optional[int] = None, lastSlice: Optional[int] = None,
                      sigma: Optional[float] = None, wait_for_thread: bool = False) -> bool:
        """
        Expand fiducials using the watershed algorithm.

        A dialog will be opened if any parameters are set to None.

        :param firstSlice: slice number for the first slice to use (minimum is 1).
        :param lastSlice: slice number for the last slice to use.
        :param sigma: standard deviation of the Gaussian filter applied to smoothen the image.
        :param wait_for_thread: True if PyJAMAS must wait for the thread running this operation to complete, False otherwise.
        :return: True if seed expansion runs, False if the process is cancelled.
        """

        # If not enough parameters, open a dialog.
        if (
                firstSlice is False or firstSlice is None or lastSlice is False or lastSlice is None or sigma is False or sigma is None) and self.pjs is not None:
            dialog = QtWidgets.QDialog()
            ui = dialogs.expandseeds.ExpandSeedsDialog()

            firstSlice = self.pjs.curslice + 1

            lastSlice = 1 if self.pjs.n_frames == 1 else self.pjs.slices.shape[0]
            ui.setupUi(dialog, firstslice=firstSlice, lastslice=lastSlice,
                       gaussian_sigma=dialogs.expandseeds.ExpandSeedsDialog.gaussianSigma)
            dialog.exec_()
            dialog.show()
            # If the dialog was closed by pressing OK, then run the measurements.
            continue_flag = dialog.result() == QtWidgets.QDialog.Accepted
            theparameters = ui.parameters()

            dialog.close()

        else:
            theparameters = {'first': firstSlice, 'last': lastSlice, 'sigma': sigma}
            continue_flag = True

        # When you have the input parameters:
        if continue_flag:
            # Expand forward.
            if theparameters['first'] <= theparameters['last']:
                theslicenumbers = numpy.arange(theparameters['first'] - 1, theparameters['last'])

            # Expand backwards.
            else:
                theslicenumbers = numpy.arange(theparameters['first'] - 1, theparameters['last'] - 2, -1)

            # But DO expand!!
            """if run_in_thread:
                self.launch_thread(self.expandSeeds,
                                   {'parameters': theparameters, 'theslices': theslicenumbers, 'progress': True},
                                   finished_fn=self.finished_fn, stop_fn=self.stop_fn, progress_fn=self.progress_fn)
            else:
                self.expandSeeds(theparameters, theslicenumbers)
                self.pjs.repaint()
            """
            start = min(theparameters['first'], theparameters['last'])
            end = max(theparameters['first'], theparameters['last'])
            self.pjs.undo_stack.push({'changetype': undo_modes.MULTI, 'frame': (start - 1, end), 'index': (False, True), 'details': self.pjs.copy_annotations((start-1, end))})

            self.launch_thread(self.expandSeeds,
                               {'parameters': theparameters, 'theslices': theslicenumbers, 'progress': True},
                               finished_fn=self.finished_fn, stop_fn=self.stop_fn, progress_fn=self.progress_fn,
                               wait_for_thread=wait_for_thread)

        return continue_flag

    def cbExpandNPropagateSeeds(self, firstSlice: Optional[int] = None, lastSlice: Optional[int] = None,
                                sigma: Optional[float] = None, xcorrWindowSize: Optional[int] = None,
                                wait_for_thread: bool = False) -> bool:
        """
        Expand fiducials using the watershed algorithm, and propagate the fiducials to the next slice, calculating the displacement to apply based on the local cross-correlation. Fiducials closer to the object edge than pjs.CENTER_SEEDS_CLOSER_TO_THE_EDGE, are moved to the object centroid before propagation.

        A dialog will be opened if any parameters are set to None.

        :param firstSlice: slice number for the first slice to use (minimum is 1).
        :param lastSlice: slice number for the last slice to use.
        :param sigma: standard deviation of the Gaussian filter applied to smoothen the image.
        :param xcorrWindowSize: width in pixels of the window size used to calculate the local cross-correlation.
        :param wait_for_thread: True if PyJAMAS must wait for the thread running this operation to complete, False otherwise.
        :return: True if expand and propagate runs, False if the process is cancelled.
        """
        # If not enough parameters, open a dialog.
        if (firstSlice is False or firstSlice is None or lastSlice is False or lastSlice is None
            or xcorrWindowSize is False or xcorrWindowSize is None or sigma is False or sigma is None) \
                and self.pjs is not None:
            dialog = QtWidgets.QDialog()
            ui = dialogs.expandnpropagateseeds.ExpandNPropagateSeedsDialog()
            lastSlice = 1 if self.pjs.n_frames == 1 else self.pjs.slices.shape[0]
            ui.setupUi(dialog, firstslice=self.pjs.curslice + 1, lastslice=lastSlice,
                       gaussian_sigma=dialogs.expandnpropagateseeds.ExpandNPropagateSeedsDialog.gaussianSigma,
                       xcorrwinsz=dialogs.expandnpropagateseeds.ExpandNPropagateSeedsDialog.window_size)
            dialog.exec_()
            dialog.show()
            # If the dialog was closed by pressing OK, then run the measurements.
            continue_flag = dialog.result() == QtWidgets.QDialog.Accepted
            theparameters = ui.parameters()

            dialog.close()

        else:
            theparameters = {'first': firstSlice, 'last': lastSlice, 'sigma': sigma, 'xcorr_win_sz': xcorrWindowSize}
            continue_flag = True

        # When you have the input parameters:
        if continue_flag:
            # Expand forward.
            if theparameters['first'] <= theparameters['last']:
                theslicenumbers = numpy.arange(theparameters['first'] - 1, theparameters['last'])

            # Expand backwards.
            else:
                theslicenumbers = numpy.arange(theparameters['first'] - 1, theparameters['last'] - 2, -1)

            # But DO expand!!
            """if wait_for_thread:
                self.launch_thread(self.expandNPropagateSeeds,
                                   {'parameters': theparameters, 'theslices': theslicenumbers,
                                    'progress': True, 'stop': True},
                                   finished_fn=self.finished_fn, stop_fn=self.stop_fn, progress_fn=self.progress_fn)
            else:
                self.expandNPropagateSeeds(theparameters, theslicenumbers)
                self.pjs.repaint()
            """
            start = min(theparameters['first'], theparameters['last'])
            end = max(theparameters['first'], theparameters['last'])
            self.pjs.undo_stack.push({'changetype': undo_modes.MULTI, 'frame': (start - 1, end), 'index': (True, True), 'details': self.pjs.copy_annotations((start-1, end))})

            self.launch_thread(self.expandNPropagateSeeds,
                               {'parameters': theparameters, 'theslices': theslicenumbers,
                                'progress': True, 'stop': True},
                               finished_fn=self.finished_fn, stop_fn=self.stop_fn, progress_fn=self.progress_fn,
                               wait_for_thread=wait_for_thread)

        return continue_flag

    def propagateSeeds(self, parameters: dict, theslices: numpy.ndarray,
                       progress_signal: Optional[ThreadSignals] = None,
                       stop_signal: Optional[ThreadSignals] = None) -> bool:

        xcorr_win_sz = parameters.get('xcorr_win_sz', RCBImage.DEFAULT_WINDOW_SZ)

        # Make sure that the slices are in a 1D numpy array.
        theslices = numpy.atleast_1d(theslices)
        num_slices = theslices.size

        # Make sure there are fiducials to move.
        if len(self.pjs.fiducials[theslices[0]]) == 0:
            if stop_signal is not None:
                stop_signal.emit(f"Stopping at slice {theslices[0] + 1}: there are no fiducials to move there.")
            return False

        # For every slice ...
        for i in range(num_slices - 1):
            # Calculate the optic flow between consecutive images and interpolate at the fiducials.
            #Xflow, Yflow, _, _ = rimutils.flow(skimage.filters.gaussian(self.pjs.slices[theslices[i]], parameters['sigma'], multichannel=False),
            #                                   skimage.filters.gaussian(self.pjs.slices[theslices[i+1]], parameters['sigma'], multichannel=False),
            #                                   numpy.array(self.pjs.fiducials[theslices[i]]), xcorr_win_sz)

            flow_vectors = rimutils.flow_at_points(self.pjs.slices[theslices[i]], self.pjs.slices[theslices[i + 1]],
                                                   numpy.array(self.pjs.fiducials[theslices[i]])[:, 1::-1], xcorr_win_sz)

            Xflow = flow_vectors[:, 1]
            Yflow = flow_vectors[:, 0]

            # Shift the position of the fiducials in this slice by the flow ... In this case, the polyline are
            # organized as [x, y], as they come from the fiducial list in PyJAMAS.
            destination_point_array = numpy.array(self.pjs.fiducials[theslices[i]])
            destination_point_array[:, 0] = numpy.int64(numpy.round(
                numpy.float64(destination_point_array[:, 0]) + Xflow))  # X coordinate.
            destination_point_array[:, 1] = numpy.int64(numpy.round(
                numpy.float64(destination_point_array[:, 1]) + Yflow))  # Y coordinate.

            # Here we should clip the fiducials at the ends so that seeds do not go beyond image margins.
            # ind2 = find(next_seeds(:, 1) < 0);
            # next_seeds(intersect(ind, ind2), 1) = 0;
            # ind2 = find(next_seeds(:, 1) >= ud.imsize(1));
            # next_seeds(intersect(ind, ind2), 1) = ud.imsize(1) - 1;
            # ind2 = find(next_seeds(:, 2) < 0);
            # next_seeds(intersect(ind, ind2), 2) = 0;
            # ind2 = find(next_seeds(:, 2) >= ud.imsize(2));
            # next_seeds(intersect(ind, ind2), 2) = ud.imsize(2) - 1;

            # ... before copying them onto the next slice.
            self.pjs.fiducials[theslices[i + 1]] = destination_point_array.tolist()

            # Only emit progress signal if doing more than one slice.
            if num_slices > 1 and progress_signal is not None:
                progress_signal.emit(int((100 * (i + 1)) / (num_slices - 1)))

        return True

    def centroidSeeds(self, theslices: numpy.ndarray, progress_signal: ThreadSignals = None) -> bool:

        # Make sure that the slices are in a 1D numpy array.
        theslices = numpy.atleast_1d(theslices)
        num_slices = theslices.size

        # For every slice ...
        for i in range(num_slices):
            thepolylines = [RUtils.qpolygonf2polygon(one_polyline) for one_polyline in self.pjs.polylines[theslices[i]]]

            for one_polyline in thepolylines:
                polycentroid = one_polyline.centroid
                self.pjs.addFiducial(int(polycentroid.x), int(polycentroid.y), theslices[i], paint=False)

            # Only emit progress signal if doing more than one slice.
            if num_slices > 1 and progress_signal is not None:
                progress_signal.emit(int((100 * (i + 1)) / num_slices))

        return True

    def findSeeds(self, parameters, theslices, progress_signal: ThreadSignals = None) -> bool:
        # Make sure that the slices are in a 1D numpy array.
        theslices = numpy.atleast_1d(theslices)
        num_slices = theslices.size

        # For every slice ...
        for i in range(num_slices):
            theimage = self.pjs.slices[theslices[i]].copy()
            theimage = skimage.filters.gaussian(theimage, parameters['sigma'])
            # Expand the seeds in the image.
            # ADD WHEELS TO DIALOG FOR WINDOW_SIZE, OPENING/CLOSING SIZE, MIN_DT_VALUE
            seed_coordinates, _ = rimutils.find_seeds(theimage,
                                                      parameters.get('window_size', RCBImage.DEFAULT_WINDOW_SZ),
                                                      parameters.get('binary_dilation_number',
                                                                     RCBImage.DEFAULT_BINARY_DILATIONS),
                                                      parameters.get('min_distance_transform',
                                                                     RCBImage.DEFAULT_MINIMUM_DISTANCE_TRANSFORM),
                                                      )

            # Add the polyline to the list of fiducials.
            for aSeed in seed_coordinates:
                self.pjs.addFiducial(aSeed[1], aSeed[0], theslices[i], paint=False)

            # Only emit progress signal if doing more than one slice.
            if num_slices > 1 and progress_signal is not None:
                progress_signal.emit(int((100 * (i + 1)) / num_slices))

        return True

    def segmentROIs(self, parameters, theslices, progress_signal: ThreadSignals = None) -> bool:

        centre_seeds: bool = parameters.get('centre_seeds', True)

        # Make sure that the slices are in a 1D numpy array.
        theslices = numpy.atleast_1d(theslices)
        num_slices = theslices.size

        one = numpy.uint(1)

        # For every slice ...
        for i in range(num_slices):
            theimage: numpy.ndarray = self.pjs.slices[theslices[i]].copy()

            theimage = skimage.filters.gaussian(theimage, parameters.get('sigma', 0), multichannel=False)

            therois = self.pjs.polylines[theslices[
                i]].copy()  # without this copy instruction, the loop below will also go through newly added (within the loop) polygons

            theindex = -1

            # For every ROI ...
            for aroi in therois:
                theindex += 1
                # This code borrowed from cbCrop. Places a seed at the center of the bounding box.
                # Because most classifiers will "detect" objects using rectangles, this works well. here.
                if aroi == [] or aroi.count() != 5 or aroi[0] != aroi[-1]:
                    continue

                minx, miny, maxx, maxy = aroi.boundingRect().getCoords()
                minx, miny, maxx, maxy = numpy.uint((minx, miny, maxx, maxy))
                roi_im: numpy.ndarray = theimage[miny:(maxy + one), minx:(maxx + one)]
                rows, columns = roi_im.shape
                roi_area = rows * columns
                corner_coords = numpy.asarray([[0, 0], [0, columns - 1], [rows - 1, columns - 1], [rows - 1, 0]],
                                              dtype=numpy.int16)  # in row, col

                # Find seeds only within the roi.
                if centre_seeds:
                    seed_coordinates = numpy.asarray([[(miny + maxy) / 2 - miny, (minx + maxx) / 2 - minx]],
                                                     dtype=numpy.int16)
                else:
                    seed_coordinates, _ = rimutils.find_seeds(roi_im,
                                                              parameters.get('window_size', RCBImage.DEFAULT_WINDOW_SZ),
                                                              parameters.get('binary_dilation_number',
                                                                             RCBImage.DEFAULT_BINARY_DILATIONS),
                                                              parameters.get('min_distance_transform',
                                                                             RCBImage.DEFAULT_MINIMUM_DISTANCE_TRANSFORM),
                                                              )

                    # if more than one seed, keep only the central one.

                # Add the polyline to the list of fiducials.
                for aSeed in seed_coordinates:
                    self.pjs.addFiducial(minx + aSeed[1], miny + aSeed[0], theslices[i], paint=False)

                # Find the dimmest corner of the image gradient to be used as background seed.
                roi_grad: numpy.ndarray = ndimage.gaussian_gradient_magnitude(roi_im, parameters['sigma'])
                ind: int = numpy.argmin(roi_im[corner_coords[:, 0], corner_coords[:, 1]])
                theseeds: numpy.ndarray = numpy.vstack((corner_coords[ind, [1, 0]], seed_coordinates[:, [1, 0]]))

                # dimmest_pnt = numpy.unravel_index(numpy.argmin(roi_im), roi_im.shape)
                # theseeds: numpy.ndarray = numpy.vstack((dimmest_pnt[::-1], seed_coordinates[:, [1, 0]]))

                # Expand the seeds on the gradient of the roi.
                contour_list = rimutils.waterseed(roi_grad, theseeds)

                # NOTE: the goal here is to have one background and one object seed. TYPICALLY, the binary masks
                # for each of the two labels will be the opposite of each other. But find_contours, used
                # in rimutils.waterseed to extract contours from binary images, will detect zero crossings, and thus
                # will return the same contour for both. So below, we will discard the first contour (the one
                # corresponding to the background seed).
                if contour_list != []:
                    contour_list = contour_list[1:]
                # If watershed did not work, just try a local threshold.
                else:
                    contour_list = rimutils.local_threshold_segm(roi_im, window_size=self.DEFAULT_WINDOW_SZ / 2,
                                                                 binary_dilation_radius=self.DEFAULT_BINARY_DILATIONS / 2,
                                                                 border_objects=False)

                # Add the contours to the list of annotations.
                # Take only 1 contour in each case, and only if the contour covers at least 5% of the ROI area.
                if contour_list != []:
                    contour_areas = []
                    for aContour in contour_list:
                        contour_areas.append(RPolyline(aContour).area())

                    ind_max = numpy.argmax(numpy.asarray(contour_areas))

                    aContour = contour_list[ind_max]
                    if contour_areas[ind_max] >= .05 * roi_area:
                        for aPoint in aContour:
                            aPoint[0], aPoint[1] = aPoint[0] + minx, aPoint[1] + miny

                        self.pjs.replacePolyline(theindex, aContour, theslices[i], paint=False)

                # Only emit progress signal if doing more than one slice.
                if num_slices > 1 and progress_signal is not None:
                    progress_signal.emit(int((100 * (i + 1)) / num_slices))

        return True

    def expandSeeds(self, parameters: dict, theslices: numpy.ndarray,
                    progress_signal: Optional[ThreadSignals] = None) -> bool:
        # Make sure that the slices are in a 1D numpy array.
        theslices = numpy.atleast_1d(theslices)
        num_slices = theslices.size

        # For every slice ...
        for i in range(num_slices):
            # Make sure there are fiducials to expand.
            if not self.pjs.fiducials[theslices[i]]:
                continue

            theimage = self.pjs.slices[theslices[i]].copy()
            theimage = skimage.filters.gaussian(theimage, parameters['sigma'])
            # Expand the seeds in the image.
            contour_list = rimutils.waterseed(theimage, numpy.asarray(self.pjs.fiducials[theslices[i]]))
            # Or for gradient-based segmentation:
            # import skimage.filters
            # contour_list = rimutils.waterseed(skimage.filters.sobel(self.pjs.slices[theslices[i]]),
            #                                               numpy.asarray(self.pjs.fiducials[theslices[i]]))

            # Add the contours to the list of annotations.
            for aContour in contour_list:
                self.pjs.addPolyline(aContour, theslices[i],
                                     paint=False)  # pushundo = False so that all new polylines are undone as a single item.

            # Only emit progress signal if doing more than one slice.
            if num_slices > 1 and progress_signal is not None:
                progress_signal.emit(int((100 * (i + 1)) / num_slices))

        return True

    def centerSeeds(self, distance, theslices, exclude_peripheral_seeds=False):
        # Make sure that the slices are in a 1D numpy array.
        theslices = numpy.atleast_1d(theslices)
        num_slices = theslices.size

        # For every slice ...
        for i in range(num_slices):
            thepolylines = [RUtils.qpolygonf2polygon(one_polyline) for one_polyline in self.pjs.polylines[theslices[i]]]

            # Find the concave hull for the fiducials
            if exclude_peripheral_seeds:
                fiducial_hull: numpy.ndarray = RUtils.concave_hull(numpy.asarray(self.pjs.fiducials[theslices[i]]),
                                                                   self.DEFAULT_ALPHA_CONCAVE_HULL)

                if fiducial_hull.size == 0:
                    fiducial_hull = ConvexHull(numpy.asarray(self.pjs.fiducials[theslices[i]]))
            # The problem is that polygons and fiducials are not stored in the same order. Aaaaarghh!
            # Or rather, they are in the same order, but the order is updated when polygons are deleted
            # after touching the edge?
            # An alternative is to find, for each fiducial, an enclosing polygon, and go from there.
            for idx_fiducial, one_fiducial in enumerate(self.pjs.fiducials[theslices[i]]):
                # If peripheral points must be excluded and this is one of them, then skip it.
                if exclude_peripheral_seeds and idx_fiducial in fiducial_hull:
                    continue

                oneShapelyFiducial = Point(one_fiducial)

                for one_polyline in thepolylines:
                    if one_polyline.contains(oneShapelyFiducial):
                        if oneShapelyFiducial.distance(one_polyline.exterior) < distance and \
                                RCBImage._MIN_CELL_AREA < one_polyline.area < RCBImage._MAX_CELL_AREA:
                            polycentroid = one_polyline.centroid
                            self.pjs.fiducials[theslices[i]][idx_fiducial][0] = int(polycentroid.x)
                            self.pjs.fiducials[theslices[i]][idx_fiducial][1] = int(polycentroid.y)

                        break

        return

    def expandNPropagateSeeds(self, parameters: dict, theslices: numpy.ndarray,
                              progress_signal: Optional[ThreadSignals] = None,
                              stop_signal: Optional[ThreadSignals] = None) -> bool:

        # Make sure that the slices are in a 1D numpy array.
        theslices = numpy.atleast_1d(theslices)
        num_slices = theslices.size

        # For every slice ...
        for i in range(num_slices - 1):
            # Expand in the current time point.
            self.expandSeeds(parameters, theslices[i])

            # Center seeds.
            self.centerSeeds(RCBImage.CENTER_SEEDS_CLOSER_TO_THE_EDGE, theslices[i])

            # Propagate to the next time point.
            self.propagateSeeds(parameters, theslices[i:i + 2])

            if progress_signal is not None:
                progress_signal.emit(int((100 * (i + 1)) / num_slices))

        # Finally, expand in the last time point and center the seeds.
        self.expandSeeds(parameters, theslices[-1])

        # Center seeds.
        self.centerSeeds(RCBImage.CENTER_SEEDS_CLOSER_TO_THE_EDGE, theslices[-1])

        if progress_signal is not None:
            progress_signal.emit(int(100))

        return True

    def cbOrthogonalViews(self):
        """
        Display the XZ and YZ planes of a stack at a given point in the 3D image. The XZ and YZ viewers will update automatically as the lines in the main window are moved.

        :return: True if the viewers were successfully opened, False otherwise.
        """

        if self.pjs.slicetracker is None:
            self.pjs.annotations.cbNoAnn()
            
            xWindow = orthogonalViews.MyWidget(self.pjs)
            yWindow = orthogonalViews.MyWidget(self.pjs)
            
            self.pjs.orthogonal_views = orthogonalViews.OrthogonalViewsWindow(self.pjs)
            self.pjs.orthogonal_views.setupUI(xWindow, yWindow)

            xWindow.show()
            yWindow.show()

            self.pjs.slicetracker = (int(self.pjs.width / 2), int(self.pjs.height / 2))

            self.pjs.orthogonal_views.reloadViews()

            return True

        return False

    def cbPropagateBalloons(self, firstSlice: Optional[int] = None, lastSlice: Optional[int] = None,
                            xcorrWindowSize: Optional[int] = None,
                            wait_for_thread: bool = False) -> bool:
        """
        Transfer polylines to subsequent slices. The displacement across slices is quantified based on the local cross-correlation and applied to the seeds. Then re-expand using a balloon (with no balloon force).

        A dialog will be opened if any parameters are set to None.

        :param firstSlice: slice number for the first slice to use (minimum is 1).
        :param lastSlice: slice number for the last slice to use.
        :param xcorrWindowSize: width in pixels of the window size used to calculate the local cross-correlation.
        :param wait_for_thread: True if PyJAMAS must wait for the thread running this operation to complete, False otherwise.
        :return: True if balloon propagation runs, False if the process is cancelled.
        """
        # If not enough parameters, open a dialog.
        if (
                firstSlice is False or firstSlice is None or lastSlice is False or lastSlice is None or xcorrWindowSize is False or xcorrWindowSize is None) and self.pjs is not None:
            dialog = QtWidgets.QDialog()
            ui = dialogs.propagateseeds.PropagateSeedsDialog()
            lastSlice = 1 if self.pjs.n_frames == 1 else self.pjs.slices.shape[0]
            ui.setupUi(dialog, firstslice=self.pjs.curslice + 1, lastslice=lastSlice,
                       xcorrwinsz=dialogs.propagateseeds.PropagateSeedsDialog.window_size)
            dialog.setWindowTitle("Propagate balloons")
            dialog.exec_()
            dialog.show()
            # If the dialog was closed by pressing OK, then run the measurements.
            continue_flag = dialog.result() == QtWidgets.QDialog.Accepted
            theparameters = ui.parameters()

            dialog.close()

        else:
            theparameters = {'first': firstSlice, 'last': lastSlice, 'xcorr_win_sz': xcorrWindowSize}
            continue_flag = True

        # When you have the input parameters:
        if continue_flag:
            # Propagate forward.
            if theparameters['first'] <= theparameters['last']:
                theslicenumbers = numpy.arange(theparameters['first'] - 1, theparameters['last'])

            # Propagate backwards.
            else:
                theslicenumbers = numpy.arange(theparameters['first'] - 1, theparameters['last'] - 2, -1)

            start = min(theparameters['first'], theparameters['last'])
            end = max(theparameters['first'], theparameters['last'])

            self.pjs.undo_stack.push({'changetype': undo_modes.MULTI, 'frame': (start - 1, end), 'index': (False, True),
                                      'details': self.pjs.copy_annotations((start - 1, end))})

            # self.propagateNInflateBalloons(theparameters, theslicenumbers)
            self.launch_thread(self.propagateNInflateBalloons,
                               {'parameters': theparameters, 'theslices': theslicenumbers, 'progress': True,
                                'stop': True}, finished_fn=self.finished_fn, stop_fn=self.stop_fn,
                               progress_fn=self.progress_fn, wait_for_thread=wait_for_thread)

        return continue_flag

    def propagateNInflateBalloons(self, parameters: dict, theslices: numpy.ndarray,
                                  progress_signal: Optional[ThreadSignals] = None,
                                  stop_signal: Optional[ThreadSignals] = None) -> bool:

        # Make sure that the slices are in a 1D numpy array.
        theslices = numpy.atleast_1d(theslices)
        num_slices = theslices.size

        # For every slice ...
        for i in range(num_slices - 1):
            # Inflate balloons.
            self.inflateAllBalloons(theslices[i])

            # Propagate balloons to the next time point.
            self.propagatePolylines(parameters, theslices[i:i + 2])

            if progress_signal is not None:
                progress_signal.emit(int((100 * (i + 1)) / num_slices))

        # Finally, inflate in the last time point.
        self.inflateAllBalloons(theslices[-1])

        if progress_signal is not None:
            progress_signal.emit(int(100))

        return True

    def inflateAllBalloons(self, theslices: numpy.ndarray,
                           progress_signal: Optional[ThreadSignals] = None) -> bool:
        # Make sure that the slices are in a 1D numpy array.
        theslices = numpy.atleast_1d(theslices)
        num_slices = theslices.size

        # For every slice ...
        for i in range(num_slices):
            # Make sure there are polylines to inflate.
            if not self.pjs.polylines[theslices[i]]:
                continue

            thepolylines = [RUtils.qpolygonf2polygon(one_polyline) for one_polyline in self.pjs.polylines[theslices[i]]]
            thepoints = numpy.asarray(
                [[one_polyline.centroid.x, one_polyline.centroid.y] for one_polyline in thepolylines])

            for acentroid in thepoints:
                self.inflateBalloon({'x': acentroid[0], 'y': acentroid[1]}, theslices[i], paint=False)

            # Only emit progress signal if doing more than one slice.
            if num_slices > 1 and progress_signal is not None:
                progress_signal.emit(int((100 * (i + 1)) / (num_slices - 1)))

        return True

    def inflateBalloon(self, parameters: dict, theslices: numpy.ndarray, paint: bool = True) -> bool:
        x: int = int(parameters.get('x'))
        y: int = int(parameters.get('y'))

        # Make sure that the slices are in a 1D numpy array.
        theslices = numpy.atleast_1d(theslices)
        num_slices = theslices.size

        # For every slice ...
        for i in range(num_slices):
            theimage = self.pjs.slices[theslices[i]].copy()

            # Check if the start point was inside an existing polyline and, in that case, delete the polyline
            # (and use it as seed to start balloon).
            init_poly = self.pjs.removePolyline(x, y, theslices[i], paint=paint, pushundo=paint)

            if not init_poly:
                init_ls = numpy.zeros(theimage.shape, dtype=numpy.int8)
                init_ls[max(0, y - 1):min(y + 2, theimage.shape[0]),
                max(0, x - 1):min(x + 2, theimage.shape[1])] = 1

            else:
                init_ls = rimutils.mask_from_polylines(theimage.shape,
                                                       [RUtils.qpolygonf2list(init_poly)], brushsz=1)

            min_row: int = max(0, y - self.pjs.balloon_crop_size)
            max_row: int = min(y + self.pjs.balloon_crop_size, self.pjs.height)
            min_col: int = max(0, x - self.pjs.balloon_crop_size)
            max_col: int = min(x + self.pjs.balloon_crop_size, self.pjs.width)

            # Use the inverse of the image gradient, cropped around the init point.
            invim = rimutils.invert(
                skimage.filters.gaussian(theimage[min_row:max_row, min_col:max_col],
                                         sigma=self.pjs.filter.INFLATE_GAUSSIAN_SIGMA))
            thepoints = rimutils.active_contour(invim,
                                                init_ls[min_row:max_row, min_col:max_col],
                                                self.pjs.filter.balloon_force)

            apoly = rimutils.extract_contours(thepoints)

            if len(apoly) > 0:
                apoly = (numpy.asarray(apoly[0]) + numpy.array(
                    [min_col, min_row])).tolist()  # object 0 is the background.
            else:
                self.pjs.filter.balloon_force = self.pjs.filter.INITIAL_BALLOON_FORCE
                return False

            if len(apoly) <= 2:
                self.pjs.filter.balloon_force = self.pjs.filter.INITIAL_BALLOON_FORCE
                return False

            self.pjs.addPolyline(apoly, theslices[i], paint=paint, pushundo=paint)
        return True

    def propagatePolylines(self, parameters: dict, theslices: numpy.ndarray,
                           progress_signal: Optional[ThreadSignals] = None,
                           stop_signal: Optional[ThreadSignals] = None) -> bool:

        xcorr_win_sz = parameters.get('xcorr_win_sz', RCBImage.DEFAULT_WINDOW_SZ)

        # Make sure that the slices are in a 1D numpy array.
        theslices = numpy.atleast_1d(theslices)
        num_slices = theslices.size

        # Make sure there are polylines to move.
        if len(self.pjs.polylines[theslices[0]]) == 0:
            if stop_signal is not None:
                stop_signal.emit(f"Stopping at slice {theslices[0] + 1}: there are no polylines to move there.")
            return False

        # For every slice ...
        for i in range(num_slices - 1):
            thepolylines = [RUtils.qpolygonf2polygon(one_polyline) for one_polyline in self.pjs.polylines[theslices[i]]]
            thepoints = numpy.asarray(
                [[one_polyline.centroid.y, one_polyline.centroid.x] for one_polyline in thepolylines])

            flow_vectors = rimutils.flow_at_points(self.pjs.slices[theslices[i]], self.pjs.slices[theslices[i + 1]],
                                                   thepoints, xcorr_win_sz)

            # Shift the position of the polylines in this slice by the flow ... In this case, the polyline are
            # organized as [x, y], as they come from the fiducial list in PyJAMAS.
            # self.pjs.polylines[theslices[i+1]] = [one_polyline.translated(one_flow[1], one_flow[0]) for one_polyline, one_flow in zip(self.pjs.polylines[theslices[i]], flow_vectors)]

            for one_polyline, one_flow in zip(self.pjs.polylines[theslices[i]], flow_vectors):
                self.pjs.addPolyline(RUtils.qpolygonf2list(one_polyline.translated(one_flow[1], one_flow[0])),
                                     theslices[i + 1])

            # Only emit progress signal if doing more than one slice.
            if num_slices > 1 and progress_signal is not None:
                progress_signal.emit(int((100 * (i + 1)) / (num_slices - 1)))

        return True
