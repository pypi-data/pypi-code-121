# Copyright (c) 2021 Grumpy Cat Software S.L.
#
# This Source Code is licensed under the MIT 2.0 license.
# the terms can be found in LICENSE.md at the root of
# this project, or at http://mozilla.org/MPL/2.0/.
from typing import Union, List

from shapelets.dsl import Node
from shapelets.dsl.widgets.contexts import (
    FilteringContext,
    TemporalContext
)
from shapelets.dsl.widgets import Widget, AttributeNames
from shapelets.dsl.widgets.controllers import SequenceSelector
from shapelets.model import Sequence, NDArray, View


class LineChart(Widget):
    def __init__(self,
                 title: Union[str, Node, SequenceSelector] = None,
                 sequence: Union[
                     List[Union[Sequence, SequenceSelector, Node]], Sequence, SequenceSelector, Node] = None,
                 x_axis: Union[List[int], List[float], List[str], NDArray, Node] = None,
                 y_axis: Union[List[int], List[float], NDArray, Node] = None,
                 views: Union[List[View], Node] = None,
                 temporal_context: TemporalContext = None,
                 filtering_context: FilteringContext = None,
                 **additional):
        self.title = title
        self.sequence = sequence
        self.x_axis = x_axis
        self.y_axis = y_axis
        self.views = views
        self.temporal_context = temporal_context
        self.filtering_context = filtering_context
        self._plots = list()
        self._is_type = None

        if self.sequence and (self.y_axis or self.x_axis):
            raise Exception("sequence and axis properties are incompatible")

        if self.filtering_context and (self.y_axis or self.x_axis):
            raise Exception("filtering contexts cannot be used with axis properties")

        if self.y_axis is None and self.sequence is None:
            raise Exception("no data was provided")

        # define TYPE
        widget_type = "LineChart"
        if self.sequence:
            widget_type = f"{self.__class__.__name__}:{AttributeNames.SEQUENCE.value.capitalize()}"
        elif isinstance(y_axis, List):
            widget_type = f"{self.__class__.__name__}"
        elif (self.y_axis is None) and (self.x_axis is None) or (self.y_axis is not None):
            widget_type = f"{self.__class__.__name__}:{AttributeNames.NDARRAY.value}"

        super().__init__(widget_type, "LineChart", **additional)
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

    def plot(self,
             y_axis: Union[List[int], List[float], NDArray, Node] = None,
             x_axis: Union[List[int], List[float], List[str], NDArray, Node] = None,
             sequence: Union[List[Union[Sequence, SequenceSelector, Node]], Sequence, Node] = None,
             label: Union[str, Node] = None,
             lane_index: int = 0):
        plot_dict = dict()

        plot_dict.update({
            AttributeNames.LANE_INDEX.value: lane_index
        })

        # list of sequences and/or nodes
        if isinstance(sequence, List) and all(
                [isinstance(seq, Sequence) or isinstance(seq, Node) or isinstance(seq, SequenceSelector) for seq in
                 sequence]):

            for seq in sequence:
                if isinstance(seq, Sequence):
                    plot_dict_array = dict()
                    plot_dict_array.update({
                        AttributeNames.LANE_INDEX.value: lane_index,
                        AttributeNames.SEQUENCE_ID.value: seq.sequence_id
                    })
                    self._plots.append(plot_dict_array)
                elif isinstance(seq, SequenceSelector):
                    seq_node = dict()
                    seq_node.update({
                        AttributeNames.LANE_INDEX.value: lane_index,
                        AttributeNames.WIDGET_REF.value: seq.widget_id
                    })
                    self._plots.append(seq_node)
                elif isinstance(seq, Node):
                    seq_node = dict()
                    seq_node.update({
                        AttributeNames.LANE_INDEX.value: lane_index,
                        AttributeNames.REF.value: f"{seq.node_id}:{seq.active_output}"
                    })
                    self._plots.append(seq_node)

        if isinstance(sequence, SequenceSelector):
            if self.sequence:
                self._plots.append({AttributeNames.WIDGET_REF.value: sequence.widget_id})
        elif isinstance(self.sequence, Node):
            seq_node = dict()
            seq_node[AttributeNames.REF.value] = f"{self.sequence.node_id}:{self.sequence.active_output}"
            self._plots.append(seq_node)

        # a single sequence
        if isinstance(sequence, Sequence):
            plot_dict.update({
                AttributeNames.SEQUENCE_ID.value: sequence.sequence_id
            })
            self._plots.append(plot_dict)

        # Handle arrays
        if isinstance(y_axis, NDArray):
            plot_dict.update({
                AttributeNames.Y_AXIS.value: y_axis.nd_array_id
            })

        if isinstance(y_axis, Node):
            plot_dict.update({
                AttributeNames.Y_AXIS.value: {
                    AttributeNames.REF.value: f"{y_axis.node_id}:{y_axis.active_output}"
                }
            })

        if isinstance(y_axis, List):
            plot_dict.update({
                AttributeNames.Y_AXIS.value: y_axis
            })

        if isinstance(x_axis, NDArray):
            is_type = ''

            if ('<i' in x_axis.dtype.str) or ('<f' in x_axis.dtype.str):
                is_type = 'number'
            elif '<U' in x_axis.dtype.str:
                is_type = 'string'

            if self._is_type is None:
                self._is_type = is_type

            if self._is_type is not None and self._is_type is not is_type:
                raise Exception("invalid mix of types in x axis")

            plot_dict.update({
                AttributeNames.X_AXIS.value: x_axis.nd_array_id
            })

        if isinstance(x_axis, Node):
            plot_dict.update({
                AttributeNames.X_AXIS.value: {
                    AttributeNames.REF.value: f"{x_axis.node_id}:{x_axis.active_output}"
                }
            })

        if isinstance(x_axis, List):
            if all([isinstance(item, str) for item in x_axis]):
                is_type = 'string'
            elif all([(isinstance(item, float) or isinstance(item, int)) for item in x_axis]):
                is_type = 'number'

            if self._is_type is None:
                self._is_type = is_type

            if self._is_type is not None and self._is_type is not is_type:
                raise Exception("invalid mix of types in x axis")

            plot_dict.update({
                AttributeNames.X_AXIS.value: x_axis
            })

        if label is not None:
            if sequence:
                plot_dict.update({
                    AttributeNames.LABEL.value: sequence
                })
            if isinstance(label, str):
                plot_dict.update({
                    AttributeNames.LABEL.value: label
                })
            if isinstance(label, Node):
                plot_dict.update({
                    AttributeNames.LABEL.value: {
                        AttributeNames.REF.value: f"{label.node_id}:{label.active_output}"
                    }
                })
        if self.sequence is None:
            self._plots.append(plot_dict)

    def to_dict_widget(self):
        line_chart_dict = super().to_dict_widget()
        if self.title is not None:
            if isinstance(self.title, str):
                line_chart_dict[AttributeNames.PROPERTIES.value].update({
                    AttributeNames.TITLE.value: self.title
                })
            if isinstance(self.title, Node):
                line_chart_dict[AttributeNames.PROPERTIES.value].update({
                    AttributeNames.TITLE.value: {
                        AttributeNames.REF.value: f"{self.title.node_id}:{self.title.active_output}"
                    }
                })
            if isinstance(self.title, SequenceSelector):
                line_chart_dict[AttributeNames.PROPERTIES.value].update({
                    AttributeNames.TITLE.value: {
                        AttributeNames.WIDGET_REF.value: self.title.widget_id
                    }
                })
        if self.sequence is not None:
            self.plot(sequence=self.sequence)
        elif self.x_axis is not None and self.y_axis is not None:
            self.plot(x_axis=self.x_axis, y_axis=self.y_axis)
        elif self.y_axis is not None:
            self.plot(y_axis=self.y_axis)



        if self.views:
            if isinstance(self.views, Node):
                line_chart_dict[AttributeNames.PROPERTIES.value].update({
                    AttributeNames.VIEWS.value: {
                        AttributeNames.REF.value: f"{self.views.node_id}:{self.views.active_output}"
                    }
                })
            if isinstance(self.views, List) and all(isinstance(view, View) for view in self.views):
                view_list = [view.to_dict() for view in self.views]
                line_chart_dict[AttributeNames.PROPERTIES.value].update({
                    AttributeNames.VIEWS.value: view_list
                })

        if len(self._plots) > 0:
            line_chart_dict[AttributeNames.PROPERTIES.value].update({
                AttributeNames.PLOTS.value: self._plots
            })
        return line_chart_dict
