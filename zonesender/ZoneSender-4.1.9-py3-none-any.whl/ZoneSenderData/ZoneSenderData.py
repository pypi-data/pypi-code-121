# 公共常量 >>>>>>>>>>>>>>>>>>>>>>>>>>>
GRPC_MAX_MESSAGE_LENGTH = 32*1024*1024

# 公共常量 <<<<<<<<<<<<<<<<<<<<<<<<<<

# GRPC 常量 >>>>>>>>>>>>>>>>>>>>>>>>>
CAN_STACK_NODE_IP = '127.0.0.1'
CAN_STACK_NODE_PORT = 6001
CAN_PARSERNODE_NODE_IP = '127.0.0.1'
CAN_PARSERNODE_NODE_PORT = 6005
SOMEIP_STACK_NODE_IP = '127.0.0.1'
SOMEIP_STACK_NODE_PORT = 6002
GRPC_OPTIONS = [
    ('grpc.max_send_message_length', GRPC_MAX_MESSAGE_LENGTH),
    ('grpc.max_receive_message_length', GRPC_MAX_MESSAGE_LENGTH),
]

# GRPC 常量 <<<<<<<<<<<<<<<<<<<<<<<<<<

# MQTT 常量 >>>>>>>>>>>>>>>>>>>>>>>>>
MQTT_BROKER_IP = '127.0.0.1'
MQTT_BROKER_PORT = 8083

# MQTT 常量 <<<<<<<<<<<<<<<<<<<<<<<<<