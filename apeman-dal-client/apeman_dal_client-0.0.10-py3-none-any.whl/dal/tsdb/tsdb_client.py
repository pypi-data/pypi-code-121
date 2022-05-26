import logging
import os

import grpc

from apeman.dal.tsdb import tsdb_pb2
from apeman.dal.tsdb import tsdb_pb2_grpc

logger = logging.getLogger("apeman.tsdb.client")


class ApemanDalTsdbClient(object):

    def __init__(self):
        apeman_dal_server_addr = os.getenv("apeman_dal_server_addr")
        if apeman_dal_server_addr is None:
            raise RuntimeError('Invalid value of apeman_dal_server_addr')

        logging.info('Connect to APEMAN DAL server %s', apeman_dal_server_addr)
        channel = grpc.insecure_channel(apeman_dal_server_addr)
        self.__stub = tsdb_pb2_grpc.TsdbServiceStub(channel)

    def create_datafeed(self, request=None):
        try:
            self.__stub.createDatafeed(request=request)
        except grpc.RpcError as e:
            logger.error(e)
            logger.error(e.args[0].trailing_metadata)
            raise Exception(e.details(), e.args[0].trailing_metadata)

    def delete_datafeed(self, datafeed=''):
        request = tsdb_pb2.DeleteDatafeedRequest(datafeed=datafeed)
        try:
            self.__stub.deleteDatafeed(request=request)
        except grpc.RpcError as e:
            logger.error(e)
            logger.error(e.args[0].trailing_metadata)
            raise Exception(e.details(), e.args[0].trailing_metadata)

    def get_datafeed(self, datafeed=''):
        request = tsdb_pb2.GetDatafeedRequest(datafeed=datafeed)
        try:
            return self.__stub.getDatafeed(request=request)
        except grpc.RpcError as e:
            logger.error(e)
            logger.error(e.args[0].trailing_metadata)
            raise Exception(e.details(), e.args[0].trailing_metadata)

    def list_datafeed(self, query_filter=''):
        request = tsdb_pb2.ListDatafeedRequest(filter=query_filter)
        try:
            return self.__stub.listDatafeed(request=request)
        except grpc.RpcError as e:
            logger.error(e)
            logger.error(e.args[0].trailing_metadata)
            raise Exception(e.details(), e.args[0].trailing_metadata)

    def put_data(self, datafeed='', data=None):
        request = tsdb_pb2.PutDataRequest(datafeed=datafeed, data=data)
        try:
            self.__stub.putData(request=request)
        except grpc.RpcError as e:
            logger.error(e)
            logger.error(e.args[0].trailing_metadata)
            raise Exception(e.details(), e.args[0].trailing_metadata)

    def get_data(self, request=None):
        try:
            return self.__stub.getData(request=request)
        except grpc.RpcError as e:
            logger.error(e)
            logger.error(e.args[0].trailing_metadata)
            raise Exception(e.details(), e.args[0].trailing_metadata)

    def get_data_as_json(self, request: tsdb_pb2.GetDataRequest = None):
        try:
            return self.__stub.getDataAsJson(request=request)
        except grpc.RpcError as e:
            logger.error(e)
            logger.error(e.args[0].trailing_metadata)
            raise Exception(e.details(), e.args[0].trailing_metadata)
