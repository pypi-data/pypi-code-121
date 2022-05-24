# Copyright (c) 2021 Grumpy Cat Software S.L.
#
# This Source Code is licensed under the MIT 2.0 license.
# the terms can be found in LICENSE.md at the root of
# this project, or at http://mozilla.org/MPL/2.0/.
from shapelets.dsl import Node
from shapelets.dsl.widgets import Widget, AttributeNames
from shapelets.model import Collection
from shapelets.dsl.widgets.contexts import (
    FilteringContext,
    TemporalContext
)


class SequenceList(Widget):
    def __init__(self,
                 collection: Collection,
                 title: str = None,
                 temporal_context: TemporalContext = None,
                 filtering_context: FilteringContext = None,
                 **additional):
        super().__init__(self.__class__.__name__,
                         **additional)
        self.collection = collection
        self.title = title
        self.temporal_context = temporal_context
        self.filtering_context = filtering_context
        temporal_context_id = None
        if self.temporal_context:
            temporal_context_id = self.temporal_context.context_id
            self.temporal_context.widgets.append(self.widget_id)
        filtering_context_id = None
        if self.filtering_context:
            filtering_context_id = filtering_context.context_id
            filtering_context.output_widgets.append(self.widget_id)
        self.temporal_context = temporal_context_id
        self.filtering_context = filtering_context_id

    def to_dict_widget(self):
        sequences_list_dict = super().to_dict_widget()
        if self.title is not None:
            if isinstance(self.title, str):
                sequences_list_dict[AttributeNames.PROPERTIES.value].update({
                    AttributeNames.TITLE.value: self.title
                })
            if isinstance(self.title, Node):
                sequences_list_dict[AttributeNames.PROPERTIES.value].update({
                    AttributeNames.TITLE.value: {
                        AttributeNames.REF.value: f"{self.title.node_id}:{self.title.active_output}"
                    }
                })
        if self.collection:
            if isinstance(self.collection, Collection):
                sequences_list_dict[AttributeNames.PROPERTIES.value].update({
                    AttributeNames.COLLECTION_ID.value: self.collection.collection_id
                })
            elif isinstance(self.collection, Node):
                sequences_list_dict[AttributeNames.PROPERTIES.value].update({
                    AttributeNames.COLLECTION_ID.value: {
                        AttributeNames.REF.value: f"{self.collection.node_id}:{self.collection.active_output}"
                    },
                })
        return sequences_list_dict
