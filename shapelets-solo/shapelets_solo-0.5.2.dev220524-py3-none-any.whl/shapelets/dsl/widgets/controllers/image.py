# Copyright (c) 2021 Grumpy Cat Software S.L.
#
# This Source Code is licensed under the MIT 2.0 license.
# the terms can be found in LICENSE.md at the root of
# this project, or at http://mozilla.org/MPL/2.0/.
from pathlib import Path
from typing import Union

from matplotlib.figure import Figure

from shapelets.dsl import Node
from shapelets.dsl.widgets import Widget, AttributeNames

from os.path import exists as file_exists

import base64
from io import BytesIO


class Image(Widget):
    def __init__(self,
                 fp: Union[str, bytes, Path, Figure, Node],
                 **additional):
        super().__init__(self.__class__.__name__, "Image", **additional)
        self._fp = fp
        self._additional = additional

    def to_dict_widget(self):
        image_dict = super().to_dict_widget()
        if isinstance(self._fp, str):
            # Reading image from local PATH
            if file_exists(self._fp):
                file = open(self._fp, 'rb')
                buffer = file.read()
                image_data = base64.b64encode(buffer).decode('utf-8')

                image_dict[AttributeNames.PROPERTIES.value].update(
                    {AttributeNames.DATA.value: f"{image_data}"}
                )
            else:
                raise FileNotFoundError(f"The file {self._fp} does not exist")
        elif isinstance(self._fp, Path):
            if self._fp.exists():
                file = open(self._fp, 'rb')
                buffer = file.read()
                image_data = base64.b64encode(buffer).decode('utf-8')

                image_dict[AttributeNames.PROPERTIES.value].update(
                    {AttributeNames.DATA.value: f"{image_data}"}
                )
            else:
                raise FileNotFoundError(f"The file {self._fp} does not exist")
        elif isinstance(self._fp, bytes):
            image_data = base64.b64encode(self._fp).decode("utf-8")

            image_dict[AttributeNames.PROPERTIES.value].update(
                {AttributeNames.DATA.value: f"{image_data}"}
            )
        elif isinstance(self._fp, Figure):
            bio = BytesIO()
            # TODO: pass information from self._additional to savefig function
            self._fp.savefig(bio, format="png", bbox_inches='tight')
            image_data = base64.b64encode(bio.getvalue()).decode("utf-8")

            image_dict[AttributeNames.PROPERTIES.value].update(
                {AttributeNames.DATA.value: f"{image_data}"}
            )
        elif isinstance(self._fp, Node):
            image_dict[AttributeNames.PROPERTIES.value].update({
                AttributeNames.DATA.value: {
                    AttributeNames.REF.value: f"{self._fp.node_id}:{self._fp.active_output}"
                }
            })

        return image_dict
