# Copyright (c) 2021 Grumpy Cat Software S.L.
#
# This Source Code is licensed under the MIT 2.0 license.
# the terms can be found in LICENSE.md at the root of
# this project, or at http://mozilla.org/MPL/2.0/.
from shapelets.dsl.widgets.util import unique_id_str
from shapelets.dsl.widgets.attribute_names import AttributeNames
from shapelets.dsl.node import (
    Node,
    NodeType
)
from shapelets.dsl.argument_types import (
    ArgumentType,
    ArgumentValue,
    SupportedTypes,
)


class Widget:
    """
    Units defined in Layout
    """

    def __init__(self,
                 widget_type: str,
                 widget_name: str = None,
                 widget_id: str = None,
                 draggable: bool = False,
                 resizable: bool = False,
                 # these are the optional properties:
                 placeholder: str = None,
                 disabled: bool = None,
                 parent_data_app: object = None) -> object:
        # parent_data_app is a reference to the DataApp used as a factory
        # for this widget
        self.parent_data_app = parent_data_app
        self.widget_id = widget_id if widget_id else unique_id_str()
        self.widget_name = widget_name if widget_name else self.widget_id
        self.widget_type = widget_type
        self.placeholder = placeholder
        self.disabled = disabled
        self.draggable = draggable
        self.resizable = resizable

    def to_dict_widget(self):
        properties = {}
        if self.placeholder is not None:
            properties[AttributeNames.PLACEHOLDER.value] = self.placeholder
        widget_dict = {
            AttributeNames.ID.value: self.widget_id,
            AttributeNames.NAME.value: self.widget_name,
            AttributeNames.TYPE.value: self.widget_type,
            AttributeNames.DRAGGABLE.value: self.draggable,
            AttributeNames.RESIZABLE.value: self.resizable,
            AttributeNames.DISABLED.value: False if self.disabled is None else self.disabled,
            AttributeNames.PROPERTIES.value: properties
        }
        return widget_dict


class WidgetNode(Widget, Node):
    OPERATION = AttributeNames.OPERATION.value

    def __init__(self,
                 widget_type: str,
                 widget_name: str,
                 value_type: ArgumentType,
                 value: SupportedTypes,
                 **additional):
        Widget.__init__(self, widget_type, widget_name, **additional)
        Node.__init__(self, WidgetNode.OPERATION, node_type=NodeType.WidgetNode)
        self.value_type = value_type
        self.value = ArgumentValue(value_type, value)

    def __hash__(self):
        return hash((Node.__hash__(self), Widget.__hash__(self)))

    def __eq__(self, other):
        return (isinstance(other, WidgetNode) and
                Node.__eq__(self, other) and
                Widget.__eq__(self, other))

    def __repr__(self):
        s_repr = Node.__repr__(self).replace('Node{id:', 'WidgetNode{id:')
        s_repr += f".{AttributeNames.VALUE.value}: {self.value.to_dict()}"
        return s_repr
