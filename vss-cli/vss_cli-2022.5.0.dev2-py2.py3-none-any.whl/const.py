"""Constants used by VSS CLI (vss-cli)."""
import os

import pkg_resources

PACKAGE_NAME = "vss_cli"

__version__ = "2022.5.0-dev2"


DEFAULT_TIMEOUT = 30
DEFAULT_ENDPOINT = "https://cloud-api.eis.utoronto.ca"
DEFAULT_ENDPOINT_NAME = "cloud-api"
DEFAULT_S3_SERVER = "https://vskey-stor.eis.utoronto.ca"
_LEGACY_CONFIG = ("~", ".vss-cli", "config.json")
_DEFAULT_CONFIG = ("~", ".vss-cli", "config.yaml")
_DEFAULT_HISTORY = ("~", ".vss-cli", "history")

COLUMNS_WIDTH_DEFAULT = -1
COLUMNS_WIDTH_STR = "\u2026"

LEGACY_CONFIG = os.path.expanduser(os.path.join(*_LEGACY_CONFIG))
DEFAULT_CONFIG = os.path.expanduser(os.path.join(*_DEFAULT_CONFIG))
DEFAULT_HISTORY = os.path.expanduser(os.path.join(*_DEFAULT_HISTORY))
DEFAULT_DATA_PATH = pkg_resources.resource_filename(PACKAGE_NAME, "data")
DEFAULT_CONFIG_TMPL = os.path.join(DEFAULT_DATA_PATH, "config.yaml")
DEFAULT_CHECK_UPDATES = True
DEFAULT_CHECK_MESSAGES = True
DEFAULT_TOTP = False

DEFAULT_TABLE_FORMAT = "simple"
DEFAULT_DATA_OUTPUT = "table"
DEFAULT_RAW_OUTPUT = "json"
DEFAULT_OUTPUT = "auto"
DEFAULT_VERBOSE = False
DEFAULT_DEBUG = False
DEFAULT_COLUMNS_WIDTH = -1
DEFAULT_WAIT_FOR_REQUESTS = False

DEFAULT_SETTINGS = {
    "endpoint": DEFAULT_ENDPOINT,
    "output": DEFAULT_OUTPUT,
    "s3_server": DEFAULT_S3_SERVER,
    "table_format": DEFAULT_TABLE_FORMAT,
    "check_for_messages": DEFAULT_CHECK_MESSAGES,
    "check_for_updates": DEFAULT_CHECK_UPDATES,
    "timeout": DEFAULT_TIMEOUT,
    "verbose": DEFAULT_VERBOSE,
    "debug": DEFAULT_DEBUG,
}

DEFAULT_DATETIME_FMT = "%Y-%m-%d %H:%M"
SUPPORTED_DATETIME_FORMATS = ["%Y-%m-%dT%H:%M:%S", "%Y-%m-%d %H:%M"]
GENERAL_SETTINGS = {
    "check_for_messages": bool,
    "check_for_updates": bool,
    "debug": bool,
    "verbose": bool,
    "default_endpoint_name": str,
    "output": str,
    "s3_server": str,
    "table_format": str,
    "timeout": int,
    "columns_width": int,
    "wait_for_requests": bool,
}

DEFAULT_HOST_REGEX = (
    "^[a-z][a-z0-9+\\-.]*://([a-z0-9\\"
    "-._~%!$&'()*+,;=]+@)?([a-z0-9\\-."
    "_~%]+|\\[[a-z0-9\\-._~%!$&'()*+,;"
    "=:]+\\])"
)

DEFAULT_NIC_DEL_MSG = (
    "Network adapter:\t{unit} ({type})\n"
    "Mac address:\t\t{mac_address}\n"
    "Network:\t\t{network[name]} ({network[moref]})\n"
    "Connected:\t\t{connected}\n"
)

DEFAULT_STATE_MSG = (
    "Host Name:\t{hostname} ({os[full_name]})\n"
    "IP Address:\t{ip_addresses}\n"
    "Are you sure you want to change the state from "
    '"{guest_state} to {state}" '
    "of the above VM?"
)

