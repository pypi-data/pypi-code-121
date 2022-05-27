"""Utility functions for running modellers from configs."""
from __future__ import annotations

import asyncio
import logging
from os import PathLike
from pathlib import Path
from typing import (
    TYPE_CHECKING,
    Any,
    Iterable,
    List,
    Optional,
    Tuple,
    Type,
    Union,
    cast,
)

import desert
import yaml

from bitfount.data.datastructure import DataStructure
from bitfount.federated.authorisation_checkers import IdentityVerificationMethod
from bitfount.federated.exceptions import AggregatorError
from bitfount.federated.helper import (
    _check_and_update_pod_ids,
    _create_aggregator,
    _create_message_service,
)
from bitfount.federated.model_reference import BitfountModelReference
from bitfount.federated.modeller import _Modeller
from bitfount.federated.privacy.differential import _DifferentiallyPrivate
from bitfount.federated.transport.config import MessageServiceConfig
from bitfount.federated.types import AlgorithmType, ProtocolType
from bitfount.federated.utils import _ALGORITHMS, _MODEL_STRUCTURES, _MODELS, _PROTOCOLS
from bitfount.hub.helper import _create_bitfounthub, get_pod_schema
from bitfount.models.base_models import _BaseModel
from bitfount.runners.config_schemas import (
    DataStructureConfig,
    ModellerConfig,
    TaskConfig,
)
from bitfount.types import DistributedModelProtocol

if TYPE_CHECKING:
    from bitfount.hub.api import BitfountHub

DEFAULT_MODEL_OUT = Path("output-model.pt")

logger = logging.getLogger(__name__)


def setup_modeller_from_config_file(
    path_to_config_yaml: Union[str, PathLike],
) -> Tuple[_Modeller, List[str]]:
    """Creates a modeller from a YAML config file.

    Args:
        path_to_config_yaml: the path to the config file

    Returns:
        A tuple of the created Modeller and the list of pod identifiers to run
    """
    with open(path_to_config_yaml) as f:
        config_yaml = yaml.safe_load(f)
    config = desert.schema(ModellerConfig).load(config_yaml)
    return setup_modeller_from_config(config)


def setup_modeller_from_config(
    config: ModellerConfig,
) -> Tuple[_Modeller, List[str]]:
    """Creates a modeller from a loaded config mapping.

    Args:
        config: The modeller configuration.

    Returns:
        A tuple of the created Modeller and the list of pod identifiers to run
        the task against.
    """
    # Load config details
    transformation_file = config.task.transformation_file
    if transformation_file is not None and not transformation_file.exists():
        raise FileNotFoundError("Transformation file specified but doesn't exist")

    bitfount_hub = _create_bitfounthub(
        username=config.modeller.username, url=config.hub.url
    )

    # We assume that if the user has not included a username in
    # a pod identifier that it is their own pod
    pod_identifiers = _check_and_update_pod_ids(config.pods.identifiers, bitfount_hub)

    modeller = setup_modeller(
        pod_identifiers=pod_identifiers,
        data_config=config.data_structure,
        task_details=config.task,
        bitfount_hub=bitfount_hub,
        ms_config=config.message_service,
        identity_verification_method=config.modeller.identity_verification_method,
        private_key_file=config.modeller.private_key_file,
        idp_url=config.modeller.identity_provider_url,
    )

    return modeller, pod_identifiers


