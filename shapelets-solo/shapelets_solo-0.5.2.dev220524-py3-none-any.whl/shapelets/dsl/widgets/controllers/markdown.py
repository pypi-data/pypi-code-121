# Copyright (c) 2021 Grumpy Cat Software S.L.
#
# This Source Code is licensed under the MIT 2.0 license.
# the terms can be found in LICENSE.md at the root of
# this project, or at http://mozilla.org/MPL/2.0/.
from typing import Union

from shapelets.dsl import Node
from shapelets.dsl.widgets.controllers.label import Label


class Markdown(Label):

    def __init__(self, text: Union[str, int, float, Node], **additional):
        super().__init__(text, **additional)