DEFAULT_VM_DEL_MSG = (
    "Moref:\t\t{vm[moref]}\n"
    "UUID:\t\t{vm[uuid]}\n"
    "Name:\t\t{vm[name]}\n"
    "Folder:\t\t{vm[folder][path]}\n"
    "Host Name:\t{vm[hostname]} "
    "({vm[guest_full_name]})\n"
    "IP Address:\t{vm[ip_address]}\n"
    "MAC Address:\t{vm[mac_address]}\n"
    "Create Date:\t{vm[create_date]}\n"
    "Are you sure you want to delete "
    "the above VM?"
)

COLUMNS_TWO_FMT = "{0:<20}: {1:<20}"

COLUMNS_DEFAULT = [("all", "*")]
COLUMNS_MFA_MIN = [("message",), ("type",)]
COLUMNS_VM_MIN = [("moref",), ("name",)]
COLUMNS_VIM_REQUEST = [("vm_moref",), ("vm_name",)]
COLUMNS_MOREF = [("moref",), ("name",)]
COLUMNS_FOLDER_MIN = [*COLUMNS_MOREF, ("path",), ("parent.name",)]
COLUMNS_FOLDER = [*COLUMNS_FOLDER_MIN, ("parent.moref",), ("has_children",)]
COLUMNS_FIRMWARE = [("firmware",)]
COLUMNS_NET_MIN = [
    *COLUMNS_MOREF,
    ("description",),
    ("subnet",),
    ("vlan_id",),
    ("vms",),
]
COLUMNS_NET = [
    *COLUMNS_NET_MIN,
    ("ports",),
    ("admin",),
    ("client",),
    ("updated_on",),
]
COLUMNS_PERMISSION = [("principal",), ("group",), ("propagate",)]
COLUMNS_MIN = [("id",), ("created_on",), ("updated_on",)]
COLUMNS_VSS_SERVICE = [("id",), ("label",), ("name",), ("group.name",)]
COLUMNS_IMAGE = [("id",), ("path",), ("name",)]
COLUMNS_CLIB_ITEMS = [("id",), ("name",), ("library.name",), ('size',)]
COLUMNS_OS = [("id",), ("guest_id",), ("full_name",), ("family",)]
COLUMNS_REQUEST = [*COLUMNS_MIN, ("status",)]
COLUMNS_REQUEST_WAIT = [('warnings', 'warnings[*]'), ('errors', 'errors[*]')]
COLUMNS_REQUEST_MAX = [
    ("errors", "message.errors[*]"),
    ("warnings", "message.warnings[*]"),
    ("task_id", "task_id"),
    ("user.username",),
]
COLUMNS_REQUEST_FILE_SYNC = [
    ("deleted",),
    ("added",),
]
COLUMNS_REQUEST_VMDK_SYNC_MIN = [*COLUMNS_REQUEST, ('run_time',)]
COLUMNS_REQUEST_VMDK_SYNC = [
    *COLUMNS_REQUEST_VMDK_SYNC_MIN,
    *COLUMNS_REQUEST_FILE_SYNC,
    *COLUMNS_REQUEST_MAX,
]
COLUMNS_REQUEST_IMAGE_SYNC_MIN = [*COLUMNS_REQUEST, ("type",)]
COLUMNS_REQUEST_IMAGE_SYNC = [
    *COLUMNS_REQUEST_IMAGE_SYNC_MIN,
    *COLUMNS_REQUEST_FILE_SYNC,
    *COLUMNS_REQUEST_MAX,
]
COLUMNS_REQUEST_SUBMITTED = [
    ("id", "request.id"),
    ("status", "request.status"),
    ("task_id", "request.task_id"),
    ("message",),
]
COLUMNS_REQUEST_MULT_SUBMITTED = [
    ("id", "request.id[*]"),
    ("status", "request.status[*]"),
    ("task_id", "request.task_id[*]"),
    ("message",),
]
COLUMNS_REQUEST_RETIRE = [
    *COLUMNS_REQUEST,
    *COLUMNS_VIM_REQUEST,
    ("retire_on",),
    ("warning",),
    ("warning_on",),
]
COLUMNS_REQUEST_RETIRE_CANCEL = [
    *COLUMNS_REQUEST_RETIRE,
    ("cancelled_on",),
    ("cancelled_by_user.username",),
]
COLUMNS_REQUEST_RETIRE_CONFIRM = [
    *COLUMNS_REQUEST_RETIRE,
    ("confirmed_on",),
    ("confirmed_by_user.username",),
]
COLUMNS_REQUEST_SNAP_MIN = [
    *COLUMNS_REQUEST,
    *COLUMNS_VIM_REQUEST,
    ("action",),
    ("from_date",),
    ("to_date",),
]
COLUMNS_REQUEST_SNAP = [
    *COLUMNS_REQUEST_SNAP_MIN,
    ("description",),
    ("snap_id",),
    ("extensions",),
]
COLUMNS_REQUEST_CHANGE_MIN = [
    *COLUMNS_REQUEST,
    *COLUMNS_VIM_REQUEST,
    ("approved",),
    ("attribute",),
]
COLUMNS_REQUEST_CHANGE_MIN_VM = [
    ("id",),
    ("created_on",),
    ("status",),
    *COLUMNS_VIM_REQUEST,
    ("user.username",),
    ("attribute",),
    ("value[*]",),
]
COLUMNS_REQUEST_CHANGE = [
    *COLUMNS_REQUEST_CHANGE_MIN,
    ("value", "value[*]"),
    ("scheduled_datetime",),
    *COLUMNS_REQUEST_MAX,
]
COLUMNS_REQUEST_EXPORT_MIN = [
    *COLUMNS_REQUEST,
    *COLUMNS_VIM_REQUEST,
    ("transferred",),
]
COLUMNS_REQUEST_EXPORT = [
    *COLUMNS_REQUEST_EXPORT_MIN,
    ("files", "files[*]"),
    *COLUMNS_REQUEST_MAX,
]
COLUMNS_REQUEST_FOLDER_MIN = [*COLUMNS_REQUEST, ("action",), ("moref",)]
COLUMNS_REQUEST_FOLDER = [*COLUMNS_REQUEST_FOLDER_MIN, *COLUMNS_REQUEST_MAX]
COLUMNS_REQUEST_INVENTORY_MIN = [
    *COLUMNS_REQUEST,
    ("name",),
    ("format",),
    ("transfer",),
]
COLUMNS_REQUEST_INVENTORY = [
    *COLUMNS_REQUEST_INVENTORY_MIN,
    ("properties", "properties.data[*]"),
    ("filters",),
    ("transfer",),
    ("transferred",),
    *COLUMNS_REQUEST_MAX,
]
COLUMNS_REQUEST_NEW_MIN = [
    *COLUMNS_REQUEST,
    *COLUMNS_VIM_REQUEST,
    ("approved",),
    ("built_from",),
]
COLUMNS_REQUEST_NEW = [
    *COLUMNS_REQUEST_NEW_MIN,
    ('guest_os',),
    ("domain",),
    ("source",),
    ("retirement",),
    ("folder",),
    ("cpu",),
    ("memory",),
    ("disks", "disks[*]"),
    ("networks", "networks[*]"),
    *COLUMNS_REQUEST_MAX,
]
COLUMNS_TK_MIN = [
    ("id",),
    ("created_on",),
    ("updated_on",),
    ("last_access",),
    ("ip_address",),
    ("valid",),
]
COLUMNS_TK = [*COLUMNS_TK_MIN, ("type",), ("expiration",), ("duration",)]
COLUMNS_MESSAGE_MIN = [*COLUMNS_MIN, ("kind",), ("subject",), ("status",)]
COLUMNS_MESSAGE = [
    *COLUMNS_MIN,
    ("kind",),
    ("status",),
    ("user.username",),
    ("subject",),
    ("text",),
]
COLUMNS_VM_TEMPLATE = [
    *COLUMNS_VM_MIN,
    ("folder.path",),
    ("cpu_count",),
    ("memory_gb",),
]
COLUMNS_VM = [*COLUMNS_VM_TEMPLATE, ("power_state",), ("ip_address",)]
COLUMNS_VM_INFO = [
    ("moref",),
    ("uuid",),
    ("name", "name.full_name"),
    ("folder.path", "folder.path"),
    ("guest_id", "config.os.guest_id"),
    ("version", "hardware.version"),
    ("overall_status", "state.overall_status"),
    ("power_state", "state.power_state"),
    ("alarms", "state.alarms"),
    ("cpu", "hardware.cpu.cpu_count"),
    ("memory_gb", "hardware.memory.memory_gb"),
    ("provisioned_gb", "storage.provisioned_gb"),
    ("snapshot", "snapshot.exist"),
    ("disks", "hardware.devices.disks[*].unit"),
    ("nics", "hardware.devices.nics[*].unit"),
    ("floppies", "hardware.devices.floppies[*].unit"),
]
COLUMNS_VM_GUEST = [
    ("hostname",),
    ("ip_address", "ip_address[*]"),
    ("full_name", "os.full_name"),
    ("guest_id", "os.guest_id"),
    ("running_status", "tools.running_status"),
]
COLUMNS_VM_GUEST_OS = [("guest_full_name",), ("guest_id",), ("guest_family",)]
COLUMNS_VM_GUEST_IP = [
    ("ip_address", "ip_address"),
    ("mac_address", "mac_address"),
    ("origin",),
    ("state",),
]
COLUMNS_VM_OS = [
    ("cfg.full_name",),
    ("cfg.guest_id",),
    ("guest.guest_full_name",),
    ("guest.guest_id",),
    ("guest.guest_family",),
]
COLUMNS_VM_HAGROUP = [*COLUMNS_VM_MIN, ("VALID", "valid")]
COLUMNS_VM_MEMORY = [
    ("memory_gb",),
    ("hot_add.enabled",),
    ("hot_add.limit_gb",),
    ("ballooned_memory_mb", "quick_stats.ballooned_memory_mb"),
    ("guest_memory_usage_mb", "quick_stats.guest_memory_usage_mb"),
]
COLUMNS_VM_NIC_MIN = [
    ("label",),
    ("mac_address",),
    ("type",),
    ("network.name",),
    ("network.moref",),
    ("connected",),
]
COLUMNS_VM_NIC = [*COLUMNS_VM_NIC_MIN, ("start_connected",)]
COLUMNS_OBJ_PERMISSION = [("principal",), ("group",), ("propagate",)]
COLUMNS_VM_SNAP_MIN = [("id",), ("name",)]
COLUMNS_VM_SNAP = [
    *COLUMNS_VM_SNAP_MIN,
    ("power_state",),
    ("quiesced",),
    ("size_gb",),
    ("description",),
    ("create_time",),
    ("age",),
]
COLUMNS_VM_ADMIN = [("name",), ("email",), ("phone",)]
COLUMNS_VM_ALARM_MIN = [*COLUMNS_MOREF, ("overall_status",), ("date_time",)]
COLUMNS_VM_ALARM = [
    *COLUMNS_VM_ALARM_MIN,
    ("acknowledged",),
    ("acknowledged_by_user",),
    ("acknowledged_date_time",),
]
COLUMNS_VM_BOOT = [
    ("enter_bios_setup",),
    ("boot_retry_delay_ms",),
    ("boot_delay_ms",),
]
COLUMNS_VM_CD_MIN = [("label",), ("backing",), ("connected",)]
COLUMNS_VM_CD = [
    *COLUMNS_VM_CD_MIN,
    ("controller.type",),
    ("controller.virtual_device_node",),
]
COLUMNS_VM_CTRL_MIN = [("label",), ("bus_number",), ("type",)]
COLUMNS_VM_CTRL = [
    *COLUMNS_VM_CTRL_MIN,
    ("controller_key",),
    ("summary",),
    ("shared_bus",),
    ("hot_add_remove",),
]
COLUMNS_VM_DISK_MIN = [
    ("label",),
    ("unit",),
    ("controller.label",),
    ("capacity_gib",),
    ("notes",),
]
COLUMNS_VM_DISK = [*COLUMNS_VM_DISK_MIN, ("shares.level",)]

