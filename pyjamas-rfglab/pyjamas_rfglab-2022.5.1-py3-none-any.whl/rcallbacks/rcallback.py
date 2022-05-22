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

import os
from typing import Callable, List, Optional, Tuple

import numpy
from PyQt5 import QtCore, QtGui

import pyjamas.pjscore as pjscore
from pyjamas.pjsthreads import Thread


class RCallback:
    def __init__(self, ui: pjscore.PyJAMAS):
        """

        :type ui: pyjamas.PyJAMAS
        """
        super(RCallback, self).__init__()

        self.pjs = ui

    # Multithreading methods here --------------------------------------------------------------------------------------
    def launch_thread(self, run_fn: Callable, params: Optional[dict] = None, wait_for_thread: bool = False,
                      progress_fn: Optional[Callable] = None, result_fn: Optional[Callable] = None,
                      stop_fn: Optional[Callable] = None,
                      error_fn: Optional[Callable] = None, finished_fn: Optional[Callable] = None):

        athread = Thread(run_fn)

        for a_param in params:
            if a_param == 'progress' and params.get(a_param):
                athread.kwargs['progress_signal'] = athread.signals.progress
            elif a_param == 'stop' and params.get(a_param):
                athread.kwargs['stop_signal'] = athread.signals.stop
            elif a_param == 'error' and params.get(a_param):
                athread.kwargs['error_signal'] = athread.signals.error
            elif a_param == 'finished' and params.get(a_param):
                athread.kwargs['finished_signal'] = athread.signals.finished
            elif a_param == 'result' and params.get(a_param):
                athread.kwargs['result_signal'] = athread.signals.result
            else:
                athread.kwargs[a_param] = params.get(a_param)

        if progress_fn is not None and progress_fn is not False:
            athread.signals.progress.connect(progress_fn)

        if error_fn is not None and error_fn is not False:
            athread.signals.error.connect(error_fn)

        if result_fn is not None and result_fn is not False:
            athread.signals.result.connect(result_fn)

        if stop_fn is not None and stop_fn is not False:
            athread.signals.stop.connect(stop_fn)

        if finished_fn is not None and finished_fn is not False:
            athread.signals.finished.connect(finished_fn)

        self.pjs.threadpool.start(athread)

        if wait_for_thread:
            self.pjs.threadpool.waitForDone()

    def finished_fn(self):
        self.pjs.repaint()

    def stop_fn(self, stop_message: str):
        self.pjs.statusbar.showMessage(stop_message)

    def progress_fn(self, n: int):
        self.pjs.statusbar.showMessage(f" {n}% completed")

    # End of multithreading methods here -------------------------------------------------------------------------------

    def get_coordinate_bounds(self, coordinates: Optional[numpy.ndarray] = None, margin_size: int = 0) -> (int, int, int, int):
        """

        :param coordinates: an array of coordinates OR an integer indicating a polygon index in self.pjs.polylines.
        :param margin_size:
        :return:
        """
        if coordinates.size == 1:
            index = numpy.min(coordinates, axis=0)
            index = numpy.int(index)
            minx, maxx, miny, maxy = None, None, None, None
            for slice_num in range(self.pjs.n_frames):
                if (self.pjs.polylines[slice_num] != []) and (len(self.pjs.polylines[slice_num]) > index):
                    polygon = self.pjs.polylines[slice_num][index]
                    bound = polygon.boundingRect()
                    if (minx is None) or (bound.topLeft().x() < minx):
                        minx = bound.topLeft().x()
                    if (miny is None) or (bound.topLeft().y() < miny):
                        miny = bound.topLeft().y()
                    if (maxy is None) or (bound.bottomRight().y() > maxy):
                        maxy = bound.bottomRight().y()
                    if (maxx is None) or (bound.bottomRight().x() > maxx):
                        maxx = bound.bottomRight().x()

        else:
            # This is here mainly to crop around non-rectangular polylines.
            minx, miny = numpy.min(coordinates, axis=0)
            maxx, maxy = numpy.max(coordinates, axis=0)

        # Make sure you are working with integers to prevent errors when slicing the original image.
        minx, miny, maxx, maxy = numpy.int(minx), numpy.int(miny), numpy.int(maxx), numpy.int(maxy)

        # Adjust for margin
        minx, miny, maxx, maxy = minx - margin_size, miny - margin_size, maxx + margin_size, maxy + margin_size

        # Check if within the image bounds, and set to max/min possible value if not
        if (maxx > self.pjs.width) or (maxy > self.pjs.height) or (min(minx, miny) < 0):
            minx = max(minx, 0)
            miny = max(miny, 0)
        maxx = min(maxx, self.pjs.width)
        maxy = min(maxy, self.pjs.height)

        return minx, miny, maxx, maxy

    def transform_annotations(self, transform: QtGui.QTransform, im_dimensions: Optional[Tuple[int, int]] = None) -> (List, List):
        if im_dimensions is None or im_dimensions is False:
            im_dimensions = (self.pjs.width, self.pjs.height)

        new_fiducials = [[] for _ in range(self.pjs.n_frames)]
        new_polylines = [[] for _ in range(self.pjs.n_frames)]

        # A box around the entire image.
        im_box: QtCore.QRectF = QtCore.QRectF(0, 0, im_dimensions[0], im_dimensions[1])

        for ii in range(self.pjs.n_frames):
            currFids = self.pjs.fiducials[ii]
            currPols = self.pjs.polylines[ii]
            for aFid in currFids:
                fp = QtCore.QPointF(aFid[0], aFid[1])
                nf = transform.map(fp)
                new_fid = [int(nf.x()), int(nf.y())]

                if im_box.contains(new_fid[0], new_fid[1]):
                    new_fiducials[ii].append(new_fid)

            for aPol in currPols:
                np = transform.map(aPol)
                if im_box.contains(np.boundingRect()):
                    new_polylines[ii].append(np)

        return new_fiducials, new_polylines

    def generate_ROI_filename(self, x_range: Tuple[int, int], y_range: Tuple[int, int], z_range: Tuple[int, int], extension: str, relative: bool = False) -> str:
        _, fname = os.path.split(self.pjs.filename)
        fname, _ = os.path.splitext(fname)

        fname += '_X' + str(x_range[0]) + '_' + str(x_range[1] - 1) + '_Y' + str(y_range[0]) + '_' + str(y_range[1] - 1) + '_Z' + str(z_range[0]) + '_' + str(z_range[1] - 1) + extension

        return os.path.join(self.pjs.cwd, fname) if not relative else fname

