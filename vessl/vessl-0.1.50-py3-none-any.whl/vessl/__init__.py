import functools
import inspect

import vessl
import vessl.integration.tensorboard
import vessl.internal
from vessl._version import __VERSION__
from vessl.util import logger
from vessl.util.constant import VESSL_LOG_LEVEL

__version__ = __VERSION__

# Execution mode
EXEC_MODE = "SDK"

# Expose functions
init = vessl.internal.init
log = vessl.internal.log
finish = vessl.internal.finish
upload = vessl.internal.upload
progress = vessl.internal.progress
hp = vessl.internal.hyperparameters

# Make API calls using `vessl_api`
vessl_api = vessl.internal.api
configure = vessl_api.configure
configure_access_token = vessl_api.configure_access_token
configure_organization = vessl_api.configure_default_organization
configure_project = vessl_api.configure_default_project

# Backward compatibility
update_access_token = vessl_api.configure_access_token
update_organization = vessl_api.configure_default_organization
update_project = vessl_api.configure_default_project

from vessl.dataset import (
    copy_dataset_volume_file,
    create_dataset,
    delete_dataset_volume_file,
    download_dataset_volume_file,
    list_dataset_volume_files,
    list_datasets,
    read_dataset,
    read_dataset_version,
    upload_dataset_volume_file,
)
from vessl.experiment import (
    create_experiment,
    download_experiment_output_files,
    list_experiment_logs,
    list_experiment_output_files,
    list_experiments,
    read_experiment,
    read_experiment_by_id,
    upload_experiment_output_files,
)
from vessl.kernel_cluster import (
    delete_cluster,
    list_cluster_nodes,
    list_clusters,
    read_cluster,
    rename_cluster,
)
from vessl.kernel_image import list_kernel_images, read_kernel_image
from vessl.kernel_resource_spec import (
    list_kernel_resource_specs,
    read_kernel_resource_spec,
)
from vessl.model import (
    create_model,
    create_model_repository,
    delete_model,
    delete_model_repository,
    delete_model_volume_file,
    download_model_volume_file,
    list_model_repositories,
    list_model_volume_files,
    list_models,
    read_model,
    read_model_repository,
    update_model,
    update_model_repository,
    upload_model_volume_file,
)
from vessl.organization import (
    create_organization,
    list_organizations,
    read_organization,
)
from vessl.project import create_project, list_projects, read_project
from vessl.ssh_key import create_ssh_key, delete_ssh_key, list_ssh_keys
from vessl.sweep import (
    create_sweep,
    get_best_sweep_experiment,
    list_sweep_logs,
    list_sweeps,
    read_sweep,
    terminate_sweep,
)
from vessl.volume import (
    copy_volume_file,
    create_volume_file,
    delete_volume_file,
    list_volume_files,
    read_volume_file,
)
from vessl.workspace import (
    backup_workspace,
    connect_workspace_ssh,
    list_workspaces,
    read_workspace,
    restore_workspace,
    update_vscode_remote_ssh,
)

# Expose others
from vessl.util.image import Image  # isort:skip
from vessl.util.audio import Audio  # isort:skip
from openapi_client.models import OrmSweepObjective as SweepObjective  # isort:skip
from openapi_client.models import OrmParameter as SweepParameter  # isort:skip
from openapi_client.models import OrmRange as SweepParameterRange  # isort:skip


# Suppress all exceptions during SDK mode
def suppress_sdk_exception(f):
    @functools.wraps(f)
    def func(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except Exception as e:
            if EXEC_MODE == "SDK":
                # Temporarily disable all exceptions that occur within the SDK
                # TODO (VSSL-1992): raise appropriate errors
                exc_info = e if VESSL_LOG_LEVEL == "DEBUG" else False
                logger.exception(f"{e.__class__.__name__}: {str(e)}", exc_info=exc_info)
            else:
                raise e

    return func


# SDK functions that the user may interact with
for name, value in inspect.getmembers(
    vessl, predicate=lambda x: inspect.ismethod(x) or inspect.isfunction(x)
):
    vars()[name] = suppress_sdk_exception(value)

# Other classes that the user may interact with
user_classes = [Image, Audio, SweepObjective, SweepParameter, SweepParameterRange]
for user_class in user_classes:
    for name, value in inspect.getmembers(
        user_class, predicate=lambda x: inspect.ismethod(x) or inspect.isfunction(x)
    ):
        setattr(user_class, name, suppress_sdk_exception(value))
