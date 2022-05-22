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
from typing import Optional, Tuple

from PyQt5 import QtWidgets

from pyjamas.rimage.rimml.rimclassifier import rimclassifier
import pyjamas.rutils as rutils


class ClassifierDialogABC(ABC):
    positive_training_folder: str = ''
    negative_training_folder: str = ''
    hard_negative_training_folder: str = ''
    train_image_size: Tuple[int, int] = (0, 0)
    step_sz: Tuple[int, int] = rimclassifier.DEFAULT_STEP_SZ
    histogram_of_gradients: bool = True

    def __init__(self):
        super().__init__()

        self.positive_training_folder_edit: QtWidgets.QLineEdit = None
        self.negative_training_folder_edit: QtWidgets.QLineEdit = None
        self.hard_negative_training_folder_edit: QtWidgets.QLineEdit = None

    @abstractmethod
    def setupUi(self, NNMLP: QtWidgets.QDialog, parameters: Optional[dict] = None):
        pass

    @abstractmethod
    def retranslateUi(self, NNMLP: QtWidgets.QDialog):
        pass

    @abstractmethod
    def parameters(self) -> dict:
        pass

    def _open_positive_folder_dialog(self) -> bool:
        folder = rutils.RUtils.open_folder_dialog("Positive training folder", ClassifierDialogABC.positive_training_folder)

        if folder == '' or folder is False or self.positive_training_folder_edit is None:
            return False

        self.positive_training_folder_edit.setText(folder)

        return True

    def _open_negative_folder_dialog(self) -> bool:
        folder = rutils.RUtils.open_folder_dialog("Negative training folder", ClassifierDialogABC.negative_training_folder)

        if folder == '' or folder is False or self.negative_training_folder_edit is None:
            return False

        self.negative_training_folder_edit.setText(folder)

        return True

    def _open_hard_folder_dialog(self) -> bool:
        folder = rutils.RUtils.open_folder_dialog("Hard negative training folder", ClassifierDialogABC.hard_negative_training_folder)

        if folder == '' or folder is False or self.hard_negative_training_folder_edit is None:
            return False

        self.hard_negative_training_folder_edit.setText(folder)

        return True

