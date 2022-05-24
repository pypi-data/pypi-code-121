# Copyright (c) 2021 Grumpy Cat Software S.L.
#
# This Source Code is licensed under the MIT 2.0 license.
# the terms can be found in LICENSE.md at the root of
# this project, or at http://mozilla.org/MPL/2.0/.
from shapelets.dsl.widgets import Widget
from shapelets.model import MetadataType, Collection
from shapelets.dsl.widgets import AttributeNames


class MetadataField(Widget):
    def __init__(self,
                 field_name: str,
                 field_type: MetadataType,
                 collection: Collection,
                 name: str = None,
                 **additional):
        super().__init__(widget_type=self.__class__.__name__,
                         widget_name=name,
                         **additional)
        self.field_type = field_type
        self.collection = collection
        self.field_name = field_name

    def to_dict_widget(self):
        metadata_field_dict = super().to_dict_widget()
        metadata_field_dict[AttributeNames.PROPERTIES.value].update({
            AttributeNames.COLLECTION_ID.value: self.collection.collection_id,
            AttributeNames.NAME.value: self.field_name,
            AttributeNames.TYPE.value: self.frontend_type
        })
        return metadata_field_dict

    @property
    def frontend_type(self):
        value = self.field_type.value
        return value[0] + value[1:].lower()