def setup_modeller(
    pod_identifiers: List[str],
    data_config: DataStructureConfig,
    task_details: TaskConfig,
    bitfount_hub: BitfountHub,
    ms_config: MessageServiceConfig,
    identity_verification_method: Union[
        str, IdentityVerificationMethod
    ] = IdentityVerificationMethod.DEFAULT,
    private_key_file: Optional[Path] = None,
    idp_url: Optional[str] = None,
) -> _Modeller:
    """Creates a modeller.

    Args:
        pod_identifiers: The pod identifiers of the pods to be used in the task.
        data_config: The details of the data schema and options to be used in the task.
        task_details: The task details as a TaskConfig instance.
        bitfount_hub: The BitfountHub instance.
        ms_config: The message service settings as a MessageServiceConfig instance.
        identity_verification_method: The identity verification method to use.
        private_key_file: The path to the private key used by this modeller.
        idp_url: URL of the modeller's identity provider.

    Returns:
        The created Modeller.
    """
    # Check validity of pod names
    if not pod_identifiers:
        raise ValueError("Must provide at least one `pod_identifier`")
    _check_and_update_pod_ids(pod_identifiers, bitfount_hub)

    # Check that the schemas of the given pods match
    # TODO: [BIT-1098] Manage pods with different schemas
    schema = get_pod_schema(pod_identifiers[0], hub=bitfount_hub)
    for pod_id in pod_identifiers[1:]:
        aux_schema = get_pod_schema(pod_id, hub=bitfount_hub)
        # We need to check that the schemas have the same contents
        if aux_schema != schema:
            raise ValueError(
                "Pod schemas must match in order to be able to train on them."
            )

    # Create data structure
    if not data_config.select.include and not data_config.select.exclude:
        data_config.select.include = schema.tables[0].get_feature_names()
    data_structure = DataStructure.create_datastructure(
        table_config=data_config.table_config,
        select=data_config.select,
        transform=data_config.transform,
        assign=data_config.assign,
    )

    # Create model
    model_details = task_details.model
    if model_details.structure:
        model_structure_class = _MODEL_STRUCTURES[model_details.structure.name]
        model_structure = model_structure_class(**model_details.structure.arguments)
    model: Union[_BaseModel, BitfountModelReference]
    if model_details.name:  # i.e. built-in model
        model_name = model_details.name
        try:
            model_class = _MODELS[model_name]
        except KeyError:
            raise KeyError(
                f"Unable to load built-in model {model_name}; "
                f"does this pod have the appropriate backend installed?"
            )
        # Check if Differential Privacy can be used with this model
        # The cast here is needed to assuage mypy due to the nested Schema classes
        # being different; any classes that inherit both _BaseModel and
        # DifferentiallyPrivate will override the schema anyway.
        if issubclass(
            cast(Type[_DifferentiallyPrivate], model_class), _DifferentiallyPrivate
        ):
            # Load defined model structure, if specified
            if model_details.structure:
                model = model_class(
                    datastructure=data_structure,
                    schema=schema,
                    model_structure=model_structure,
                    dp_config=model_details.dp_config,
                    logger_config=model_details.logger_config,
                    **model_details.hyperparameters,
                )

            else:
                model = model_class(
                    datastructure=data_structure,
                    schema=schema,
                    dp_config=model_details.dp_config,
                    logger_config=model_details.logger_config,
                    **model_details.hyperparameters,
                )

        else:
            # Load defined model structure, if specified
            if model_details.structure:
                model = model_class(
                    datastructure=data_structure,
                    schema=schema,
                    model_structure=model_structure,
                    logger_config=model_details.logger_config,
                    **model_details.hyperparameters,
                )

            else:
                model = model_class(
                    datastructure=data_structure,
                    schema=schema,
                    logger_config=model_details.logger_config,
                    **model_details.hyperparameters,
                )
    elif model_details.bitfount_model:  # i.e. custom model
        # Custom DP models not currently supported
        if model_details.dp_config:
            raise ValueError(
                "Custom models cannot currently be used with Differential Privacy."
            )

        # We set the hyperparameters of the BitfountModelReference using those from
        # the config; allows the config format to avoid duplicate hyperparameter
        # fields.
        model = BitfountModelReference(
            username=model_details.bitfount_model.username,
            model_ref=model_details.bitfount_model.model_ref,
            datastructure=data_structure,
            schema=schema,
            hyperparameters=model_details.hyperparameters,
            hub=bitfount_hub,
        )

    else:
        raise TypeError(
            "Unrecognised model type: should be a built-in model "
            "or a BitfountModelReference."
        )

    # Set aggregation options
    if task_details.aggregator is not None:
        if model is not None:
            if not isinstance(
                model, (DistributedModelProtocol, BitfountModelReference)
            ):
                raise TypeError(
                    "Aggregation is only compatible with models implementing "
                    "DistributedModelProtocol or BitfountModelReference instances."
                )

        # We check early, whilst both are in scope, to ensure that, if weightings
        # have been supplied, weightings for all pods have been supplied.
        if task_details.aggregator.weights is not None:
            if (weight_pods := set(task_details.aggregator.weights.keys())) != (
                requested_pods := set(pod_identifiers)
            ):
                raise AggregatorError(
                    f"Pods in task and aggregation weightings do not match: "
                    f"{requested_pods} != {weight_pods}"
                )

        aggregator = _create_aggregator(
            secure_aggregation=task_details.aggregator.secure,
            weights=task_details.aggregator.weights,
        )
        task_details.protocol.arguments["aggregator"] = aggregator

    # Load algorithm from components
    algorithm = _ALGORITHMS[AlgorithmType(task_details.algorithm.name).name](
        **task_details.algorithm.arguments, model=model
    )

    # Load protocol from components
    protocol = _PROTOCOLS[ProtocolType(task_details.protocol.name).name](
        algorithm=algorithm,
        **task_details.protocol.arguments,
    )

    # Create Modeller
    message_service = _create_message_service(
        session=bitfount_hub.session,
        ms_config=ms_config,
    )
    modeller = _Modeller(
        protocol=protocol,
        message_service=message_service,
        bitfounthub=bitfount_hub,
        identity_verification_method=identity_verification_method,
        private_key=private_key_file,
        idp_url=idp_url,
    )

    return modeller


async def run_modeller_async(
    modeller: _Modeller,
    pod_identifiers: Iterable[str],
    model_out: Path = DEFAULT_MODEL_OUT,
) -> Optional[Any]:
    """Runs the modeller.

    Run the modeller, submitting tasks to the pods and waiting for the results.

    Args:
        modeller: The Modeller instance being used to manage the task.
        pod_identifiers: The group of pod identifiers to run the task against.
        model_out: The path to save the model out to. Defaults to "./output-model.pt".
    """
    # Start task running
    result = await modeller.run_async(pod_identifiers)
    modeller._serialize(model_out)
    if result is False:
        return None

    return result


def run_modeller(
    modeller: _Modeller,
    pod_identifiers: Iterable[str],
    model_out: Path = DEFAULT_MODEL_OUT,
) -> Optional[Any]:
    """Runs the modeller.

    Run the modeller, submitting tasks to the pods and waiting for the results.

    Args:
        modeller: The Modeller instance being used to manage the task.
        pod_identifiers: The group of pod identifiers to run the task against.
        model_out: The path to save the model out to. Defaults to "./output-model.pt".
    """
    pod_identifiers = _check_and_update_pod_ids(pod_identifiers, modeller._hub)
    return asyncio.run(run_modeller_async(modeller, pod_identifiers, model_out))
