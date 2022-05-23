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

from abc import ABC, abstractmethod

import numpy


class rimml(ABC):
    DEFAULT_SEED: int = 1
    TRAIN_IMAGE_SIZE = (192, 192, 1)  # (rows, cols, channels)

    def __init__(self, parameters: Optional[dict] = None):
        # Classifier: SVC, DecisionTreeClassifier, etc.
        self.classifier = None

    @abstractmethod
    def save(self, filename: str) -> bool:
        pass

    @abstractmethod
    def fit(self) -> bool:
        pass

    @abstractmethod
    def predict(self, image: numpy.ndarray) -> (numpy.ndarray, numpy.ndarray):
        pass