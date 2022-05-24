# Copyright (c) 2021 Grumpy Cat Software S.L.
#
# This Source Code is licensed under the MIT 2.0 license.
# the terms can be found in LICENSE.md at the root of
# this project, or at http://mozilla.org/MPL/2.0/.
from typing import List

from shapelets.dsl import ArgumentType, ArgumentTypeEnum
from shapelets.dsl.widgets import WidgetNode, AttributeNames
from shapelets.model import Collection, Sequence


class SequenceSelector(WidgetNode):
    def __init__(self,
                 collection: Collection = None,
                 sequences: List[Sequence] = None,
                 default_sequence: Sequence = None,
                 name: str = None,
                 title: str = None,
                 **additional):
        super().__init__(self.__class__.__name__,
                         name,
                         ArgumentType(ArgumentTypeEnum.SEQUENCE),
                         default_sequence,
                         **additional)
        self.collection = collection
        self.sequences = sequences
        self.title = title
        self.default_sequence = default_sequence

    def to_dict_widget(self):
        sequence_selector_dict = super().to_dict_widget()
        if self.collection is not None:
            sequence_selector_dict[AttributeNames.PROPERTIES.value].update(
                {AttributeNames.COLLECTION_ID.value: self.collection.collection_id}
            )
        if self.sequences is not None:
            sequences = [seq.sequence_id for seq in self.sequences]
            sequence_selector_dict[AttributeNames.PROPERTIES.value].update({
                f"{AttributeNames.SEQUENCE_ID.value}s": sequences
            })
        if self.title is not None:
            sequence_selector_dict[AttributeNames.PROPERTIES.value].update(
                {AttributeNames.TITLE.value: self.title}
            )
        if self.default_sequence:
            sequence_selector_dict[AttributeNames.PROPERTIES.value].update({
                AttributeNames.DEFAULT.value: self.default_sequence.sequence_id
            })
        return sequence_selector_dict
