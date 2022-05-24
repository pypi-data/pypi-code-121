# Copyright (c) 2021 Grumpy Cat Software S.L.
#
# This Source Code is licensed under the MIT 2.0 license.
# the terms can be found in LICENSE.md at the root of
# this project, or at http://mozilla.org/MPL/2.0/.
import uuid
from shapelets.dsl.widgets import AttributeNames


class FilteringContext:
    """
    Filtering Context: Set Widgets to the same filtering context
        param: input_filters -> widgets which trigger an effect when filter applied
        param: output_widget -> widgets affected by the input_filter
    """

    def __init__(self,
                 name: str = None,
                 collection_id: str = None,
                 input_filter_ids: [str] = None,
                 context_id: str = None):
        self.name = name
        self.collection_id = collection_id
        self.context_id = context_id if context_id else str(uuid.uuid1())
        self.input_filters = input_filter_ids
        self.output_widgets = []

    def to_dict(self):
        filtering_context_dict = {
            AttributeNames.COLLECTION_ID.value: self.collection_id,
            AttributeNames.ID.value: self.context_id,
            AttributeNames.INPUT_FILTERS.value: self.input_filters,
            AttributeNames.NAME.value: self.name,
            AttributeNames.OUTPUT_WIDGET.value: self.output_widgets
        }
        return filtering_context_dict
