"""Transport layer classes for communicating tasks between pods and modellers."""

#: Maximum size of a message: 700MB.
MAXIMUM_GRPC_MESSAGE_SIZE_BYTES = 700 * 1024 * 1024
_MESSAGE_SERVICE_GRPC_OPTIONS = [
    ("grpc.max_message_length", MAXIMUM_GRPC_MESSAGE_SIZE_BYTES),
    ("grpc.max_receive_message_length", MAXIMUM_GRPC_MESSAGE_SIZE_BYTES),
]
