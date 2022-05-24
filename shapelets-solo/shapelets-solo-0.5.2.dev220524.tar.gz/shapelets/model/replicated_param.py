# Copyright (c) 2021 Grumpy Cat Software S.L.
#
# This Source Code is licensed under the MIT 2.0 license.
# the terms can be found in LICENSE.md at the root of
# this project, or at http://mozilla.org/MPL/2.0/.

import typing

from shapelets.model.ndarray import NDArray
from shapelets.model.sequence import Sequence

GenericTypeVar = typing.TypeVar('T', int, float, NDArray, Sequence)


class ReplicatedParam(typing.Generic[GenericTypeVar]):
    def __init__(self,
                 values: typing.Optional[typing.List[GenericTypeVar]] = None):
        if not values:
            values = []
        self.values = values

    def add_output(self, value: GenericTypeVar):
        self.values.append(value)
