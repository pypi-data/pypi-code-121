#!/usr/bin/python3
import argparse
from datetime import datetime
import os
import numpy as np
import pandas as pd
import sf_virtual_data.models as models
import grpc
import re
from google.protobuf import timestamp_pb2 as google_dot_protobuf_dot_timestamp__pb2
from sf_virtual_data.api import vt_pb2

timedelta_regex = re.compile(r'((?P<hours>\d{2})):((?P<minutes>\d{2})):((?P<seconds>\d{2}))')
MAX_MESSAGE_LENGTH = 100 * 1024 * 1024
TIME_FORMAT = "%Y-%m-%d %H:%M:%S"

class EnvDefault(argparse.Action):
    def __init__(self, envvar, required=True, default=None, **kwargs):
        if not default and envvar:
            if envvar in os.environ:
                default = os.environ[envvar]
        if required and default:
            required = False
        super(EnvDefault, self).__init__(default=default, required=required,
                                         **kwargs)

    def __call__(self, parser, namespace, values, option_string=None):
        setattr(namespace, self.dest, values)


def get_grpc_channel_according_to_args(args: models.VTCommandLineArgsBase) -> grpc.Channel:
    if args.insecure:
        channel = grpc.insecure_channel(args.execution_url, options = [
        ('grpc.max_send_message_length', MAX_MESSAGE_LENGTH),
        ('grpc.max_receive_message_length', MAX_MESSAGE_LENGTH),
        ])
    else:
        credentials = grpc.ssl_channel_credentials()
        channel = grpc.secure_channel(args.execution_url, credentials,  options = [
        ('grpc.max_send_message_length', MAX_MESSAGE_LENGTH),
        ('grpc.max_receive_message_length', MAX_MESSAGE_LENGTH),
        ])
    return channel


def convert_to_df(dto: vt_pb2.DataFrameDto) -> pd.DataFrame:
    res = pd.DataFrame()
    tag_to_series = {}
    for row_data in dto.data:
        for key, data_point in row_data.value.items():
            series = None
            if key in tag_to_series:
                series = tag_to_series[key]
            else:
                series = pd.Series()
                tag_to_series[key] = series
            ### get value
            data_point_value = None
            if data_point.HasField("value"):
                data_point_value = data_point.value
            if data_point.HasField("string_value"):
                data_point_value = data_point.string_value
            if data_point.HasField("time_value"):
                data_point_value = data_point.time_value
            if data_point.HasField("value_per_object"):
                value_per_object_data = []
                objects_ids = []
                for object_id in data_point.value_per_object.data:
                    value_per_object_data.append(data_point.value_per_object.data[object_id].value)
                    objects_ids.append(object_id)
                data_point_value = models.FieldData(data = value_per_object_data,objects_ids = objects_ids, update_time = data_point.value_per_object.timestamp_utc.ToDatetime())
            if data_point.HasField("table"):
                data_point_value = convert_to_df(data_point.table) # not really implemented, user can't define table as an input
            if data_point.HasField("alarm"):
                data_point_value = data_point.alarm # not really implemented, user can't define alarm as an input
            ### get index
            if row_data.HasField("timestamp_utc"):
                series[row_data.timestamp_utc.ToDatetime()] = data_point_value
            if row_data.HasField("string_index"):
                series[row_data.string_index] = data_point_value
            if row_data.HasField("numeric_index"):
                series[row_data.numeric_index] = data_point_value

    for key, series in tag_to_series.items():
        res[key] = series
    return res


def convert_to_dto(df: pd.DataFrame) -> vt_pb2.DataFrameDto:
    res = vt_pb2.DataFrameDto()
    for index, row in df.iterrows():
        row_data = res.data.add()
        index_type = type(index)
        if index_type is str:
            row_data.string_index = index
        if index_type is float or index_type is int :
            row_data.numeric_index = index
        if index_type is google_dot_protobuf_dot_timestamp__pb2.Timestamp:
            row_data.timestamp_utc = index.ToDatetime()
        if index_type is pd.Timestamp:
            timestamp =google_dot_protobuf_dot_timestamp__pb2.Timestamp()
            google_dot_protobuf_dot_timestamp__pb2.Timestamp.FromDatetime(timestamp, dt = index.to_pydatetime())
            row_data.timestamp_utc.CopyFrom(timestamp)
        if index_type is datetime:
            row_data.timestamp_utc = index
        for key, value in row.items():
            data_point = row_data.value[key]
            value_type = type(value)
            if value_type is float:
                data_point.value = value
            if value_type is str:
                data_point.string_value = value
            if value_type is datetime:
                data_point.time_value = value
            if value_type is models.FieldData:
                i = 0
                for val in value:
                    data_point.value_per_object.data[value.get_object_id(i)].value = val
                    i = i + 1
            if value_type is vt_pb2.DataFrameDto:
                data_point.table = value
            if value_type is vt_pb2.Alarm:
                data_point.alarm = value
    return res


def parse_input(cmd_line_args) -> models.VTCommandLineArgsBase:
    parser = argparse.ArgumentParser(
        description='Input parameters to run virtual data module')
    parser.add_argument('--api-access-key',
                        action=EnvDefault,
                        envvar='VT_API_KEY',
                        dest='api_access_key',
                        help='virtual trends api aceess key')
    parser.add_argument('--insecure', action='store_true',
                        dest='insecure',
                        help='do not verfiy https certificate - used for SF execution')
    parser.add_argument('--cert', action='store',
                        dest='cert', default='cert.pem',
                        help='path to root CA relative to entry point file')
    parser.add_argument('--execution-url', dest='execution_url',
                        action='store', default='solarfocus.bseinc.com')
    parser.add_argument('--debug', dest='debug', action='store_true')
    parser.add_argument('--metadata-file', dest='metadata_file',
                        action='store', default='metadata.json')
    parser.add_argument('--output-filename', action='store', required='--debug' not in cmd_line_args and '--metadata' not in cmd_line_args,
                        dest='output_filename',
                        help='Output filename to extract')
    parser.add_argument('--field-objects', action='store', default='',
                        dest='field_objects',
                        help='field objects ids list - can be given by ids seperated by comma (e.g. "1,2,3,4") or by range (e.g. "1-4")')
    parser.add_argument('--start-utc', action='store', required='--metadata' not in cmd_line_args,
                        dest='start',
                        help='Start time of the query in UTC, format YYYY-MM-DD hh:mm:ss')
    parser.add_argument('--end-utc', action='store', required='--metadata' not in cmd_line_args,
                        dest='end',
                        help='End time of the query in UTC, format YYYY-MM-DD hh:mm:ss')
    args = parser.parse_known_args(cmd_line_args)
    known_args = args[0]
    execution_url = known_args.execution_url
    debug = known_args.debug if known_args.debug is not None else False
    insecure = known_args.insecure if known_args.insecure is not None else False
    metadata_file = known_args.metadata_file
    field_objects = list()
    print(known_args.field_objects)
    if known_args.field_objects != "":
        if "-" in known_args.field_objects:
            before, after = known_args.field_objects.split('-')
            field_objects = list(range(int(before), int(after)+1))
        else:
            field_objects = list(map(lambda x: int(x), known_args.field_objects.split(',')))
    start_utc = datetime.strptime(known_args.start, TIME_FORMAT)
    end_utc = datetime.strptime(known_args.end, TIME_FORMAT)
    return models.VTCommandLineArgsBase(metadata_file, execution_url, debug,
                             known_args.output_filename, known_args.api_access_key, insecure, known_args.cert, start_utc, end_utc, field_objects)
