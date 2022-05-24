import logging
import os

import grpc

from apeman.model import ModelInstanceTaskDTO
from apeman.model import ModelInstanceTaskLaunchType
from apeman.model import ModelInstanceTaskStatus
from apeman.model import ModelInstanceTaskType
from apeman.model.openapi import apemanOpenApi_pb2
from apeman.model.openapi import apemanOpenApi_pb2_grpc
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
        self.__stub = apemanOpenApi_pb2_grpc.ApemanModelOpenApiStub(channel)

    def report(self, task_id='', status=TaskStatus.NONE, progress=0.0, message='', token=''):
        logger.debug('report....')
        model_instance_task_status = ModelInstanceTaskStatus.Value(status.value)
        request = apemanOpenApi_pb2.TaskStatusReportRequest(modelInstanceTaskId=task_id,
                                                            status=model_instance_task_status,
                                                            progress=progress,
                                                            token=token,
                                                            message=message)
        try:
            self.__stub.Report(request)
        except grpc.RpcError as e:
            logger.error(e)
            logger.error(e.args[0].trailing_metadata)
            raise Exception(e.details(), e.args[0].trailing_metadata)

    def report_get_status(self, task_id='', status=TaskStatus.NONE, progress=0.0, message='', token=''):
        model_instance_task_status = ModelInstanceTaskStatus.Value(status.value)
        request = apemanOpenApi_pb2.TaskStatusReportRequest(modelInstanceTaskId=task_id,
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
        request = apemanOpenApi_pb2.CancelModelInstanceTaskRequest(model_instance_task_id=task_id,
                                                                   force_delete=force_delete, token=token)
        try:
            return self.__stub.ReportAndGetStatus(request=request)
        except grpc.RpcError as e:
            logger.error(e)
            logger.error(e.args[0].trailing_metadata)
            raise Exception(e.details(), e.args[0].trailing_metadata)

    def get_endpoint(self, model_instance_id=''):
        request = apemanOpenApi_pb2.GetModelEndpointRequest(modelInstanceId=model_instance_id)
        try:
            response = self.__stub.GetModelEndpoint(request)
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
        request = ModelInstanceTaskDTO(modelInstanceId=model_instance_id, taskStatus=None,
                                       tenantId=tenant_id, taskToken=task_token,
                                       taskParameters=task_parameters,
                                       jobContext=job_context,
                                       startTime=start_time, endTime=end_time,
                                       taskLaunchType=task_launch_type,
                                       taskType=model_instance_type)
        try:
            response = self.__stub.CreateModelInstanceTask(request)
        except grpc.RpcError as e:
            logger.error(e)
            logger.error(e.args[0].trailing_metadata)
            raise Exception(e.details(), e.args[0].trailing_metadata)

        return response.modelInstanceTaskId

    def get_instance_task(self, model_instance_task_id: str = None, token: str = None):
        request = apemanOpenApi_pb2.GetModelInstanceTaskRequest(
            modelInstanceTaskId=model_instance_task_id,
            taskToken=token)
        try:
            response = self.__stub.GetModelInstanceTask(request=request)
        except grpc.RpcError as e:
            logger.error(e)
            logger.error(e.args[0].trailing_metadata)
            raise Exception(e.details(), e.args[0].trailing_metadata)

        return response
