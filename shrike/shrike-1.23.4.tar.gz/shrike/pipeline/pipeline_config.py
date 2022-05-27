# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.

""" Configuration dataclasses for AMLPipelineHelper """
from dataclasses import dataclass, field
from omegaconf import MISSING
from typing import Optional, Any, Dict, List, Union
from shrike.pipeline.module_helper import module_loader_config, module_manifest

# Default config for HDI components
HDI_DEFAULT_CONF = '{"spark.yarn.appMasterEnv.DOTNET_ASSEMBLY_SEARCH_PATHS":"./udfs","spark.yarn.maxAppAttempts":"1","spark.yarn.appMasterEnv.PYSPARK_PYTHON":"/usr/bin/anaconda/envs/py37/bin/python3","spark.yarn.appMasterEnv.PYSPARK_DRIVER_PYTHON":"/usr/bin/anaconda/envs/py37/bin/python3"}'


@dataclass
class pipeline_cli_config:  # pylint: disable=invalid-name
    """
    Pipeline config for command line parameters

    Parameters:
    - `regenerate_outputs` (bool): set to True for forcing the re-computation of outputs, even if code or data did not change (default to False)
    - `continue_on_failure` (bool): set to True for, in the event of a step failure, forcing the not-downstream steps to keep running (default to False)
    - `disable_telemetry` (bool): set to True to disable telemetry (default to False)
    - `verbose` (bool): set to True for verbose logging (default to False)
    - `submit` (bool): set to True for actually submitting the pipeline (default to False)
    - `resume` (bool): set to True for resuming a previous pipeline run (default to False), in which case you'll also need to provide the experiment name (`experiment_name`) and the run Id (`pipeline_run_id`)
    - `canary` (bool): set to True for running a canary test after experiment completion (default to False); the *canary()* method, stubbed in the AMLPipelineHelper class but whose implementation is left to the user, can be used to check for outputs, metrics, etc...
    - `export` (Optional[str]): provide a file name if you want to export the pipeline graph (no name by default, which implies no export)
    - `silent` (bool): set to True for not automatically opening a browser window upon pipeline submission (default to False)
    - `wait` (bool): set to True to wait for the completion of the pipeline execution and show the full logs in the meantime (default to False)
    - `experiment_name` (str): to set the name of the experiment in the Azure ML portal
    - `experiment_description` (Optional[str]): to set the description of the experiment in the Azure ML portal
    - `display_name` (Optional[str]): to set the display name of the experiment in the Azure ML portal
    - `pipeline_run_id` (str): the ID of the pipeline to reuse when resume is set to True
    - `tags` (Optional[Any]): any optional tags to add to the experiment
    - `config_dir` (Optional[str]): the directory where the pipeline configuration is stored
    - `publish` (bool): set to True to publish the pipeline to Azure ML as an endpoint (default to False)
    - `endpoint_name` (Optional[str]): name of the endpoint in which to publish the pipeline
    - `endpoint_description` (Optional[str]): description of the endpoint in which to publish the pipeline
    """

    regenerate_outputs: bool = False
    continue_on_failure: bool = False
    disable_telemetry: bool = False
    verbose: bool = False
    submit: bool = False
    resume: bool = False
    canary: bool = False
    export: Optional[str] = None
    silent: bool = False
    wait: bool = False
    experiment_name: str = MISSING
    experiment_description: Optional[str] = None
    display_name: Optional[str] = None
    pipeline_run_id: str = MISSING
    tags: Optional[Any] = None
    config_dir: Optional[str] = None
    publish: bool = False
    endpoint_name: Optional[str] = None
    endpoint_description: Optional[str] = None


@dataclass
class aml_connection_config:  # pylint: disable=invalid-name
    """
    AML connection configuration

    Parameters:
    - `subscription_id` (str): Azure subscription id
    - `resource_group` (str): Azure resource group
    - `workspace_name` (str): Azure ML workspace name
    - `tenant` (Optional[str]): Azure Active Directory tenant
    - `auth` (str): the authentication method to connect to Azure ("msi", "azurecli", or "interactive" by default).
    - `force` (bool): to force tenant authentication (False by default)
    """

    subscription_id: str = MISSING
    resource_group: str = MISSING
    workspace_name: str = MISSING
    tenant: Optional[str] = None
    auth: str = "interactive"
    force: bool = False


