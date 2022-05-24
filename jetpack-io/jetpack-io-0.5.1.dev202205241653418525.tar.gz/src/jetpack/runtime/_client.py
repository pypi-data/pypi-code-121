from __future__ import annotations

import base64
import math
import os
from typing import TYPE_CHECKING, Any, Dict, Final, List, Optional, Tuple, cast
import uuid

from google.protobuf.timestamp_pb2 import Timestamp
import grpc

import jetpack
from jetpack import __version__
from jetpack.config import _instrumentation, _k8s, _namespace, _symbols
from jetpack.proto.runtime.v1alpha1 import remote_pb2, remote_pb2_grpc
from jetpack.runtime._errors import ApplicationError, JetpackError, SystemError
from jetpack.runtime._interceptor import header_adder_interceptor
from jetpack.runtime._local import LocalStub
from jetpack.util import _jetpickle
from jetpack.util.network import _codec

# Instead of having individual clients per functionality (e.g. job), have a
# single client for our runtime.

# TODO(Landau): Move client functionality out of _job.client and centralize it
# here.

# TODO(landau): make this a param
MAX_MESSAGE_LENGTH: Final[int] = 10485760  # 10MB

# Prevent circular dependency
if TYPE_CHECKING:
    from jetpack.core._task import Task


# v3 format: v3::<id>::<secret>::<runtime-host>
# In the future we may also support v3 without runtime host
# (that can be manually specified)
# We no longer support any other version.
def get_runtime_host(key: str) -> str:
    try:
        decoded_api_key = base64.b64decode(key).decode("utf-8")
    except Exception:
        raise SystemError("Could not decode api key")
    parts = decoded_api_key.split("::")
    if len(parts) != 4:
        raise SystemError(
            f"expected key to have 4 parts, but instead got {len(parts)} parts"
        )
    if parts[0] != "v3":
        raise SystemError(f"expected version v3, but got {parts[0]}")
    return parts[3]


