# Copyright (c) 2021 Grumpy Cat Software S.L.
#
# This Source Code is licensed under the MIT 2.0 license.
# the terms can be found in LICENSE.md at the root of
# this project, or at http://mozilla.org/MPL/2.0/.
import uuid
from shapelets.dsl.widgets import AttributeNames


class TemporalContext:
    """
    Temporal Context: Set Widgets to the same temporal context
    """

    def __init__(self,
                 name: str = None,
                 widget_ids: [str] = None,
                 context_id: str = None):
        self.name = name
        self.context_id = context_id if context_id else str(uuid.uuid1())
        self.widgets = widget_ids

    def to_dict(self):
        temporal_context_dict = {
            AttributeNames.ID.value: self.context_id,
            AttributeNames.NAME.value: self.name,
            AttributeNames.WIDGETS.value: self.widgets
        }
        return temporal_context_dict
