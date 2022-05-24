# Copyright (c) 2021 Grumpy Cat Software S.L.
#
# This Source Code is licensed under the MIT 2.0 license.
# the terms can be found in LICENSE.md at the root of
# this project, or at http://mozilla.org/MPL/2.0/.

import json
import time
from enum import Enum
from json import JSONEncoder
from pathlib import Path
from typing import List, overload, Union, Any

from matplotlib.figure import Figure

from shapelets.dsl import ArgumentTypeEnum
from shapelets.dsl.data_app_events import Event
from shapelets.dsl.graph import Node
from shapelets.dsl.widgets import Widget, WidgetNode
from shapelets.dsl.widgets.charts import (
    AltairChart,
    BarChart,
    DonutChart,
    HeatMap,
    Histogram,
    LineChart,
    PieChart,
    PolarArea,
    RadarArea,
    ScatterPlot
)
from shapelets.dsl.widgets.contexts import MetadataField
from shapelets.dsl.widgets.contexts.filtering_context import FilteringContext
from shapelets.dsl.widgets.contexts.temporal_context import TemporalContext
from shapelets.dsl.widgets.controllers import (
    Button,
    Date,
    DateRange,
    Image,
    Label,
    Markdown,
    MultiSequenceSelector,
    Number,
    RadioGroup,
    Selector,
    SequenceSelector,
    SequenceList,
    Slider,
    Table,
    Text,
    Timer
)
from shapelets.dsl.widgets.layouts import VerticalFlowPanel, HorizontalFlowPanel, GridPanel, TabsFlowPanel
from shapelets.dsl.widgets.layouts.panel import Panel
from shapelets.model import Collection, Sequence, MetadataType, NDArray, View, Dataframe


class AttributeNames(Enum):
    CREATION_DATE = "creationDate"
    CUSTOM_GRAPH = "customGraphs"
    DESCRIPTION = "description"
    FILTERING_CONTEXTS = "filteringContexts"
    MAIN_PANEL = "mainPanel"
    NAME = "name"
    ID = "id"
    TEMPORAL_CONTEXTS = "temporalContexts"
    TITLE = "title"
    UPDATE_DATE = "updateDate"


