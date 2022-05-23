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
from skimage.feature import hog

from pyjamas.rimage.rimml.featurecalculator import FeatureCalculator


class FeatureCalculatorSOG(FeatureCalculator):
    DEFAULT_SOG_PARAMETERS: dict = {'orientations': 8,
                                    'pixels_per_cell': [8, 8],
                                    'cells_per_block': (2, 2),
                                    'visualize': False,
                                    'block_norm': 'L2'
                                    }

    def __init__(self, parameters: Optional[dict] = None):
        super().__init__()

        if parameters is None or parameters is False:
            self.calculator_parameters = FeatureCalculatorSOG.DEFAULT_SOG_PARAMETERS
        else:
            self.calculator_parameters = parameters

    def calculate_features(self, image: numpy.ndarray) -> bool:
        self.image = image  # Does not copy, just assigns.

        # Make sure you can use the pixels per cell indicated.
        # You could return False here, or try to fix it ... we opt for the latter.
        image_too_small: bool = False

        while image.shape[-1] < self.calculator_parameters.get('pixels_per_cell')[-1] * 2:
            self.calculator_parameters['pixels_per_cell'][-1] /= 2
            image_too_small = True

        while image.shape[-2] < self.calculator_parameters.get('pixels_per_cell')[-2] * 2:
            self.calculator_parameters['pixels_per_cell'][-2] /= 2
            image_too_small = True

        if image_too_small:
            print(
                f'Images are too small, had to reduce pixels per cell to calculate gradient distribution to {self.calculator_parameters.get("pixels_per_cell")}.')

        # Expand dims is necessary below, as predict methods in skimage require a 2D array.
        self.feature_array = hog(self.image,
                                 orientations=self.calculator_parameters['orientations'],
                                 pixels_per_cell=self.calculator_parameters['pixels_per_cell'],
                                 cells_per_block=self.calculator_parameters['cells_per_block'],
                                 visualize=self.calculator_parameters['visualize'],
                                 block_norm=self.calculator_parameters['block_norm'])

        self.feature_array = self.feature_array.reshape(1, -1)

        return True
