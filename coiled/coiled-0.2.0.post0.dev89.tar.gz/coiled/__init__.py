# Get function backing "coiled install" command
from .cli.install import install as _install
from .core import (
    create_api_token,
    create_software_environment,
    delete_software_environment,
    diagnostics,
    get_billing_activity,
    get_notifications,
    get_software_info,
    list_api_tokens,
    list_core_usage,
    list_gpu_types,
    list_instance_types,
    list_local_versions,
    list_performance_reports,
    list_software_environments,
    list_user_information,
    performance_report,
    revoke_all_api_tokens,
    revoke_api_token,
    set_backend_options,
)
from .utils import enable_debug_mode
from .v2 import (
    AWSOptions,
    BackendOptions,
    Cloud,
    Cluster,
    FirewallOptions,
    GCPOptions,
    cluster_logs,
    create_cluster,
    delete_cluster,
    list_clusters,
)

install = _install.callback
del _install

# Get function backing "coiled upload" command
from .cli.upload import upload as _upload

upload = _upload.callback
del _upload

# Get function backing "coiled env inspect" command
from .cli.env import inspect as _inspect

inspect = _inspect.callback
del _inspect

# Register coiled configuration values with Dask's config system
from . import config

del config

# Top-level coiled.config attribute


def __getattr__(name):
    if name == "config":
        import dask

        return dask.config.get("coiled")
    raise AttributeError(f"module '{__name__}' has no attribute '{name}'")


# Use versioneer to handle package versioning
from ._version import get_versions

__version__ = get_versions()["version"]
del get_versions

__all__ = [
    "Cloud",
    "Cluster",
    "cluster_logs",
    "create_cluster",
    "create_software_environment",
    "delete_cluster",
    "delete_software_environment",
    "diagnostics",
    "get_billing_activity",
    "get_notifications",
    "get_software_info",
    "install",
    "list_clusters",
    "list_core_usage",
    "list_gpu_types",
    "list_instance_types",
    "list_local_versions",
    "list_performance_reports",
    "list_software_environments",
    "list_user_information",
    "performance_report",
    "set_backend_options",
    "list_api_tokens",
    "revoke_api_token",
    "revoke_all_api_tokens",
    "create_api_token",
    "AWSOptions",
    "GCPOptions",
    "BackendOptions",
]