class DataApp:
    """
    Entry point for data app registration.
    """

    @staticmethod
    def now() -> int:
        return int(time.mktime(time.gmtime()) * 1e3)

    def __init__(self,
                 name: str,  # acts as app_id, must be unique
                 description: str,
                 creation_date: int = None,
                 update_date: int = None,
                 main_panel: Panel = None):
        """
        Initializes a dataApp.
        param name: String with the dataApp Name.
        param description: String with the dataApp Description.
        param creation_date: dataApp Creation Date.
        param update_date: dataApp Update Date.
        param main_panel: dataApp Main Panel.
        """
        self.name = name
        self.description = description
        self.creation_date = creation_date
        self.update_date = update_date
        self.main_panel = main_panel if main_panel else VerticalFlowPanel(panel_id=name)
        self.title = name
        self.temporal_contexts = []
        self.filtering_contexts = []
        self._custom_graphs: List[Event] = []

    def set_title(self, title: str):
        """
        Sets the DataApp's title.
        param title: The title for the app.
        """
        self.title = title

    def temporal_context(self,
                         name: str = None,
                         widgets: List[WidgetNode] = None,
                         context_id: str = None):
        """
        Defines a temporal context for your dataApp.
        param name: String with the temporal context name.
        param widgets: List of Widgets inside the temporal context.
        param context_id: String with the temporal context ID.
        return New Temporal Context.
        """
        widget_ids = []
        if widgets:
            for widget in widgets:
                if hasattr(widget, 'temporal_context'):
                    widget_ids.append(widget.widget_id)
                else:
                    raise Exception(f"Component {widget.widget_type} does not allow temporal context")
        temporal_context = TemporalContext(name, widget_ids, context_id)
        self.temporal_contexts.append(temporal_context)
        return temporal_context

    def filtering_context(self,
                          name: str = None,
                          input_filter: List[MetadataField] = None,
                          context_id: str = None):
        """
        Defines a filtering context for your dataApp.
        param name: String with the filtering context name.
        param input_filter: List of Widgets inside the temporal context.
        param context_id: String with the filtering context ID.
        return New Filtering Context.
        """
        input_filters_ids = []
        collection_id = None
        if input_filter:
            collection_ids = [mfield.collection.collection_id for mfield in input_filter]
            collection_ids_set = set(collection_ids)
            if len(set(collection_ids)) == 1:
                collection_id = collection_ids_set.pop()
                for widget in input_filter:
                    # if hasattr(widget, 'filtering_context'):
                    input_filters_ids.append(widget.widget_id)
                    # else:
                    #     raise Exception(f"Component {widget.widget_type} does not allow filtering context")
            else:
                raise Exception("Collection missmatch: All MetadataFields need to come from the same Collection.")
        filtering_context = FilteringContext(name, collection_id, input_filters_ids, context_id)
        self.filtering_contexts.append(filtering_context)
        return filtering_context

    @staticmethod
    def set_filtering_context(input_filter: WidgetNode, output_filter: List[WidgetNode]):
        for widget in output_filter:
            if hasattr(widget, 'filtering_context'):
                widget.filtering_context = input_filter.widget_id
            else:
                raise AttributeError(f"Output widget {widget.widget_type} does not allow filtering context")

    def add_custom_graph(self, event: Event):
        self._custom_graphs.append(event)

    def image(self,
              fp: Union[str, bytes, Path, Figure, Node],
              **additional) -> Image:
        """
        Adds an Image to your dataApp.
        param fp: Image to be included.
        return Image.
        """
        return Image(fp, **additional)

    def number(self,
               from_node: Node = None,
               name: str = None,
               default_value: float = 0,
               value_type: type = float,
               **additional) -> Number:
        """
        A basic widget for getting the user input as a number field.
        param from_node: Allows to create a number from the result of any node.
        param name: String with the number name.
        param default_value: Define number default value (set to 0).
        param value_type: Define number value type.
        return Number.
        """
        number = Number(name=name,
                        default_value=default_value,
                        value_type=value_type,
                        parent_data_app=self,
                        **additional)
        if from_node:
            Event.add_output_mapping(self._custom_graphs, from_node, number.widget_id)
        return number

    def sequence_list(self,
                      title: Union[str, Node] = None,
                      collection: Union[Collection, Node] = None,
                      temporal_context: TemporalContext = None,
                      filtering_context: FilteringContext = None,
                      **additional):
        return SequenceList(
            title,
            collection,
            temporal_context,
            filtering_context,
            **additional)

    def text(self,
             title: Union[str, Node] = None,
             text: Union[str, Node] = None,
             **additional):
        """
        A basic widget for getting the user input as a text field.
        param title: String with the widget title. It will be placed on top of the widget box.
        param text: Text showed inside the widget.
        return Text.
        """
        return Text(title, text, parent_data_app=self, **additional)

    def date(self,
             title: Union[str, Node] = None,
             date: Union[int, Node] = None,
             min_date: Union[int, Node] = None,
             max_date: Union[int, Node] = None,
             **additional):
        """
        Creates a box that allows the user input as date.
        param title: String with the widget title. It will be placed on top of the widget box.
        param date: Preloaded date.
        param min_date: Minimum date allowed.
        param max_date: Maximum date allowed.
        return Date
        """
        return Date(title, date, min_date, max_date, parent_data_app=self, **additional)

    def date_range(self,
                   title: Union[str, Node] = None,
                   start_date: Union[int, Node] = None,
                   end_date: Union[int, Node] = None,
                   min_date: Union[int, Node] = None,
                   max_date: Union[int, Node] = None,
                   time_format: str = None,
                   **additional):
        """
        Creates a box that allows the user input as date range.
        param title: String with the widget title. It will be placed on top of the widget box.
        param start_date: Preloaded start range date.
        param end_date: Preloaded end range date.
        param min_date: Minimum date allowed.
        param max_date: Maximum date allowed.
        param time_format: String with a format for the displayed time, e.g. HH:mm:ss
        return DateRange
        """
        return DateRange(title, start_date,end_date, min_date, max_date, time_format, parent_data_app=self, **additional)

    def slider(self,
               min_value,
               max_value,
               step=None,
               default_value=None,
               in_range: bool = False,
               title: Union[str, Node] = None,
               value_type: type = int,
               formatter: str = "number",
               **additional) -> Slider:
        """
        Creates a slider that lets a user pick a value from a set range by moving a knob.
        param min_value: Minimum value of the slider.
        param max_value: Maximum value of the slider.
        param step: The granularity the slider can step through values. Must greater than 0, and be divided by (max - min)
        param default_value: Initial value of the slider.
        param in_range: Dual thumb mode.
        param title: String with the Slider title. It will be placed on top of the Slider.
        param value_type: Defines slider value type.
        param formatter: str = "number",
        return Slider
        """
        if default_value > max_value or default_value < min_value:
            raise ValueError("Default value should be inside max and min range")
        return Slider(
            min_value,
            max_value,
            step,
            default_value=default_value,
            value_type=value_type,
            in_range=in_range,
            title=title,
            formatter=formatter,
            parent_data_app=self,
            **additional)

    def button(self, name: str = None, text: str = "", **additional) -> Button:
        """
        Creates a button.
        param name: String with the button name.
        param text: String placed inside the button.
        return Button.
        """
        return Button(name, text, parent_data_app=self, **additional)

    def timer(self,
              title: str,
              every: int,
              start_delay: int = None,
              times: int = None,
              hidden: bool = False,
              **additional) -> Timer:
        """
        Creates a Timer for your dataApp.
        param title: String with the Timer title. It will be placed on top of the Timer.
        param every: Defines how often the Timer is executed.
        param start_delay: Defines a start delay for the Timer.
        param times: Defines the amount of cycles the Timer is repeated.
        param hidden: Should the timer be hidden?
        return Timer.
        """
        return Timer(title, every, start_delay, times, hidden, parent_data_app=self, **additional)

    def altair_chart(self, alt: Union[Any, Node], **additional) -> AltairChart:
        """
        Creates an Altair chart: a declarative statistical visualization library for Python (https://altair-viz.github.io/index.html).
        param alt: Loads an Altair Chart.
        return AltairChart
        """
        return AltairChart(alt, **additional)

    def vertical_flow_panel(self,
                            title: str = None,
                            panel_id: str = None,
                            **additional) -> VerticalFlowPanel:
        """
        Defines a Vertical Flow Panel.
        param title: String with the Panel title. It will be placed on top of the Panel.
        param panel_id: Panel ID.
        return VerticalFlowPanel.
        """
        return VerticalFlowPanel(panel_title=title, panel_id=panel_id, **additional)

    def horizontal_flow_panel(self,
                              title: str = None,
                              panel_id: str = None,
                              **additional) -> HorizontalFlowPanel:
        """
        Defines a Horizontal Flow Panel.
        param title: String with the Panel title. It will be placed on top of the Panel.
        param panel_id: Panel ID.
        return HorizontalFlowPanel.
        """
        return HorizontalFlowPanel(panel_title=title, panel_id=panel_id, **additional)

    def grid_panel(self,
                   num_rows: int,
                   num_cols: int,
                   title: str = None,
                   panel_id: str = None,
                   **additional):
        """
        Defines a Grid Panel.
        param num_rows: Number of rows.
        param num_cols: Number of columns.
        param title: String with the Panel title. It will be placed on top of the Panel.
        param panel_id: Panel ID.
        return GridPanel.
        """
        return GridPanel(num_rows, num_cols, panel_title=title, panel_id=panel_id, **additional)

    def tabs_flow_panel(self, title: Union[str, Node] = None, **additional) -> TabsFlowPanel:
        """
        Defines a Tabs Flow Panel.
        param title: String with the Panel title. It will be placed on top of the Panel.
        return TabsFlowPanel.
        """
        return TabsFlowPanel(title, **additional)

    @overload
    def line_chart(self) -> LineChart:
        ...

    @overload
    def line_chart(self,
                   sequence: Union[List[Sequence], Sequence, SequenceSelector, Node],
                   views: Union[List[View], Node] = None,
                   title: Union[str, Node] = None,
                   temporal_context: TemporalContext = None,
                   filtering_context: FilteringContext = None, **additional) -> LineChart:
        """
        Overloads the Line Chart to represent a Sequence.
        param sequence: Sequence to be represented.
        param views: Views to be represented inside the Line Chart.
        param title: String with the Line Chart title. It will be placed on top of the Line Chart.
        param temporal_context: Temporal Context which the Line Chart is attached to.
        param filtering_context: Filtering Context which the Line Chart is attached to.
        return LineChart
        """
        ...

    @overload
    def line_chart(self,
                   y_axis: Union[List[int], List[float], NDArray, Node],
                   x_axis: Union[List[int], List[float], List[str], NDArray, Node] = None,
                   title: Union[str, Node] = None) -> LineChart:
        """
        Overloads the Line Chart to represent X and Y axis.
        param x_axis: X Axis to be represented.
        param y_axis: Y Axis to be represented.
        param title: String with the Line Chart title. It will be placed on top of the Line Chart.
        return LineChart
        """
        ...

    def line_chart(self,
                   title: Union[str, Node, SequenceSelector] = None,
                   sequence: Union[List[Sequence], Sequence, SequenceSelector, Node] = None,
                   x_axis: Union[List[int], List[float], List[str], NDArray, Node] = None,
                   y_axis: Union[List[int], List[float], NDArray, Node] = None,
                   views: Union[List[View], Node] = None,
                   temporal_context: TemporalContext = None,
                   filtering_context: FilteringContext = None, **additional) -> LineChart:
        """
        Creates a Line Chart figure. It represents either a Sequence or X and Y axis.
        param title: String with the Line Chart title. It will be placed on top of the Line Chart.
        param sequence: Sequence to be represented.
        param x_axis: X Axis to be represented.
        param y_axis: Y Axis to be represented.
        param views: Views to be represented inside the Line Chart.
        param temporal_context: Temporal Context which the Line Chart is attached to.
        param filtering_context: Filtering Context which the Line Chart is attached to.
        return LineChart
        """
        return LineChart(
            title,
            sequence,
            x_axis,
            y_axis,
            views,
            temporal_context,
            filtering_context,
            parent_data_app=self,
            **additional)

    def metadata_field(self,
                       field_name: str,
                       field_type: MetadataType,
                       collection: Collection,
                       name: str = None,
                       **additional):
        """
        Creates a Metadata Field
        param field_name: Metadata Name.
        param field_type: Metadata Field.
        param collection: Collection where the Metadata Field belongs.
        param name: Internal Name of the Metadata Field object.
        return MetadataField.
        """
        return MetadataField(field_name, field_type, collection, name, parent_data_app=self, **additional)

    def sequence_selector(self,
                          collection: Collection = None,
                          sequences: List[Sequence] = None,
                          default_sequence: Sequence = None,
                          name: str = None,
                          title: str = None,
                          **additional):
        """
        Creates a Sequence Selector, a drop down menu that allow the selection of any particular sequence.
        param collection: Collection containing the Sequences to be represented in the Sequence Selector.
        param sequences: List of Sequences to be represented in the Sequence Selector.
        param default_sequence: Default Sequence selected in the Sequence Selector.
        param name: Internal name of the Sequence Selector object.
        param title: String with the Sequence Selector title. It will be placed on top of the Sequence Selector.
        return SequenceSelector.
        """
        return SequenceSelector(collection,
                                sequences,
                                default_sequence,
                                name,
                                title,
                                parent_data_app=self,
                                **additional)

    def multi_sequence_selector(self,
                                collection: Collection = None,
                                sequences: List[Sequence] = None,
                                default_sequence: List[Sequence] = None,
                                name: str = None,
                                title: str = None,
                                **additional):
        """
        Creates a Multi Sequence Selector, a drop down menu that allow the selection of multiple sequences.
        param collection: Collection containing the Sequences to be represented in the Sequence Selector.
        param sequences: List of Sequences to be represented in the Sequence Selector.
        param default_sequence: Default Sequence selected in the Sequence Selector.
        param name: Internal name of the Sequence Selector object.
        param title: String with the Sequence Selector title. It will be placed on top of the Sequence Selector.
        return MultiSequenceSelector.
        """
        return MultiSequenceSelector(collection,
                                     sequences,
                                     default_sequence,
                                     name,
                                     title,
                                     parent_data_app=self,
                                     **additional)

    @overload
    def selector(self,
                 options: List[str],
                 title: str = None,
                 value: str = None):
        ...

    @overload
    def selector(self,
                 options: List[int],
                 title: str = None,
                 value: int = None):
        ...

    @overload
    def selector(self,
                 options: List[float],
                 title: str = None,
                 value: float = None):
        ...

    @overload
    def selector(self,
                 options: List[dict],
                 label_by: str,
                 value_by: str,
                 value: any = None,
                 title: str = None):
        ...

    def selector(self,
                 options: List,
                 title: str = None,
                 label_by: str = None,
                 value_by: str = None,
                 value: any = None,
                 **additional):
        """
        Creates a dropdown menu for displaying multiple choices.
        param options: A list of items to be chosen.
        param title: String with the Selector title. It will be placed on top of the Selector.
        param label_by: Selects key to use as label.
        param value_by: Selects key to use as value.
        param value: Default value.
        return Selector
        """
        return Selector(options, title, label_by, value_by, value, parent_data_app=self, **additional)

    def radio_group(self,
                    options: List,
                    title: str = None,
                    label_by: str = None,
                    value_by: str = None,
                    value: any = None,
                    **additional: object) -> object:
        """
        Creates a radio button group for displaying multiple choices and allows to select one value out of a set.
        param options: A list of items to be chosen.
        param title: String with the RadioGroup title. It will be placed on top of the RadioGroup.
        param label_by: Selects key to use as label.
        param value_by: Selects key to use as value.
        param value: Default value.
        return RadioGroup
        """
        return RadioGroup(options, title, label_by, value_by, value, parent_data_app=self, **additional)

    def bar_chart(self,
                  data: Union[List[int], List[float], NDArray, Node],
                  categories: Union[List[str], List[int], List[float], NDArray, Node] = None,
                  name: Union[str, Node] = None,
                  title: Union[str, Node] = None,
                  **additional):
        """
        Produces a Bar Chart figure for your dataApp.
        param data: Data to be included in the Bar Chart.
        param categories: Categories to be included in the Bar Chart.
        param name: Internal name of the Bar Chart object.
        param title: String with the Bar Chart title. It will be placed on top of the Bar Chart.
        return BarChart
        """
        return BarChart(data, categories, name, title, **additional)

    def heatmap(self,
                x_axis: Union[List[int], List[float], List[str], NDArray, Node],
                y_axis: Union[List[int], List[float], List[str], NDArray, Node],
                z_axis: Union[List[int], List[float], NDArray, Node],
                name: Union[str, Node] = None,
                title: Union[str, Node] = None):
        """
        Produces a Heatmap figure for your dataApp.
        param x_axis: X axis to be included in the heatmap.
        param y_axis: Y Axis to be included in the heatmap.
        param z_axis: Z axis to be included in the heatmap. Is represented with color.
        param name: Internal name of the Heatmap object.
        param title: String with the Heatmap title. It will be placed on top of the Heatmap.
        return HeatMap
        """
        return HeatMap(x_axis, y_axis, z_axis, name, title)

    def histogram(self,
                  x: Union[List[int], List[float], NDArray, Node],
                  bins: Union[int, float, Node] = None,
                  cumulative: Union[bool, Node] = False,
                  **additional):
        """
        Produces a Histogram figure for your dataApp.
        param x: Data to be included in the Histogram.
        param bins: Amount of bins for the Histogram.
        param cumulative: Should values be cumulative?
        return Histogram
        """
        return Histogram(x, bins, cumulative, **additional)

    @overload
    def scatter_plot(self,
                     x_axis: Union[List[int], List[float], NDArray, Node],
                     y_axis: Union[List[int], List[float], NDArray, Node] = None,
                     size: Union[List[int], List[float], NDArray, Node] = None,
                     color: Union[List[int], List[float], NDArray, Node] = None,
                     title: Union[str, Node] = None,
                     trend_line: bool = False):
        ...

    @overload
    def scatter_plot(self,
                     x_axis: Union[List[int], List[float], NDArray, Node],
                     y_axis: Union[List[int], List[float], NDArray, Node] = None,
                     size: Union[List[int], List[float], NDArray, Node] = None,
                     categories: Union[List[int], List[float], List[str], NDArray, Node] = None,
                     title: Union[str, Node] = None,
                     trend_line: bool = False):
        ...

    def scatter_plot(self,
                     x_axis: Union[List[int], List[float], NDArray, Node],
                     y_axis: Union[List[int], List[float], NDArray, Node],
                     size: Union[List[int], List[float], NDArray, Node] = None,
                     color: Union[List[int], List[float], NDArray, Node] = None,
                     categories: Union[List[int], List[float], List[str], NDArray, Node] = None,
                     name: str = None,
                     title: Union[str, Node] = None,
                     trend_line: bool = False,
                     **additional):
        """
        Produces a Scatter Plot figure for your dataApp.
        param x_axis: X axis values.
        param y_axis: Y axis values.
        param size: Add size of each point.
        param color: Add color scale for each point.
        param categories: Category of each point.
        param name: Internal name of the Scatter Plot object.
        param title: String with the Scatter Plot title. It will be placed on top of the Scatter Plot.
        param trend_line: Add a trend line to the Scatter Plot.
        return ScatterPlot
        """
        return ScatterPlot(x_axis, y_axis, size, color, categories, name, title, trend_line, **additional)

    def pie_chart(self,
                  data: Union[List[int], List[float], NDArray, Node],
                  categories: Union[List[int], List[float], List[str], NDArray, Node] = None,
                  name: str = None,
                  title: Union[str, Node] = None,
                  **additional):
        """
        Produces a Pie Chart figure for your dataApp.
        param data: Data to be included in the Pie Chart.
        param categories: Categories to be included in the Pie Chart.
        param name: Internal name of the Pie Chart object.
        param title: String with the Pie Chart title. It will be placed on top of the Pie Chart.
        return PieChart
        """
        return PieChart(data, categories, name, title, **additional)

    def donut_chart(self,
                    data: Union[List[int], List[float], NDArray, Node],
                    categories: Union[List[int], List[float], List[str], NDArray, Node] = None,
                    name: str = None,
                    title: Union[str, Node] = None,
                    **additional):
        """
        Produces a Donut Chart figure for your dataApp.
        param data: Data to be included in the Donut Chart.
        param categories: Categories to be included in the Donut Chart.
        param name: Internal name of the Donut Chart object.
        param title: String with the Donut Chart title. It will be placed on top of the Donut Chart.
        return DonutChart
        """
        return DonutChart(data, categories, name, title, **additional)

    def polar_area_chart(self,
                         categories: Union[List[int], List[float], List[str], NDArray, Node],
                         data: Union[List[int], List[float], NDArray, Node],
                         name: str = None,
                         title: Union[str, Node] = None,
                         **additional):
        """
        Produces a Polar Area Chart figure for your dataApp.
        param data: Data to be included in the Polar Area Chart.
        param categories: Categories to be included in the Polar Area Chart.
        param name: Internal name of the Polar Area Chart object.
        param title: String with the Polar Area Chart title. It will be placed on top of the Polar Area Chart.
        return PieChart
        """
        return PolarArea(categories, data, name, title, **additional)

    def radar_area_chart(self,
                         categories: Union[List[int], List[float], List[str], NDArray, Node],
                         data: Union[List[int], List[float], NDArray, Node],
                         groups: Union[List[int], List[float], List[str], NDArray, Node],
                         name: str = None,
                         title: Union[str, Node] = None,
                         **additional):
        """
        Produces a Radar Area Chart figure for your dataApp
        param categories: Categories to be included in the Radar Area Chart.
        param data: Data to be included in the Radar Area Chart.
        param groups: Defines the grouping of the data for the Radar Area Chart.
        param name: Internal name of the Radar Area Chart object.
        param title: String with the Radar Area Chart title. It will be placed on top of the Radar Area Chart.
        return RadarArea.
        """
        return RadarArea(categories, data, groups, name, title, **additional)

    def markdown(self, text: Union[str, int, float, Node], **additional):
        """
        Creates a Markdown block of text. Follows markdown syntax.
        param text: Text to be included.
        return Markdown.
        """
        return Markdown(text, **additional)

    def label(self, text: Union[str, int, float, Node], **additional):
        """
        Creates a Label.
        param text: Label text.
        return Label.
        """
        return Label(text, **additional)

    @overload
    def table(self, data: Union[Dataframe, Node]):
        """
        Creates a table for your dataApp using a Dataframe.
        param data: Data to be included in the Table.
        return Table.
        """
        ...

    @overload
    def table(self, rows: Union[NDArray, Node], cols: Union[NDArray, Node] = None):
        """
        Creates a table for your dataApp using columns and rows.
        param cols: Columns for the table.
        param rows: Rows for the table.
        return Table.
        """
        ...

    def table(self,
              data: Union[Dataframe, Node] = None,
              cols: Union[NDArray, Node] = None,
              rows: Union[NDArray, Node] = None,
              **additional):
        """
        Creates a table for your dataApp.
        param data: Dataframe to be included in the Table.
        param cols: Columns for the table.
        param rows: Rows for the table.
        return Table.
        """
        return Table(data, cols, rows, **additional)

    def place(self, widget: Widget, *args, **kwargs):
        """
        Places a widget into the dataApp.
        param widget: Widget to be included in the dataApp.
        """
        self.main_panel.place(widget, *args, **kwargs)

    def to_dict_widget(self):
        self_dict = {
            AttributeNames.ID.value: self.name,
            AttributeNames.NAME.value: self.name,
            AttributeNames.DESCRIPTION.value: self.description,
            AttributeNames.CREATION_DATE.value: self.creation_date,
            AttributeNames.UPDATE_DATE.value: self.update_date,
            AttributeNames.TEMPORAL_CONTEXTS.value: self.temporal_contexts,
            AttributeNames.FILTERING_CONTEXTS.value: self.filtering_contexts
        }
        if hasattr(self, AttributeNames.TITLE.value):
            self_dict.update({
                AttributeNames.TITLE.value: self.title
            })
        self_dict[AttributeNames.MAIN_PANEL.value] = self.main_panel.to_dict_widget()
        temporal_context = []
        for temporal in self.temporal_contexts:
            temporal_context.append(temporal.to_dict())
        self_dict[AttributeNames.TEMPORAL_CONTEXTS.value] = temporal_context

        filtering_context = []
        for filter_context in self.filtering_contexts:
            filtering_context.append(filter_context.to_dict())
        self_dict[AttributeNames.FILTERING_CONTEXTS.value] = filtering_context

        for event in self._custom_graphs:
            if event.custom_graph_dict:
                custom_graphs = self_dict.get(AttributeNames.CUSTOM_GRAPH.value)
                if not custom_graphs:
                    custom_graphs = {}
                    self_dict[AttributeNames.CUSTOM_GRAPH.value] = custom_graphs
                custom_graphs.update({event.custom_graph_name: event.custom_graph_dict})

        return self_dict

    class DataAppEncoder(JSONEncoder):
        def default(self, o):
            if isinstance(o, (DataApp, Widget)):
                return o.to_dict_widget()
            try:
                return o.__dict__
            except AttributeError as attr_error:
                print(f"ERROR: {attr_error}")
                return {}

    def to_json(self):
        """
        Shows your dataApp specification in JSON format.
        """
        return json.dumps(self, cls=DataApp.DataAppEncoder, indent=2)

    def __repr__(self):
        s_repr = f"{AttributeNames.NAME.value}={self.name}, "
        s_repr += f"{AttributeNames.DESCRIPTION.value}={self.description}, "
        s_repr += f"{AttributeNames.CREATION_DATE.value}={self.creation_date}, "
        s_repr += f"{AttributeNames.UPDATE_DATE.value}={self.update_date}"
        return s_repr
