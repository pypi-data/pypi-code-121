import asyncio
import logging

import grpc
from google.protobuf import empty_pb2

from apeman.model.openapi import apemanOpenApi_pb2
from apeman.model.openapi import apemanOpenApi_pb2_grpc


class ApemanModelServer(apemanOpenApi_pb2_grpc.ApemanModelOpenApiServicer):

    def Report(self, request, context):
        taskId = request.modelInstanceTaskId
        status = request.status
        progress = request.progress
        token = request.token
        message = request.message
        print('taskId: ', taskId)
        print('status: ', status)
        print('progress: ', progress)
        print('token: ', token)
        print('message: ', message)
        return empty_pb2.Empty()

    def GetModelEndpoint(self, request, context):
        taskId = request.modelInstanceId
        print('taskId: ', taskId)

        return apemanOpenApi_pb2.GetModelEndpointResponse(endpoint='http://svc-test.apeman')


async def serve() -> None:
    server = grpc.aio.server()
    apemanOpenApi_pb2_grpc.add_ApemanModelOpenApiServicer_to_server(
        ApemanModelServer(), server)
    server.add_insecure_port('[::]:9090')
    await server.start()
    await server.wait_for_termination()


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    asyncio.get_event_loop().run_until_complete(serve())
