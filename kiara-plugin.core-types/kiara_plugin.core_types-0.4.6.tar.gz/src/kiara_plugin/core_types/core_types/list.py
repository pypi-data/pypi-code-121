# -*- coding: utf-8 -*-

from kiara import KiaraModule
from kiara.models.values.value import ValueMap
from kiara.modules import ValueSetSchema


class IncludedInListCheckModule(KiaraModule):
    """Check whether an element is in a list."""

    _module_type_name = "list.contains"

    def create_inputs_schema(
        self,
    ) -> ValueSetSchema:

        inputs = {
            "list": {"type": "list", "doc": "The list."},
            "item": {
                "type": "any",
                "doc": "The element to check for inclusion in the list.",
            },
        }
        return inputs

    def create_outputs_schema(
        self,
    ) -> ValueSetSchema:

        outputs = {
            "is_included": {
                "type": "boolean",
                "doc": "Whether the element is in the list, or not.",
            }
        }
        return outputs

    def process(self, inputs: ValueMap, outputs: ValueMap) -> None:

        item_list = inputs.get_value_data("list")
        item = inputs.get_value_data("item")

        outputs.set_value("is_included", item in item_list)
