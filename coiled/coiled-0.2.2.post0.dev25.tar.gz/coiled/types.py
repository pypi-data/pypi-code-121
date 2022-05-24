try:
    from typing import Literal
# Python 3.7
except ImportError:
    from typing_extensions import Literal

event_type_list = Literal[
    "add_role_to_profile",
    "attach_gateway_to_router",
    "attach_subnet_to_router",
    "create_vm",
    "create_machine_image",
    "create_scheduler" "create_worker",
    "delete_machine_image",
    "create_fw_rule",
    "create_fw",
    "create_network_cidr",
    "create_subnet",
    "create_network",
    "create_log_sink",
    "create_router",
    "create_iam_role",
    "create_log_bucket",
    "create_storage_bucket",
    "create_instance_profile",
    "check_log_sink_exists",
    "check_or_attach_cloudwatch_policy",
    "delete_vm",
    "delete_route",
    "get_firewall",
    "get_network",
    "get_subnet",
    "get_policy_arn",
    "get_log_group",
    "gcp_instance_create",
    "net_gateways_get_or_create",
    "scale",
]