class Client:
    def __init__(self) -> None:
        self.stub: Optional[remote_pb2_grpc.RemoteExecutorStub] = None
        pass

    def _address(self) -> str:
        def host() -> str:
            if jetpack.api_key != "":
                host = get_runtime_host(jetpack.api_key)
            else:
                host = os.environ.get("JETPACK_RUNTIME_SERVICE_HOST", "")
            return host.strip()

        def port() -> str:
            default_port = "80" if jetpack.api_key == "" else "443"
            port: str = os.environ.get("JETPACK_RUNTIME_SERVICE_PORT", default_port)
            return port.strip()

        address = f"{host()}:{port()}"
        return address

    def dial(self) -> remote_pb2_grpc.RemoteExecutorStub:
        if "JETPACK_LOCAL_MODE" in os.environ:
            return LocalStub(self)

        if self.stub is None:
            address = self._address()
            if self._has_runtime_credentials():
                sdk_info_interceptor = header_adder_interceptor(
                    "x-jetpack-sdk-version", f"python-{__version__}"
                )
                options = [
                    ("grpc.max_send_message_length", MAX_MESSAGE_LENGTH),
                ]
                interceptors = [
                    sdk_info_interceptor,
                ]
                if jetpack.api_key == "":
                    channel = grpc.aio.insecure_channel(
                        address,
                        options=options,
                        interceptors=interceptors,
                    )
                else:
                    # https://grpc.github.io/grpc/python/grpc.html#create-client-credentials
                    creds = grpc.composite_channel_credentials(
                        grpc.ssl_channel_credentials(),
                        # This gets sent as an authorization bearer header:
                        grpc.access_token_call_credentials(f"{jetpack.api_key}"),
                    )

                    channel = grpc.aio.secure_channel(
                        address,
                        creds,
                        options=options,
                        interceptors=interceptors,
                    )
                self.stub = remote_pb2_grpc.RemoteExecutorStub(channel)
            else:
                raise SystemError("Expect jetpack.api_key to be set")

        return self.stub

    def _has_runtime_credentials(self) -> bool:
        # implicit credentials: is in cluster
        # explicit credentials: api key
        return _k8s.is_in_cluster() or jetpack.api_key != ""

    async def register_app(
        self,
        cron_jobs: List[remote_pb2.CronJob],
    ) -> remote_pb2.RegisterAppResponse:
        request = remote_pb2.RegisterAppRequest(
            namespace=cast(str, _namespace.get()),
            hostname=os.environ["HOSTNAME"],
            cron_jobs=cron_jobs,
            qualified_symbols=_symbols.get_symbol_table().defined_symbols(),
            endpoints=_symbols.get_symbol_table().get_registered_endpoints(),
        )
        stub = self.dial()
        response: remote_pb2.RegisterAppResponse = await stub.RegisterApp(request)
        return response

    async def deregister_app(self) -> remote_pb2.DeregisterAppResponse:
        request = remote_pb2.DeregisterAppRequest(
            namespace=cast(str, _namespace.get()),
            hostname=os.environ["HOSTNAME"],
        )
        stub = self.dial()
        response: remote_pb2.DeregisterAppResponse = await stub.DeregisterApp(request)
        return response

    async def create_task(
        self,
        task: Task,
        args: Optional[Tuple[Any, ...]] = None,
        kwargs: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Creates a Jetpack task. How the task gets executed is up to
        jetpack runtime.

        Keyword arguments:
        task -- task to create
        """

        request = self._build_create_task_request(task, args, kwargs)
        response: remote_pb2.CreateTaskResponse = await self.dial().CreateTask(request)

        task.id = uuid.UUID(response.task_id)
        if task.is_scheduled:
            _instrumentation.get_tracer().scheduled_task_created(task)
        else:
            _instrumentation.get_tracer().task_created(task)

    async def cancel_task(self, task_id: str) -> bool:
        req = remote_pb2.CancelTaskRequest(task_id=task_id)
        resp: remote_pb2.CancelTaskResponse = await self.dial().CancelTask(req)
        return resp.success

    async def post_result(
        self, exec_id: str, value: Any = None, error: Optional[Exception] = None
    ) -> remote_pb2.PostResultResponse:

        if not exec_id:
            # Note: value=None and error=None is acceptable because a job
            # can run successfully and return nothing.
            raise Exception("An exec_id is required to post a result")

        result = remote_pb2.Result()
        if error:
            result.error.code = remote_pb2.APPLICATION
            result.error.message = str(error)

            result.error.encoded_error = _jetpickle.encode(error)
        else:  # order matters, as 'value' can be None
            result.value.encoded_value = _jetpickle.encode(value)

        request = remote_pb2.PostResultRequest(
            exec_id=exec_id,
            result=result,
        )

        response = await self.dial().PostResult(request)
        return cast(remote_pb2.PostResultResponse, response)

    async def wait_for_result(self, task_id: uuid.UUID, symbol_name: str) -> Any:
        request = remote_pb2.WaitForResultRequest(task_id=str(task_id))
        response = await self.dial().WaitForResult(request)
        _instrumentation.get_tracer().result_returned(task_id, response.result)
        return self._transform_response_exception(response, symbol_name)

    async def get_task(self, task_id: str) -> remote_pb2.GetTaskResponse:
        request = remote_pb2.GetTaskRequest(task_id=task_id)
        response: remote_pb2.GetTaskResponse = await self.dial().GetTask(request)
        return response

    @staticmethod
    def _build_create_task_request(
        task: Task,
        args: Optional[Tuple[Any, ...]],
        kwargs: Optional[Dict[str, Any]],
    ) -> remote_pb2.CreateTaskRequest:
        encoded_args = b""
        if args or kwargs:
            encoded_args = _codec.encode_args(
                args if args else None,
                kwargs if kwargs else None,
            ).encode("utf-8")

        if len(encoded_args) > MAX_MESSAGE_LENGTH:
            raise SystemError(
                f"Function argument size is over {math.floor(MAX_MESSAGE_LENGTH / 1000000)}MB"
            )

        current_namespace = _namespace.get()
        task_proto_obj = remote_pb2.Task(
            qualified_symbol=task.jetpack_function.name(),
            encoded_args=encoded_args,
            hostname=os.environ.get("HOSTNAME", ""),  # k8s sets this
            app_name=os.environ.get("JETPACK_LABEL_APP_INSTANCE", ""),
            chart_revision=os.environ.get("JETPACK_LABEL_CHART_REVISION", ""),
            parent_task_id=task.parent_task_id,
            with_checkpointing=task.with_checkpointing,
            target_time=Timestamp(seconds=task.target_time),
        )
        if current_namespace:
            task_proto_obj.namespace = current_namespace

        return remote_pb2.CreateTaskRequest(
            task=task_proto_obj, sdk_version=__version__
        )

    @staticmethod
    def _transform_response_exception(
        response: remote_pb2.WaitForResultResponse,
        symbol_name: str,
    ) -> Any:
        if response.result.HasField("error") and response.result.error.encoded_error:
            err = _jetpickle.decode(response.result.error.encoded_error)
            error_code = response.result.error.code
            jetpack_err = JetpackError(f"chained exception for: {symbol_name}")
            if error_code == remote_pb2.ErrorCode.SYSTEM:
                jetpack_err = SystemError(f"chained exception for: {symbol_name}")
            elif error_code == remote_pb2.ErrorCode.APPLICATION:
                jetpack_err = ApplicationError(f"chained exception for: {symbol_name}")
            raise jetpack_err from err
        elif response.result.HasField("value"):
            val = _jetpickle.decode(response.result.value.encoded_value)
            return val
        else:
            raise SystemError(
                f"Either 'value' or 'error' should be specified in response. Got: {response}"
            )


client = Client()
