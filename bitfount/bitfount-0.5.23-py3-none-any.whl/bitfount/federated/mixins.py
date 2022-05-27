"""MixIn classes for compatible models with the federated algorithms."""
from __future__ import annotations

from abc import ABC, abstractmethod
import os
from pathlib import Path
from typing import (
    TYPE_CHECKING,
    Any,
    Dict,
    List,
    Mapping,
    MutableMapping,
    Optional,
    Sequence,
    Tuple,
    Union,
    cast,
)

from cryptography.hazmat.primitives.asymmetric.rsa import RSAPrivateKey
import numpy as np
import pandas as pd

from bitfount.data.dataloaders import _BitfountDataLoader
from bitfount.data.datasources.base_source import _BaseSource
from bitfount.federated.aggregators.base import _BaseAggregatorFactory
from bitfount.federated.algorithms.model_algorithms.evaluate import ModelEvaluation
from bitfount.federated.algorithms.model_algorithms.federated_training import (
    FederatedModelTraining,
)
from bitfount.federated.authorisation_checkers import IdentityVerificationMethod
from bitfount.federated.helper import (
    _check_and_update_pod_ids,
    _create_aggregator,
    _create_message_service,
    _get_idp_url,
)
from bitfount.federated.modeller import _Modeller
from bitfount.federated.protocols.fed_avg import FederatedAveraging
from bitfount.federated.protocols.results_only import (
    ResultsOnly,
    _ResultsOnlyCompatibleAlgoFactory_,
)
from bitfount.federated.transport.message_service import _MessageService
from bitfount.hub.helper import _create_bitfounthub
from bitfount.types import DistributedModelProtocol

if TYPE_CHECKING:
    from bitfount.data.datastructure import DataStructure
    from bitfount.federated.transport.config import MessageServiceConfig
    from bitfount.hub.api import BitfountHub
    from bitfount.metrics import Metric
    from bitfount.types import T_DTYPE, _SerializedWeights, _Weights, _Residuals

from bitfount.federated.logging import _get_federated_logger

logger = _get_federated_logger(__name__)


