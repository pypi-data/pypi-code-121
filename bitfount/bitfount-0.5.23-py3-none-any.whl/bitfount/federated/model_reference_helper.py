"""Helper module for easier custom model training."""
from __future__ import annotations

import os
from pathlib import Path
from typing import TYPE_CHECKING, Dict, List, Mapping, Optional, Union

from cryptography.hazmat.primitives.asymmetric.rsa import RSAPrivateKey

from bitfount.federated.algorithms.model_algorithms.federated_training import (
    FederatedModelTraining,
)
from bitfount.federated.authorisation_checkers import IdentityVerificationMethod
from bitfount.federated.helper import (
    _check_and_update_pod_ids,
    _create_aggregator,
    _create_message_service,
)
from bitfount.federated.modeller import _Modeller
from bitfount.federated.protocols.fed_avg import (
    FederatedAveraging,
    _FederatedAveragingCompatibleAlgoFactory,
)

if TYPE_CHECKING:
    from bitfount.federated.aggregators.base import _BaseAggregatorFactory
    from bitfount.federated.model_reference import BitfountModelReference
    from bitfount.federated.protocols.base import _BaseProtocolFactory
    from bitfount.federated.transport.config import MessageServiceConfig
    from bitfount.federated.transport.message_service import _MessageService


def create_and_run_modeller_from_bf_model_ref(
    model_ref: BitfountModelReference,
    pod_identifiers: List[str],
    algorithm: Optional[_FederatedAveragingCompatibleAlgoFactory] = None,
    protocol: Optional[_BaseProtocolFactory] = None,
    aggregator: Optional[_BaseAggregatorFactory] = None,
    steps_between_parameter_updates: Optional[int] = None,
    epochs_between_parameter_updates: Optional[int] = None,
    ms_config: Optional[MessageServiceConfig] = None,
    message_service: Optional[_MessageService] = None,
    pod_public_key_paths: Optional[Mapping[str, Path]] = None,
    pretrained_file: Optional[Union[str, os.PathLike]] = None,
    secure_aggregation: bool = False,
    auto_eval: bool = True,
    identity_verification_method: IdentityVerificationMethod = IdentityVerificationMethod.DEFAULT,  # noqa: B950
    private_key_or_file: Optional[Union[RSAPrivateKey, Path]] = None,
    idp_url: Optional[str] = None,
    model_out: Optional[Path] = None,
) -> Optional[Dict[str, str]]:
    """Helper function for easier custom model training.

    Args:
        model_ref: A `BitfountModelRefrence` object.
        pod_identifiers: list of pod identifiers on which to train.
        algorithm: The algorithm to use for training. Will use
            Federated Model Training algorithm if not provided.
        protocol: The protocol to use for training. Will use the
            `Federated Averaging` protocol if not provided
        aggregator: Aggregator to use.
        steps_between_parameter_updates: The number of steps between parameter updates.
            Protocol hyperparam.
        epochs_between_parameter_updates: The number of epochs between parameter
            updates. Protocol hyperparam.
        ms_config: Message service configuration. Defaults to None.
        message_service: The message service to use for communication with pods.
            Defaults to None, in which case a new message service will be created.
        pod_public_key_paths: Optional. Mapping of pod identifiers to public
            key files for existing pod public keys. Expired or non-existent
            keys will be downloaded from the Hub.
        pretrained_file: Path to a file containing pretrained model parameters.
            Defaults to None.
        secure_aggregation: Boolean denoting whether aggregator should be secure.
            Defaults to False.
        auto_eval: Whether to calculate validation metrics. Defaults to True.
        identity_verification_method: The identity verification method to use.
            Defaults to OIDC_DEVICE_CODE.
        private_key_or_file: This modeller's private key either as an `RSAPrivateKey`
            instance or a path to a private key file. If a non-key-based identity
            verification method is used, this is ignored. Defaults to None.
        idp_url: URL of identity provider, used for the SAML Identity
            Verification Method. Defaults to None.
        model_out: If specified, path to save the model out to.

    Raises:
          ValueError if both steps and epoch are specified in the model hyperparameters
          or if none of epochs or steps are specified.
    """
    if not algorithm:
        algorithm = FederatedModelTraining(
            model=model_ref, pretrained_file=pretrained_file
        )
    elif pretrained_file:
        algorithm.pretrained_file = pretrained_file

    if "epochs" in model_ref.hyperparameters and "steps" in model_ref.hyperparameters:
        raise ValueError("You must specify one (and only one) of steps or epochs.")
    elif (
        "epochs" not in model_ref.hyperparameters
        and "steps" not in model_ref.hyperparameters
    ):
        raise ValueError(
            "You must specify at least one of steps or epochs "
            "in the model hyperparameters."
        )
    bitfounthub = model_ref.hub

    pod_identifiers = _check_and_update_pod_ids(pod_identifiers, bitfounthub)

    if not message_service:
        message_service = _create_message_service(bitfounthub.session, ms_config)
    if not aggregator:
        aggregator = _create_aggregator(secure_aggregation=secure_aggregation)
    if not protocol:
        protocol = FederatedAveraging(
            algorithm=algorithm,
            aggregator=aggregator,
            steps_between_parameter_updates=steps_between_parameter_updates,
            epochs_between_parameter_updates=epochs_between_parameter_updates,
            auto_eval=auto_eval,
        )
    modeller = _Modeller(
        protocol=protocol,
        message_service=message_service,
        bitfounthub=bitfounthub,
        pod_public_key_paths=pod_public_key_paths,
        identity_verification_method=identity_verification_method,
        private_key=private_key_or_file,
        idp_url=idp_url,
    )
    result = modeller.run(pod_identifiers, model_out=model_out)
    if result is False:
        return None
    else:
        return result
