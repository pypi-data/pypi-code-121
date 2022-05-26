try:
    import grpc
except ImportError:
    raise ImportError("Please install grpcio")

from tecton._internals.metadata_service_impl.grpc import grpc_stub
from tecton_spark.logger import get_logger


logger = get_logger("grpc_over_grpc")


def channel():
    channel_options = [
        ("grpc.max_message_length", 64 * 1024 * 1024),
        ("grpc.max_receive_message_length", 64 * 1024 * 1024),
    ]
    return grpc.insecure_channel(grpc_stub._get_host_port(), options=channel_options)