class _DistributedModelMixIn(ABC):
    """A mixin for models used in federated mechanisms.

    An abstract base mixin for models that are compatible with the following
    distributed learning protocols:
        - FederatedAveraging
    """

    datastructure: DataStructure
    # Denotes the Pod the model is running in (if any)
    pod_identifier: Optional[str] = None

    @abstractmethod
    def get_param_states(self) -> _Weights:
        """Gets the current states of the trainable parameters of the model.

        Returns:
            A dict of param names to tensors
        """
        raise NotImplementedError

    @abstractmethod
    def apply_weight_updates(self, weight_updates: Sequence[_Residuals]) -> _Weights:
        """Applies weight updates to the weights of this model.

        Apply a sequence of parameter weight updates (mappings of parameter name
        to a tensor describing the weight update) to the parameters of this model.
        Used by Modeller to apply updates received from Workers.

        Args:
            weight_updates (Sequence[_Residuals]): The sequence
                of weight updates

        Returns:
            The updated parameters as a dict of name to tensor.
        """
        raise NotImplementedError

    @abstractmethod
    def update_params(self, new_model_params: _Weights) -> None:
        """Updates the current model parameters to the ones provided.

        Used by Worker to update new parameters received from Modeller.

        Args:
            new_model_params (WeightMapping): The new model parameters
                to update to as a mapping of parameter names to tensors.
        """
        raise NotImplementedError

    @abstractmethod
    def deserialize_params(self, serialized_weights: _SerializedWeights) -> _Weights:
        """Converts serialized model parameters to tensors.

        Used by Worker to convert serialized parameters received from Modeller.

        Args:
            serialized_weights (_SerializedWeights): The model parameters
                to deserialize.
        """
        raise NotImplementedError

    @abstractmethod
    def serialize_params(self, weights: _Weights) -> _SerializedWeights:
        """Serializes model parameters.

        Used by Modeller to serialize model parameters to send to the Worker.

        Args:
            weights (_Weights): The model parameters
                to serialize.
        """
        raise NotImplementedError

    @abstractmethod
    def diff_params(self, old_params: _Weights, new_params: _Weights) -> _Residuals:
        """Calculates the difference between two sets of model parameters."""
        raise NotImplementedError

    @abstractmethod
    def set_model_training_iterations(self, iterations: int) -> None:
        """Sets model steps or epochs to the appropriate number between updates."""
        raise NotImplementedError

    @abstractmethod
    def reset_trainer(self) -> None:
        """Resets the trainer to its initial state.

        :::note

        Importantly, calling this method in between `fit` calls allows the caller to
        repeatedly refit the model continuing from the batch after the one that was last
        fit. This only applies to step-wise training.

        :::
        """
        raise NotImplementedError

    @abstractmethod
    def log_(self, name: str, value: Any, **kwargs: Any) -> Any:
        """Logs a metric with a particular value to the user's configured model loggers.

        Args:
            name: The name of the metric to log
            value: The value of the metric to log
            **kwargs: Additional keyword arguments to pass to the logger
        """
        raise NotImplementedError

    @abstractmethod
    def tensor_precision(self) -> T_DTYPE:
        """Gets the floating point precision used by model tensors.

        Typically this will be 32 bits.
        """
        raise NotImplementedError

    @abstractmethod
    def _fit_local(
        self,
        data: _BaseSource,
        metrics: Optional[MutableMapping[str, Metric]] = None,
        **kwargs: Any,
    ) -> Dict[str, str]:
        """Fits model locally using data from `datasource`.

        Should be implemented in the final model class that subclasses
        DistributedModelMixIn.
        """
        raise NotImplementedError

    def set_pod_identifier(self, pod_identifier: str) -> None:
        """Sets the pod identifier for the model.

        This must be called on the Pod/Worker side in Distributed training because it
        is needed for the model to be able to extract the relevant information from the
        datastructure sent by the Modeller.

        Args:
            pod_identifier: The pod identifier for the model.
        """
        self.pod_identifier = pod_identifier

    def _fit_federated(
        self,
        pod_identifiers: List[str],
        username: Optional[str] = None,
        aggregator: Optional[_BaseAggregatorFactory] = None,
        steps_between_parameter_updates: Optional[int] = None,
        epochs_between_parameter_updates: Optional[int] = None,
        bitfounthub: Optional[BitfountHub] = None,
        ms_config: Optional[MessageServiceConfig] = None,
        message_service: Optional[_MessageService] = None,
        pod_public_key_paths: Optional[Mapping[str, Path]] = None,
        pretrained_file: Optional[Union[str, os.PathLike]] = None,
        secure_aggregation: bool = False,
        auto_eval: bool = True,
        identity_verification_method: IdentityVerificationMethod = IdentityVerificationMethod.DEFAULT,  # noqa: B950
        private_key_or_file: Optional[Union[RSAPrivateKey, Path]] = None,
        idp_url: Optional[str] = None,
        model_out: Optional[Union[Path, str]] = None,
    ) -> Optional[Dict[str, str]]:
        """Fits model federated-ly."""
        algorithm = FederatedModelTraining(
            model=cast(DistributedModelProtocol, self), pretrained_file=pretrained_file
        )

        if not bitfounthub:
            bitfounthub = _create_bitfounthub(username=username)

        pod_identifiers = _check_and_update_pod_ids(pod_identifiers, bitfounthub)
        datastructure_pod_identifiers = self.datastructure.get_pod_identifiers()
        if datastructure_pod_identifiers:
            datastructure_pod_identifiers = _check_and_update_pod_ids(
                datastructure_pod_identifiers, bitfounthub
            )
            self.datastructure._update_datastructure_with_hub_identifiers(
                datastructure_pod_identifiers
            )

        if not message_service:
            message_service = _create_message_service(bitfounthub.session, ms_config)

        if not aggregator:
            aggregator = _create_aggregator(secure_aggregation=secure_aggregation)
        if not idp_url:
            idp_url = _get_idp_url()
        # TODO: [BIT-1098] Manage pods with different schemas
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

        # Run task
        result = modeller.run(pod_identifiers, model_out=model_out)
        if result is False:
            return None
        else:
            return result

    def fit(
        self,
        data: Optional[_BaseSource] = None,
        metrics: Optional[Dict[str, Metric]] = None,
        pod_identifiers: Optional[List[str]] = None,
        **kwargs: Any,
    ) -> Optional[Dict[str, str]]:
        """Fits model either locally or federated-ly.

        `pod_identifiers` must be provided for federated training.

        Args:
            data: Datasource for training. Defaults to None.
            metrics: Metrics to calculate for validation. Defaults to None.
            pod_identifiers: List of pod identifiers. If this is provided, the model
                will be trained in a federated manner. Defaults to None.
            private_key_or_file: Either private key or path to private key file.
                Defaults to None.
            kwargs: Optional keyword arguments passed to the federated fit method.

        """
        if pod_identifiers is not None:
            logger.info(f"Training federated with pods: {', '.join(pod_identifiers)}.")
            return self._fit_federated(pod_identifiers=pod_identifiers, **kwargs)
        elif data is not None:
            logger.info("Training locally using `self.datasource`.")
            return self._fit_local(data=data, metrics=metrics)
        else:
            raise (
                ValueError(
                    "Please provide either pod identifiers "
                    "or a datasource for model training."
                )
            )

    def evaluate(
        self,
        test_dl: Optional[_BitfountDataLoader] = None,
        pod_identifiers: Optional[List[str]] = None,
        **kwargs: Any,
    ) -> Union[Tuple[np.ndarray, np.ndarray], Dict[str, float]]:
        """Evaluates model either locally or federated-ly.

        `pod_identifiers` must be provided for federated evaluation.

        Args:
            test_dl: Optional dataloader to run inference on which takes precedence over
                the dataloader returned by `self.test_dataloader`.
            pod_identifiers: List of pod identifiers. If this is provided, the model
                will be trained in a federated manner. Defaults to None.
            kwargs: Optional keyword arguments passed to the federated evaluate method.

        Returns:
            Either:
                - A tuple of numpy arrays containing the predicted and actual values if
                evaluated locally.
                - A dictionary of metrics if evaluated remotely.
        """
        if pod_identifiers is not None:
            logger.info(f"Evaluating model on pods: {', '.join(pod_identifiers)}.")
            return self._evaluate_federated(pod_identifiers=pod_identifiers, **kwargs)

        logger.info("Evaluating model locally")
        return self._evaluate_local(test_dl=test_dl)

    def _evaluate_local(
        self, test_dl: Optional[_BitfountDataLoader] = None, **kwargs: Any
    ) -> Tuple[np.ndarray, np.ndarray]:
        """This method runs inference on the test dataloader.

        Args:
            test_dl: Optional dataloader to run inference on which takes precedence over
                the dataloader returned by `self.test_dataloader`.

        Returns:
            A tuple of predictions and targets as numpy arrays.
        """
        raise NotImplementedError

    def _evaluate_federated(
        self,
        pod_identifiers: List[str],
        username: Optional[str] = None,
        bitfounthub: Optional[BitfountHub] = None,
        ms_config: Optional[MessageServiceConfig] = None,
        message_service: Optional[_MessageService] = None,
        pod_public_key_paths: Optional[Mapping[str, Path]] = None,
        pretrained_file: Optional[Union[str, os.PathLike]] = None,
        identity_verification_method: IdentityVerificationMethod = IdentityVerificationMethod.DEFAULT,  # noqa: B950
        private_key_or_file: Optional[Union[RSAPrivateKey, Path]] = None,
        idp_url: Optional[str] = None,
        model_out: Optional[Union[Path, str]] = None,
    ) -> Dict[str, float]:
        """Evaluates model remotely on all the specified pods separately.

        Returns:
            A dictionary of metrics.
        """
        algorithm = ModelEvaluation(
            model=cast(DistributedModelProtocol, self), pretrained_file=pretrained_file
        )

        if not bitfounthub:
            bitfounthub = _create_bitfounthub(username=username)

        pod_identifiers = _check_and_update_pod_ids(pod_identifiers, bitfounthub)
        datastructure_pod_identifiers = self.datastructure.get_pod_identifiers()
        if datastructure_pod_identifiers:
            datastructure_pod_identifiers = _check_and_update_pod_ids(
                datastructure_pod_identifiers, bitfounthub
            )
            self.datastructure._update_datastructure_with_hub_identifiers(
                datastructure_pod_identifiers
            )
        if not message_service:
            message_service = _create_message_service(bitfounthub.session, ms_config)

        if not idp_url:
            idp_url = _get_idp_url()

        protocol = ResultsOnly(algorithm=algorithm)

        modeller = _Modeller(
            protocol=protocol,
            message_service=message_service,
            bitfounthub=bitfounthub,
            pod_public_key_paths=pod_public_key_paths,
            identity_verification_method=identity_verification_method,
            private_key=private_key_or_file,
            idp_url=idp_url,
        )

        metrics = modeller.run(pod_identifiers, model_out=model_out)
        return cast(Dict[str, float], metrics)


