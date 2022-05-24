import logging
import os

import grpc

from apeman.model import ModelInstanceTaskDTO
from apeman.model import ModelInstanceTaskLaunchType
from apeman.model import ModelInstanceTaskStatus
from apeman.model import ModelInstanceTaskType
from apeman.model.openapi import apeman_open_api_pb2
from apeman.model.openapi import apeman_open_api_pb2_grpc
from apeman.model.openapi.model_instance_task_launch_type import TaskLaunchType
from apeman.model.openapi.model_instance_task_status import TaskStatus
from apeman.model.openapi.model_instance_task_type import TaskType

logger = logging.getLogger('apeman.model.client')


class ApemanModelServiceClient(object):

    def __init__(self):
        apeman_meta_server_addr = os.getenv("apeman_meta_server_addr")
        if apeman_meta_server_addr is None:
            raise RuntimeError('Invalid value of apeman_meta_server_addr')

        logger.debug('Connect to APEMAN meta server %s', apeman_meta_server_addr)
        channel = grpc.insecure_channel(apeman_meta_server_addr)
        self.__stub = apeman_open_api_pb2_grpc.ApemanModelOpenApiStub(channel)

    def report(self, task_id='', status=TaskStatus.NONE, progress=0.0, message='', token=''):
        logger.debug('report....')
        model_instance_task_status = ModelInstanceTaskStatus.Value(status.value)
        request = apeman_open_api_pb2.TaskStatusReportRequest(modelinstance_task_id=task_id,
                                                              status=model_instance_task_status,
                                                              progress=progress,
                                                              token=token,
                                                              message=message)
        try:
            self.__stub.Report(request=request)
        except grpc.RpcError as e:
            logger.error(e)
            logger.error(e.args[0].trailing_metadata)
            raise Exception(e.details(), e.args[0].trailing_metadata)

    def report_and_get_status(self, task_id='', status=TaskStatus.NONE, progress=0.0, message='', token=''):
        model_instance_task_status = ModelInstanceTaskStatus.Value(status.value)
        request = apeman_open_api_pb2.TaskStatusReportRequest(modelinstance_task_id=task_id,
                                                              status=model_instance_task_status,
                                                              progress=progress,
                                                              token=token,
                                                              message=message)
        try:
            return self.__stub.ReportAndGetStatus(request=request)
        except grpc.RpcError as e:
            logger.error(e)
            logger.error(e.args[0].trailing_metadata)
            raise Exception(e.details(), e.args[0].trailing_metadata)

    def cancel_task(self, task_id: str = '', force_delete: bool = None, token: str = None):
        request = apeman_open_api_pb2.CancelModelInstanceTaskRequest(model_instance_task_id=task_id,
                                                                     force_delete=force_delete, token=token)
        try:
            return self.__stub.ReportAndGetStatus(request=request)
        except grpc.RpcError as e:
            logger.error(e)
            logger.error(e.args[0].trailing_metadata)
            raise Exception(e.details(), e.args[0].trailing_metadata)

    def get_endpoint(self, model_instance_id=''):
        request = apeman_open_api_pb2.GetModelEndpointRequest(model_instance_id=model_instance_id)
        try:
            response = self.__stub.GetModelEndpoint(request=request)
        except grpc.RpcError as e:
            logger.error(e)
            logger.error(e.args[0].trailing_metadata)
            raise Exception(e.details(), e.args[0].trailing_metadata)

        return response.endpoint

    def add_model_instance_task(self, model_instance_id: str = None, tenant_id: str = None, task_token: str = None,
                                task_parameters: str = None, job_context: str = None, start_time: int = None,
                                end_time: int = None,
                                launch_type: TaskLaunchType = None,
                                task_type: TaskType = None):
        model_instance_type = ModelInstanceTaskType.Value(task_type.value)
        task_launch_type = ModelInstanceTaskLaunchType.Value(launch_type.value)
        request = ModelInstanceTaskDTO(model_instance_id=model_instance_id, task_status=None,
                                       tenant_id=tenant_id, task_token=task_token,
                                       task_parameters=task_parameters,
                                       job_context=job_context,
                                       start_time=start_time, end_time=end_time,
                                       task_launch_type=task_launch_type,
                                       task_type=model_instance_type)
        try:
            response = self.__stub.CreateModelInstanceTask(request=request)
        except grpc.RpcError as e:
            logger.error(e)
            logger.error(e.args[0].trailing_metadata)
            raise Exception(e.details(), e.args[0].trailing_metadata)

        return response.modelInstanceTaskId

    def get_instance_task(self, model_instance_task_id: str = None, token: str = None):
        request = apeman_open_api_pb2.GetModelInstanceTaskRequest(
            model_instance_task_id=model_instance_task_id,
            task_token=token)
        try:
            return self.__stub.GetModelInstanceTask(request=request)
        except grpc.RpcError as e:
            logger.error(e)
            logger.error(e.args[0].trailing_metadata)
            raise Exception(e.details(), e.args[0].trailing_metadata)

    def batch_get_model_instance_task(self, task_id_list: [str] = None):
        request = apeman_open_api_pb2.BatchGetModelInstanceTaskRequest(task_id=task_id_list)
        try:
            return self.__stub.BatchGetModelInstanceTask(request=request)
        except grpc.RpcError as e:
            logger.error(e)
            logger.error(e.args[0].trailing_metadata)
            raise Exception(e.details(), e.args[0].trailing_metadata)