@dataclass
class pipeline_compute_config:  # pylint: disable=invalid-name
    """
    AML workspace compute targets and I/O modes

    Parameters:
    - `default_compute_target (str): name of default compute target to use if not specified
    - `linux_cpu_dc_target` (str): name of linux cpu detonation chamber compute target
    - `linux_cpu_prod_target` (str): name of linux cpu regular compute target
    - `linux_gpu_dc_target` (str): name of linux gpu detonation chamber compute target
    - `linux_gpu_prod_target` (str): name of linux gpu regular compute target
    - `linux_input_mode` (str): input mode for linux compute targets (default to "mount"), more details at https://componentsdk.azurewebsites.net/concepts/inputs-and-outputs.html#input-dataset-mode
    - `linux_output_mode` (str): output mode for linux compute targets (default to "mount"), more details at https://componentsdk.azurewebsites.net/concepts/inputs-and-outputs.html#output-dataset-mode
    - `windows_cpu_prod_target` (str): name of windows cpu regular compute target
    - `windows_cpu_dc_target` (str): name of windows cpu detonation chamber compute target
    - `windows_input_mode` (str): input mode for windows compute targets (default to "download"), more details at https://componentsdk.azurewebsites.net/concepts/inputs-and-outputs.html#input-dataset-mode
    - `windows_output_mode` (str): output mode for windows compute targets (default to "upload"), more details at https://componentsdk.azurewebsites.net/concepts/inputs-and-outputs.html#output-dataset-mode
    - `hdi_prod_target` (str): name of HDI regular compute target
    - `hdi_dc_target` (Optional[str]): name of HDI detonation chamber compute target
    - `hdi_driver_memory` (str): HDI driver memory in GB (default to "4g")
    - `hdi_driver_cores` (int): number of HDI driver cores (default to 2)
    - `hdi_executor_memory` (str): HDI executor memory in GB (default to "3g")
    - `hdi_executor_cores` (int): number of HDI executor cores (default to 2)
    - `hdi_number_executors` (int): number of HDI executors (default to 1)
    - `hdi_conf` (Optional[Any]): additional HDI parameters
    - `parallel_node_count` (int): number of nodes for parallel steps (default to 10)
    - `parallel_process_count_per_node` (Optional[int]): number of processes for each node for parallel steps
    - `parallel_run_invocation_timeout` (int): threshold in seconds for parallel step invocations to timeout (default to 10800)
    - `parallel_run_max_try` (int): maximum number of times to retry parallel step invocations (default to 3)
    - `parallel_mini_batch_size` (int): mini batch size for parallel steps (default to 1)
    - `parallel_error_threshold` (int): error threshold for parallel steps (default to -1)
    - `datatransfer_target` (Optional[str]): name of DataFactory for datatransfer steps
    - `compliant_datastore` (str): name of the default compliant datastore
    - `noncompliant_datastore` (Optional[str]): name of the default non-compliant datastore
    - `dc_datastore` (Optional[str]): name of the default datastore for HDI detonation chamber and downstream steps
    """

    default_compute_target: str = MISSING
    linux_cpu_dc_target: str = MISSING
    linux_cpu_prod_target: str = MISSING
    linux_gpu_dc_target: str = MISSING
    linux_gpu_prod_target: str = MISSING
    linux_input_mode: str = "mount"
    linux_output_mode: str = "mount"

    windows_cpu_prod_target: str = MISSING
    windows_cpu_dc_target: str = MISSING
    windows_input_mode: str = "download"
    windows_output_mode: str = "upload"

    hdi_prod_target: str = MISSING
    hdi_dc_target: Optional[str] = None
    hdi_driver_memory: str = "4g"
    hdi_driver_cores: int = 2
    hdi_executor_memory: str = "3g"
    hdi_executor_cores: int = 2
    hdi_number_executors: int = 10
    hdi_conf: Optional[Any] = MISSING

    parallel_node_count: int = 10
    parallel_process_count_per_node: Optional[int] = MISSING
    parallel_run_invocation_timeout: int = 10800
    parallel_run_max_try: int = 3
    parallel_mini_batch_size: int = 1
    parallel_error_threshold: int = -1

    datatransfer_target: Optional[str] = MISSING

    compliant_datastore: str = MISSING
    noncompliant_datastore: Optional[str] = MISSING
    dc_datastore: Optional[str] = None