class _SQLAlgorithmMixIn(ABC):
    """A mixin for SQL Algorithms.

    An abstract base mixin for SQL algorithms that are compatible with the
    ResultOnly protocol.
    """

    def execute(
        self: _ResultsOnlyCompatibleAlgoFactory_,
        pod_identifiers: List[str],
        username: Optional[str] = None,
        bitfounthub: Optional[BitfountHub] = None,
        ms_config: Optional[MessageServiceConfig] = None,
        message_service: Optional[_MessageService] = None,
        pod_public_key_paths: Optional[Mapping[str, Path]] = None,
        identity_verification_method: IdentityVerificationMethod = IdentityVerificationMethod.DEFAULT,  # noqa: B950
        private_key_or_file: Optional[Union[RSAPrivateKey, Path]] = None,
        idp_url: Optional[str] = None,
    ) -> List[pd.DataFrame]:
        """Execute ResultsOnly compatible algorithm.

        Syntactic sugar to allow the modeller to call `.execute(...)` on
        ResultsOnly compatible algorithms.
        """
        if not bitfounthub:
            bitfounthub = _create_bitfounthub(username=username)

        pod_identifiers = _check_and_update_pod_ids(pod_identifiers, bitfounthub)

        if not message_service:
            message_service = _create_message_service(bitfounthub.session, ms_config)

        if not idp_url:
            idp_url = _get_idp_url()

        protocol = ResultsOnly(algorithm=cast(_ResultsOnlyCompatibleAlgoFactory_, self))  # type: ignore[redundant-cast] # Reason: errors either way # noqa: B950
        modeller = _Modeller(
            protocol=protocol,
            message_service=message_service,
            bitfounthub=bitfounthub,
            pod_public_key_paths=pod_public_key_paths,
            identity_verification_method=identity_verification_method,
            private_key=private_key_or_file,
            idp_url=idp_url,
        )

        result = cast(List[pd.DataFrame], modeller.run(pod_identifiers=pod_identifiers))
        return result
