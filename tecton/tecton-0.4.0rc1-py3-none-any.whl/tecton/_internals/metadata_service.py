from google.protobuf.empty_pb2 import Empty

from tecton._internals.metadata_service_impl.base_stub import BaseStub
from tecton._internals.metadata_service_impl.http_client import PureHTTPStub
from tecton_spark import conf
from tecton_spark.logger import get_logger

_stub_instance: BaseStub = None

logger = get_logger("metadata_service")


def instance() -> BaseStub:
    if not _stub_instance:
        _init_stub_instance()
    return _stub_instance


def close_instance():
    if _stub_instance:
        _stub_instance.close()


def _init_stub_instance():
    global _stub_instance

    if not conf.get_or_none("DISABLE_DIRECT_HTTP"):
        _stub_instance = PureHTTPStub()
        conf._init_metadata_server_config(_stub_instance.GetConfigs(Empty()))
        return

    # Warning: Do NOT move grpc and libraries depending on it to top-level imports.
    # This will break the Tecton SDK.
    #
    # `grpc` and libraries depending on it are supported as fallbacks for cases
    # where DISABLE_DIRECT_HTTP is set. grpcio (the package that provides `grpc`)
    # has been removed from the default set of dependencies for the Tecton SDK, but
    # it's supported for fallback behavior until PureHTTPStub is stable. It is also
    # used in hermetic integration tests for now.
    try:
        import grpc
    except ImportError:
        raise ImportError("Please install grpcio")
    from tecton._internals.metadata_service_impl.grpc import grpc_over_grpc
    from tecton._internals.metadata_service_impl.grpc import grpc_over_http
    from tecton._internals.metadata_service_impl.grpc import grpc_stub

    if conf.get_or_none("USE_DIRECT_GRPC"):
        channel = grpc_over_grpc.channel()
    else:
        channel = grpc_over_http.channel()

    intercept_channel = grpc.intercept_channel(channel, grpc_stub.MetadataServiceInterceptor())
    _stub_instance = grpc_stub.MetadataServiceStub(intercept_channel)
    conf._init_metadata_server_config(_stub_instance.GetConfigs(Empty()))
