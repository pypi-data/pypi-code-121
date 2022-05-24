# Copyright (c) 2021 Grumpy Cat Software S.L.
#
# This Source Code is licensed under the MIT 2.0 license.
# the terms can be found in LICENSE.md at the root of
# this project, or at http://mozilla.org/MPL/2.0/.

import json
import os
import unittest
import unittest.mock as mock

from shapelets.dsl import (
    DataApp
)
from shapelets.dsl.widgets.charts import LineChart
from shapelets.model import Sequence, SequenceDensityEnum, SequenceBaseTypeEnum, MetadataType, Collection


def download_dsl_stub():
    pass


@mock.patch("shapelets.services.functions_service.FunctionsService.download_dsl")
class SampleDataAppTest(unittest.TestCase):
    RESOURCES_DIR = f"{os.path.dirname(os.path.abspath(__file__))}{os.sep}resources{os.sep}"

    def test_sample_data_app(self, download_dsl_mock):
        download_dsl_mock.side_effect = download_dsl_stub
        app = DataApp(name="Data app suma",
                      description="Data app suma",
                      creation_date=123)
        x = app.number(widget_id="widget_id_1",
                       name="number_1",
                       default_value=3,
                       value_type=int)
        w = app.number(widget_id="widget_id_2",
                       name="number_2",
                       default_value=5,
                       value_type=int)
        y = app.number(widget_id="widget_id_3",
                       name="number_3",
                       default_value=7,
                       value_type=int)
        button = app.button(widget_id="widget_id_4",
                            name="button1",
                            text="Click para sumar x + y")
        app.place(w, x, y, button)
        with open(f"{self.RESOURCES_DIR}test_sample_data_app.json") as json_file:
            data = json.load(json_file)
        self.assertEqual(app.to_dict_widget(), data)

    def test_sample_data_app_nested_panels(self, download_dsl_mock):
        download_dsl_mock.side_effect = download_dsl_stub
        app = DataApp(name="Data app suma",
                      description="Data app suma",
                      creation_date=123)
        app.set_title("DataApp Title")
        x = app.number(widget_id="widget_id_1",
                       name="number_1",
                       default_value=3,
                       value_type=int)
        w = app.number(widget_id="widget_id_2",
                       name="number_2",
                       default_value=5,
                       value_type=int)
        y = app.number(widget_id="widget_id_3",
                       name="number_3",
                       default_value=7,
                       value_type=int)
        button = app.button(widget_id="widget_id_4",
                            name="button1",
                            text="Click para sumar x + y")
        input_panel = app.horizontal_flow_panel(title="Operands",
                                                panel_id="horizontal_panel_id_1")
        input_panel.place(w)
        input_panel.place(x)
        input_panel.place(y)
        outputs_panel = app.horizontal_flow_panel(title="Results",
                                                  panel_id="horizontal_panel_id_2")
        outputs_panel.place(button)
        app.place(input_panel, outputs_panel)
        with open(f"{self.RESOURCES_DIR}test_sample_data_app_nested_panels.json") as json_file:
            data = json.load(json_file)
        self.assertEqual(app.to_dict_widget(), data)

    @staticmethod
    def create_sequence(index: int) -> Sequence:
        return Sequence(
            f"sequence_id_{index}", f"sequence_{index}", None, 0, 0, None,
            SequenceDensityEnum.DENSE, SequenceBaseTypeEnum.NUMERICAL)

    def test_temporal_context(self, download_dsl_mock):
        download_dsl_mock.side_effect = download_dsl_stub
        seq1 = SampleDataAppTest.create_sequence(1)
        seq2 = SampleDataAppTest.create_sequence(2)
        seq3 = SampleDataAppTest.create_sequence(3)
        seq4 = SampleDataAppTest.create_sequence(4)
        app = DataApp(name="Data app temporal context",
                      description="Data app temporal context",
                      creation_date=123)
        temporal_context = app.temporal_context(name="My first temporal context", context_id="context_id_1")
        line_chart1 = LineChart(sequence=seq1,
                                title="First Sequence",
                                temporal_context=temporal_context,
                                widget_id="line_chart_1")
        line_chart2 = LineChart(sequence=seq2,
                                temporal_context=temporal_context,
                                widget_id="line_chart_2")
        line_chart3 = LineChart(sequence=seq3,
                                widget_id="line_chart_3")
        line_chart4 = LineChart(sequence=seq4,
                                widget_id="line_chart_4")
        app.temporal_context("Other temporal context", [line_chart3, line_chart4], context_id="context_id_2")
        app.place(line_chart1, line_chart2, line_chart3, line_chart4)
        with open(f'{self.RESOURCES_DIR}test_temporal_context.json') as json_file:
            data = json.load(json_file)
        self.assertEqual(app.to_dict_widget(), data)

    def test_filtering_context(self, download_dsl_mock):
        download_dsl_mock.side_effect = download_dsl_stub
        seq1 = Sequence(
            "sequence_id_1",
            "sequence_1", None, 0, 0, None,
            SequenceDensityEnum.DENSE,
            SequenceBaseTypeEnum.NUMERICAL)
        seq2 = Sequence(
            "sequence_id_2",
            "sequence_2", None, 0, 0, None,
            SequenceDensityEnum.DENSE,
            SequenceBaseTypeEnum.NUMERICAL)
        seq3 = Sequence(
            "sequence_id_3",
            "sequence_3", None, 0, 0, None,
            SequenceDensityEnum.DENSE,
            SequenceBaseTypeEnum.NUMERICAL)
        collection = Collection("manoli")
        app = DataApp(name="Data app filtering context",
                      description="Data app filtering context",
                      creation_date=123)

        metadata_1 = app.metadata_field("METADATA1", MetadataType.STRING, collection, widget_id="metadata_1")
        metadata_2 = app.metadata_field("METADATA2", MetadataType.DOUBLE, collection, widget_id="metadata_2")
        # metadata_filter1 = app.metadata_filter(metadata_1, metadata_2, widget_id="metadata_filter_1")
        filter1 = app.filtering_context(name="Filter context 1",
                                        input_filter=[metadata_1, metadata_2],
                                        context_id="context_1")
        line_chart1 = LineChart(sequence=seq1,
                                title="First Sequence",
                                filtering_context=filter1,
                                widget_id="line_chart_1")

        metadata_3 = app.metadata_field("INDUSTRY", MetadataType.STRING, collection, widget_id="metadata_3")
        metadata_4 = app.metadata_field("DATA_QUALITY_INDEX", MetadataType.DOUBLE, collection, widget_id="metadata_4")
        metadata_5 = app.metadata_field("LAT_LNG_COORDINATES", MetadataType.GEOHASH, collection, widget_id="metadata_5")
        # metadata_filter2 = app.metadata_filter(metadata_3, metadata_4, metadata_5, widget_id="metadata_filter_2")
        filter2 = app.filtering_context(name="Filter context 2",
                                        input_filter=[metadata_3, metadata_4, metadata_5],
                                        context_id="context_2")
        line_chart2 = LineChart(sequence=seq2,
                                filtering_context=filter2,
                                widget_id="line_chart_2")
        line_chart3 = LineChart(sequence=seq3,
                                filtering_context=filter2,
                                widget_id="line_chart_3")
        app.place(line_chart1, line_chart2, line_chart3)
        app.place(metadata_1, metadata_2, metadata_3, metadata_4, metadata_5)
        with open(f'{self.RESOURCES_DIR}test_filtering_context.json') as json_file:
            data = json.load(json_file)
        self.assertEqual(app.to_dict_widget(), data)
