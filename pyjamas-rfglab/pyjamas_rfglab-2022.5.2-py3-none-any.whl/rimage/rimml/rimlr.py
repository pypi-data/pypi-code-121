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

from sklearn.linear_model import LogisticRegression

from pyjamas.rimage.rimml.rimclassifier import rimclassifier


class lr(rimclassifier):
    # Missed class penalty: small values (0.05) result in some additional nuclei detected and others
    # not. Large values (100) do not seem to change the result with respect to 1.0.
    DEFAULT_C: float = 1.0

    def __init__(self, parameters: Optional[dict] = None):
        super().__init__(parameters)

        # LR-specific parameters.
        misclass_penalty_C: float = parameters.get('C', lr.DEFAULT_C)
        self.classifier = parameters.get('classifier', LogisticRegression(C=misclass_penalty_C,
                                                                          solver='liblinear',
                                                                          random_state=rimclassifier.DEFAULT_SEED))
