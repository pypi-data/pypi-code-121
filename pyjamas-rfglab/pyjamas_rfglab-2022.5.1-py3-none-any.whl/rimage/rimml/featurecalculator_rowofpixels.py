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
from pyjamas.rimage.rimml.featurecalculator import FeatureCalculator


class FeatureCalculatorROP(FeatureCalculator):

    def __init__(self):
        super().__init__()

    def calculate_features(self, image: numpy.ndarray) -> bool:
        self.image = image  # Does not copy, just assigns.

        # Expand dims is necessary below, as predict methods in skimage require a 2D array.
        self.feature_array = image.reshape(1, numpy.prod(image.shape))

        return True
