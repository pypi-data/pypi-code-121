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

from typing import Optional, Tuple

import numpy

from pyjamas.rimage.rimml.rimml import rimml


class rimneuralnet(rimml):
    OUTPUT_CLASSES: int = 2
    BATCH_SIZE: int = 1
    EPOCHS: int = 100
    LEARNING_RATE: float = 0.001
    STEP_SIZE: Tuple[int, int] = (rimml.TRAIN_IMAGE_SIZE[0]//8, rimml.TRAIN_IMAGE_SIZE[1]//8)

    def __init__(self, parameters: Optional[dict] = None):
        super().__init__(parameters)

        self.positive_training_folder: str = parameters.get('positive_training_folder')

        # Size of training images (rows, columns).
        self.train_image_size: Tuple[int, int] = parameters.get('train_image_size', rimneuralnet.TRAIN_IMAGE_SIZE)  # (row, col)
        self.step_sz: Tuple[int, int] = parameters.get('step_sz', rimneuralnet.STEP_SIZE)

        self.scaler: int = parameters.get('scaler', 1)  # max pixel value of the training set.

        self.X_train: numpy.ndarray = None
        self.Y_train: numpy.ndarray = None

        self.object_array: numpy.ndarray = None
        self.prob_array: numpy.ndarray = None