@dataclass
class tenant_override_config:
    """
    Tenant override configuration

    Parameters:
    - `allow_override` (bool): set to True to control whether the submission-time override functionality will be executed or not (default to False)
    - `keep_modified_files` (bool): set to True for the modified files (`spec.yaml`, `env.yaml`, etc...) to be saved and renamed as `<filename>_<tenant_id>.<extension>` (default to False)
    - `mapping` (Dict[str, Any]): (nested) dictionary-style definition. If this tenant is being used with `allow_override` = True, then all **local** components will be scanned and the matching fields defined in this `mapping` section will be changed.
      - Keys: `tenant_id` (e.g.: `72f988bf-86f1-41af-91ab-2d7cd011db47`) or "aml configuration" filename in `<config-dir>/aml` (which is also used as in `defaults: aml` in this yaml file).
      - Values: (nested) dictionaries, e.g. `environment.docker.image`. You could define the override for any field in [component schema](https://componentsdk.azurewebsites.net/components.html).
      - For string-type fields such as `environment.docker.image`, the override pattern is "old_value: new_value". For dict-type fields such as `tags`, the pattern is "key: new_value".
      - See https://shrike-docs.com/pipeline/submission-time-override/ for more information
    """

    allow_override: bool = False
    keep_modified_files: bool = False
    mapping: Dict[str, Any] = field(default_factory=lambda: {})


@dataclass
class silo:
    """
    Silo info for federated learning

    Parameters:
    - `compute` (str): the compute target for this silo
    - `datastore` (str): the datastore for this silo
    - `params` (Optional[Dict[str, Any]]): additional parameters relevant to the job that will run in the silo, such as `dataset`, etc...
    - `inherit` (Optional[List[str]]): list of `config_group`s to apply to this silo, and the override priority is per-silo config > `inherit` > `default_config`
    """

    compute: str = MISSING
    datastore: str = MISSING
    params: Optional[Dict[str, Any]] = MISSING
    inherit: Optional[List[str]] = MISSING


@dataclass
class federated_config:
    """
    Federated learning configuration

    Parameters:
    - `silos` (Dict[str, silo]): the various silos to use for federated learning
    - `max_iterations` (int): number of training rounds (default to 1)
    - `params` (Optional[Dict[str, Any]]): additional parameters such as `agg_weight`, `model_name`, etc...
    - `config_group` (Optional[Dict[str, Any]]): config applying to all or some silos; `default_config` will be applied to all silos, and you can also define any customized config
    - `data_transfer_component` (str): name of the data transfer component **registered** in your workspace
    - `deactivate_data_transfer` (bool): set to True to not move the data between central datastore and silo datastore, so that previous results can be reused (default to False)
    """

    silos: Dict[str, silo] = MISSING
    max_iterations: int = 1
    params: Optional[Dict[str, Any]] = MISSING
    config_group: Optional[Dict[str, Any]] = MISSING
    data_transfer_component: str = MISSING
    deactivate_data_transfer: bool = False


def default_config_dict():
    """Constructs the config dictionary for the pipeline helper settings"""
    return {
        "aml": aml_connection_config,
        "run": pipeline_cli_config,
        "compute": pipeline_compute_config,
        "module_loader": module_loader_config,
        "modules": module_manifest,
        "tenant_overrides": tenant_override_config,
        "federated_config": federated_config,
    }
