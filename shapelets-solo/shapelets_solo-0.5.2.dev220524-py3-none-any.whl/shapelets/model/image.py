# Copyright (c) 2021 Grumpy Cat Software S.L.
#
# This Source Code is licensed under the MIT 2.0 license.
# the terms can be found in LICENSE.md at the root of
# this project, or at http://mozilla.org/MPL/2.0/.

import base64
from enum import Enum
import io
from os.path import exists as file_exists
from matplotlib.figure import Figure
from pathlib import Path
from typing import Union


class AttributeNames(Enum):
    DATA = "data"


class Image:
    """
    This class is a data holder to represent Shapelets Images.
    """

    def __init__(self,
                 data: Union[bytes, Path, Figure]):
        if isinstance(data, str):
            self.data = data
        elif isinstance(data, Path):
            # Reading image from local PATH
            if data.exists():
                file = open(data, 'rb')
                buffer = file.read()
                image_data = base64.b64encode(buffer).decode('utf-8')
                self.data = image_data
            else:
                raise FileNotFoundError(f"The file {data} does not exist")
        elif isinstance(data, bytes):
            image_data = base64.b64encode(data).decode("utf-8")
            self.data = image_data
        elif isinstance(data, Figure):
            bio = io.BytesIO()
            # TODO: pass information from self._additional to savefig function
            data.savefig(bio, format="png", bbox_inches='tight')
            image_data = base64.b64encode(bio.getvalue()).decode("utf-8")
            self.data = image_data
        else:
            raise AttributeError("Only str paths, bytes and Matplotlib Figures are the supported Image's formats")

    def __hash__(self):
        return hash((str(self.data),
                     ))

    def __eq__(self, other):
        return (isinstance(other, Image) and
                self.data == other.data)

    def __repr__(self):
        ob_repr = f"({AttributeNames.DATA.value}={self.data})"
        return ob_repr

    def to_dict(self):
        data_dict = dict()
        data_dict[AttributeNames.DATA.value] = self.data
        return data_dict

    @staticmethod
    def from_dict(dct):
        data = dct[AttributeNames.DATA.value]
        return Image(data=data)
