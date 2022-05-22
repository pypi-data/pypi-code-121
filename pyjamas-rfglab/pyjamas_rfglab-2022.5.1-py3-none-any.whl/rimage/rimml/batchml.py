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

from abc import ABC, abstractmethod
from typing import Optional

import numpy

from pyjamas.pjsthreads import ThreadSignals
from pyjamas.rimage.rimml import rimml


class BatchML(ABC):
    def __init__(self, n_frames: int, classifier: rimml = None):
        self.n_frames = n_frames

        if classifier is not None:
            self.image_classifier: rimml = classifier
        else:
            self.image_classifier: rimml = None

    @abstractmethod
    def fit(self, stop_signal: Optional[ThreadSignals] = None) -> bool:
        pass

    @abstractmethod
    def predict(self, slices: numpy.ndarray, indices: numpy.ndarray, progress_signal: Optional[ThreadSignals] = None) -> bool:
        pass
