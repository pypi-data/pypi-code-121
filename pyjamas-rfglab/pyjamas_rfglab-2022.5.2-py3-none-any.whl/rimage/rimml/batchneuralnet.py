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

from pyjamas.pjsthreads import ThreadSignals
from pyjamas.rimage.rimml.batchml import BatchML
from pyjamas.rimage.rimml.rimneuralnet import rimneuralnet


class BatchNeuralNet(BatchML):
    def __init__(self, n_frames: int, classifier: Optional[rimneuralnet] = None):
        super().__init__(n_frames, classifier)

        self.prob_arrays = [numpy.empty((1, 0)) for i in range(self.n_frames)]
        self.object_arrays = [numpy.empty((1, 0)) for i in range(self.n_frames)]

    def fit(self, stop_signal: Optional[ThreadSignals] = None) -> bool:
        if self.image_classifier is None:
            return False

        if stop_signal is not None:
            stop_signal.emit('Launching classifier training ...')


        self.image_classifier.fit()

        if stop_signal is not None:
            stop_signal.emit('Classifier training completed.')
        return True

    def predict(self, slices: numpy.ndarray, indices: numpy.ndarray, progress_signal: Optional[ThreadSignals] = None) -> bool:
        # Make sure that the slices are in a 1D numpy array.
        indices = numpy.atleast_1d(indices)
        num_slices = len(indices)

        # For every slice ...
        for i, index in enumerate(indices):
            if slices.ndim > 2:
                theimage = slices[index].copy()
            elif slices.ndim == 2 and index == 0:
                theimage = slices.copy()

            self.object_arrays[index], self.prob_arrays[index] = self.image_classifier.predict(theimage)

            if progress_signal is not None:
                progress_signal.emit(int((100 * (i + 1)) / num_slices))

        return True