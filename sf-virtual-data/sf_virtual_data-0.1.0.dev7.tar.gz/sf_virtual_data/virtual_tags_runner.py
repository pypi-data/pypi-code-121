#!/usr/bin/python3
from abc import ABC
from typing import Callable, List, Tuple
import pandas as pd
from sf_virtual_data import utils
from sf_virtual_data.api import vt_pb2, vt_pb2_grpc
from sf_virtual_data.models import VTCommandLineArgsBase
import google.protobuf.json_format as json_format


class VirtualTagsRunner(ABC):
    def __init__(self, metadata_file: str):
        self.metadata = self.get_metadata(metadata_file)

    def validate_res(self, res: pd.DataFrame):
        """
        Verify that result of this virtual trend match the defines outputs
        """
        expected = set([x.name for x in self.metadata.output_data])
        results = set([x for x in res.columns])
        if len(expected) != len(results) or expected != results:
            raise Exception(
                "The calculated results map doesn't match the defined output tags: expected - {0}, received - {1}".format(expected, results))


    def query_solar_focus(self, vtCommandLineArgs: VTCommandLineArgsBase) -> Tuple[pd.DataFrame, vt_pb2.SiteMetadata, List[vt_pb2.FieldObjectMetadata]]:
        query = vt_pb2.InputDataRequestArgs(module_metadata = self.metadata)
        if vtCommandLineArgs.end_utc < vtCommandLineArgs.start_utc:
            raise Exception("Query params error: end time - {0} is smaller than start time - {1}".format(vtCommandLineArgs.end_utc, vtCommandLineArgs.start_utc))
        query.start_time_utc.FromDatetime(vtCommandLineArgs.start_utc)
        query.end_time_utc.FromDatetime(vtCommandLineArgs.end_utc)
        query.field_objects_ids.extend(vtCommandLineArgs.field_objects)
        channel = utils.get_grpc_channel_according_to_args(vtCommandLineArgs)
        client = vt_pb2_grpc.InputDataServiceStub(channel)
        server_res: vt_pb2.DataResponseDto = client.GetData(query, metadata=[('x-api-key', f'{vtCommandLineArgs.api_access_key}')])
        df = utils.convert_to_df(server_res.data)
        return (df, server_res.site_metadata, server_res.field_objects_metadata)



    def execute(self, vtCommandLineArgs: VTCommandLineArgsBase, calc_method: Callable) -> pd.DataFrame:
        """
        This is the executaion call for this VT calculation flow
        """
        (input_data, site_metadata, field_objects_metadata) = self.query_solar_focus(vtCommandLineArgs)
        res = calc_method(start_time_utc = vtCommandLineArgs.start_utc, end_time_utc = vtCommandLineArgs.end_utc,
        data = input_data, site_metadata = site_metadata, field_objects_metadata = field_objects_metadata )
        self.validate_res(res)
        return res


    def get_metadata(self, metadata_file: str) -> vt_pb2.VirtualDataModule:
        with open(metadata_file, 'r', encoding='utf-8') as f:
            message = vt_pb2.VirtualDataModule()
            json_format.Parse(f.read(), message)
            return message