COLUMNS_VM_DISK_BACKING = [
    ("descriptor_file_name",),
    ("device_name",),
    ("disk_mode",),
    ("file_name",),
    ("lun_uuid",),
    ("thin_provisioned",),
]
COLUMNS_VM_DISK_SCSI = [("bus_number",), ("label",), ("type",)]
COLUMNS_VM_CTRL_DISK = [
    ("controller.virtual_device_node",),
    *COLUMNS_VM_DISK_MIN,
    ("capacity_gb",),
]
COLUMNS_VM_CPU = [
    ("cpu",),
    ("cores_per_socket",),
    ("hot_add.enabled",),
    ("hot_remove.enabled",),
    ("overall_cpu_demand_mhz", "quick_stats.overall_cpu_demand_mhz"),
    ("overall_cpu_usage_mhz", "quick_stats.overall_cpu_usage_mhz"),
]
COLUMNS_VM_EVENT = [("user_name",), ("created_time",), ("message",)]
COLUMNS_VM_STATE = [
    ("create_date", "state.create_date"),
    ("power_state", "state.power_state"),
    ("boot_time", "state.boot_time"),
    ("connection_state", "state.connection_state"),
    ("domain_name", "domain.name"),
    ("domain_moref", "domain.moref"),
]
COLUMNS_VM_TOOLS = [("version",), ("version_status",), ("running_status",)]
COLUMNS_VM_HW = [
    ("value",),
    ("status",),
    ("upgrade_policy", "upgrade_policy.upgrade_policy"),
]
COLUMNS_VM_CONSOLIDATION = [("require_disk_consolidation",)]
COLUMNS_VM_CONTROLLERS = [('scsi.count',)]
COLUMNS_EXTRA_CONFIG = [("options", "[*]")]
COLUMNS_VSS_OPTIONS = [("options", "[*]")]
COLUMNS_GROUP = [
    ("name",),
    ("description",),
    ("users_count",),
    ("ldap.last_sync",),
]
COLUMNS_GROUPS = [("id",), ("name",), ("description",), ('users_count',)]
COLUMNS_GROUP_MEMBERS = [
    ("username",),
    ("first_name",),
    ("last_name",),
    ("email",),
]
COLUMNS_ROLE = [
    ("name",),
    ("description",),
    ("entitlements", "entitlements[*]"),
]
COLUMNS_USER_PERSONAL = [
    ("username",),
    ("full_name",),
    ("email",),
    ("phone",),
    ("auth_timestamp",),
    ("pwd_change_time",),
    ("pwd_account_locked_time",),
]
COLUMNS_USER_STATUS = [
    ("created_on",),
    ("updated_on",),
    ("last_access",),
    ("ip_address",),
]
COLUMNS_USER_MFA = [
    ("enabled",),
    ("method",),
    ("enabled_on",),
    ("disabled_on",),
]
COLUMNS_MESSAGE_DIGEST = [("message",)]
COLUMNS_NOT_REQUEST = [
    ("all",),
    ("none",),
    ("completion",),
    ("error",),
    ("submission",),
]
COLUMNS_STOR = [("files", "[*]")]
COLUMNS_STOR_INFO = [
    ("name",),
    ("bucket_name",),
    ("last_modified",),
    ("size",),
]
COLUMNS_STOR_SHARE = [('url',)]
COLUMNS_SSH_KEY_MIN = [*COLUMNS_MIN, ("type",), ("comment",)]
COLUMNS_SSH_KEY = [*COLUMNS_SSH_KEY_MIN, ("fingerprint",), ("value",)]
COLUMNS_VMRC = [("enabled",), ("options",)]
