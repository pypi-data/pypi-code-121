"""Federated Averaging protocol."""
from __future__ import annotations

import asyncio
import os
import time
from typing import (
    TYPE_CHECKING,
    Any,
    ClassVar,
    Dict,
    List,
    Mapping,
    Optional,
    Protocol,
    Tuple,
    Union,
    cast,
    runtime_checkable,
)

from marshmallow import fields

from bitfount.data.datasources.base_source import _BaseSource
from bitfount.federated.aggregators.base import (
    _AggregatorWorkerFactory,
    _BaseAggregator,
    _BaseAggregatorFactory,
    _BaseModellerAggregator,
    _BaseWorkerAggregator,
)
from bitfount.federated.aggregators.base import registry as aggregators_registry
from bitfount.federated.aggregators.secure import _InterPodAggregatorWorkerFactory
from bitfount.federated.algorithms.model_algorithms.base import (
    registry as algorithms_registry,
)
from bitfount.federated.early_stopping import FederatedEarlyStopping
from bitfount.federated.helper import _create_aggregator
from bitfount.federated.logging import _get_federated_logger
from bitfount.federated.model_reference import BitfountModelReference
from bitfount.federated.pod_vitals import _PodVitals
from bitfount.federated.privacy.differential import DPPodConfig
from bitfount.federated.protocols.base import (
    _BaseCompatibleAlgoFactory,
    _BaseModellerProtocol,
    _BaseProtocolFactory,
    _BaseWorkerProtocol,
)
from bitfount.federated.transport.modeller_transport import (
    _get_parameter_updates_from_workers,
    _get_training_metrics_from_workers,
    _ModellerMailbox,
    _send_model_parameters,
)
from bitfount.federated.transport.worker_transport import (
    _get_model_parameters,
    _InterPodWorkerMailbox,
    _send_parameter_update,
    _send_training_metrics,
    _WorkerMailbox,
)
from bitfount.federated.types import SerializedProtocol
from bitfount.hub.api import BitfountHub
from bitfount.schemas.utils import bf_dump
from bitfount.types import (
    T_DTYPE,
    T_FIELDS_DICT,
    T_NESTED_FIELDS,
    DistributedModelProtocol,
    _SerializedWeights,
    _Weights,
)

if TYPE_CHECKING:
    from bitfount.types import _DistributedModelTypeOrReference

logger = _get_federated_logger(__name__)


@runtime_checkable
class _FederatedAveragingCompatibleAlgo(Protocol[T_DTYPE]):
    @property
    def epochs(self) -> Optional[int]:
        """Number of epochs."""
        ...

    @property
    def steps(self) -> Optional[int]:
        """Number of steps."""
        ...

    @property
    def tensor_precision(self) -> T_DTYPE:
        ...


@runtime_checkable
class _FederatedAveragingCompatibleWorker(_FederatedAveragingCompatibleAlgo, Protocol):
    """Defines worker-side algorithm compatibility."""

    def initialise(
        self,
        datasource: _BaseSource,
        pod_dp: Optional[DPPodConfig] = None,
        **kwargs: Any,
    ) -> None:
        """Initialise the worker-side algorithm."""
        ...

    def run(
        self,
        data: _BaseSource,
        model_params: _SerializedWeights,
        iterations: int,
    ) -> Tuple[_Weights, Optional[Dict[str, str]]]:
        """Run the worker-side algorithm."""
        ...

    def save_final_parameters(self, model_params: _SerializedWeights) -> None:
        """Save the weights from the worker-side algorithm."""
        ...


@runtime_checkable
class _FederatedAveragingCompatibleModeller(
    _FederatedAveragingCompatibleAlgo, Protocol
):
    """Defines modeller-side algorithm compatibility."""

    def initialise(
        self,
        **kwargs: Any,
    ) -> None:
        """Initialise the modeller-side algorithm."""
        ...

    def run(
        self,
        update: Optional[_Weights] = None,
        validation_metrics: Optional[Mapping[str, float]] = None,
    ) -> _SerializedWeights:
        """Run the modeller-side algorithm."""
        ...


@runtime_checkable
class _FederatedAveragingCompatibleAlgoFactory(_BaseCompatibleAlgoFactory, Protocol):
    """Defines algorithm factory compatibility."""

    model: _DistributedModelTypeOrReference
    pretrained_file: Optional[Union[str, os.PathLike]] = None

    def modeller(self, **kwargs: Any) -> _FederatedAveragingCompatibleModeller:
        """Returns a modeller-side algorithm."""
        ...

    def worker(
        self, hub: BitfountHub, **kwargs: Any
    ) -> _FederatedAveragingCompatibleWorker:
        """Returns a worker-side algorithm."""
        ...


class _BaseFederatedAveragingMixIn:
    """Shared behaviour for the `FederatedAveraging` classes."""

    # This is set in the base protocol
    algorithm: _FederatedAveragingCompatibleAlgo

    def __init__(
        self,
        *,
        aggregator: _BaseAggregator,
        steps_between_parameter_updates: Optional[int] = None,
        epochs_between_parameter_updates: Optional[int] = None,
        **_kwargs: Any,
    ):
        self.aggregator = aggregator
        self.steps_between_parameter_updates = steps_between_parameter_updates
        self.epochs_between_parameter_updates = epochs_between_parameter_updates

    def perform_iterations_checks(self) -> None:
        """Perform checks on iterations to ensure training configuration is correct.

        Raises:
            ValueError: if there is a mismatch between model iterations and
                algorithm iterations.
        """
        if bool(self.steps_between_parameter_updates) == bool(
            self.epochs_between_parameter_updates
        ):
            raise ValueError("You must specify one (and only one) of steps or epochs.")
        if bool(self.steps_between_parameter_updates) != bool(self.algorithm.steps):
            raise ValueError(
                "Parameter update method must match model training method"
                + " i.e. steps or epochs."
            )
        if (
            # If steps_between_parameter_updates then algorithm.steps is not None
            self.steps_between_parameter_updates
            and self.steps_between_parameter_updates > self.algorithm.steps  # type: ignore[operator] # Reason: see comment # noqa: B950
        ) or (
            # If epochs_between_parameter_updates then algorithm.epochs is not None
            self.epochs_between_parameter_updates
            and self.epochs_between_parameter_updates > self.algorithm.epochs  # type: ignore[operator] # Reason: see comment # noqa: B950
        ):
            raise ValueError(
                "Number of iterations between sharing updates must not be "
                "greater than total number of model iterations."
            )

    def get_num_federated_iterations(self) -> int:
        """Returns number of rounds of federated training to be done.

        This is rounded down to the nearest whole number.
        """
        num_iterations_between_updates = cast(
            int,
            self.epochs_between_parameter_updates
            or self.steps_between_parameter_updates,
        )
        num_iterations = cast(int, self.algorithm.epochs or self.algorithm.steps)

        # floor division rounds the result down to the nearest whole number
        return num_iterations // num_iterations_between_updates


class _ModellerSide(_BaseModellerProtocol, _BaseFederatedAveragingMixIn):
    """Modeller side of the FederatedAveraging protocol."""

    aggregator: _BaseModellerAggregator
    algorithm: _FederatedAveragingCompatibleModeller

    def __init__(
        self,
        *,
        algorithm: _FederatedAveragingCompatibleModeller,
        mailbox: _ModellerMailbox,
        aggregator: _BaseModellerAggregator,
        steps_between_parameter_updates: Optional[int],
        epochs_between_parameter_updates: Optional[int],
        early_stopping: Optional[FederatedEarlyStopping],
        auto_eval: bool = True,
        **kwargs: Any,
    ):
        super().__init__(
            algorithm=algorithm,
            mailbox=mailbox,
            aggregator=aggregator,
            steps_between_parameter_updates=steps_between_parameter_updates,
            epochs_between_parameter_updates=epochs_between_parameter_updates,
            **kwargs,
        )

        self.early_stopping = early_stopping
        self.auto_eval = auto_eval
        self.validation_results: List[Dict[str, float]] = []

    async def _send_parameters(self, new_parameters: _SerializedWeights) -> None:
        """Sends central model parameters to workers."""
        logger.debug("Sending global parameters to workers")
        await _send_model_parameters(new_parameters, self.mailbox)

    async def _receive_parameter_updates(
        self,
    ) -> Dict[str, _SerializedWeights]:
        """Receives parameter updates from every worker."""
        return await _get_parameter_updates_from_workers(self.mailbox)

    async def _get_training_metrics_updates(
        self,
    ) -> Dict[str, float]:
        return await _get_training_metrics_from_workers(self.mailbox)

    async def run(
        self,
        **kwargs: Any,
    ) -> List[Dict[str, float]]:
        """Receives updates and sends new parameters in a loop."""
        self.algorithm.initialise()
        self.perform_iterations_checks()
        initial_parameters = self.algorithm.run(update=None)
        await self._send_parameters(initial_parameters)
        num_federated_iterations = self.get_num_federated_iterations()
        for i in range(1, num_federated_iterations + 1):
            if self.algorithm.epochs:
                logger.info(f"Federated Epoch {i}")
            else:
                logger.info(f"Federated Step {i}")

            logger.info("Sending model parameters to Pods")
            if self.auto_eval:
                # We create this as a task so that it can process TRAINING_METRICS
                # messages in the background without blocking TRAINING_UPDATE
                # messages.
                validation_metrics_task = asyncio.create_task(
                    self._get_training_metrics_updates()
                )

            # from worker(s)
            weight_updates = await self._receive_parameter_updates()
            parameter_update = self.aggregator.run(
                parameter_updates=weight_updates,
                tensor_dtype=self.algorithm.tensor_precision,
            )
            if self.auto_eval:
                # This is guaranteed to be bound as it's creation is also in a
                # `if self.auto_eval:` block.
                # noinspection PyUnboundLocalVariable
                await validation_metrics_task
                validation_metrics: Dict[str, float] = validation_metrics_task.result()
                logger.info(
                    f"Validation Metrics at iteration {i}: {validation_metrics}"
                )
                # Each item in the list is the average results from every worker
                # for a given iteration. New results are appended to the list
                # such that the final item is always the latest.
                self.validation_results.append(validation_metrics)

                new_parameters = self.algorithm.run(
                    update=parameter_update, validation_metrics=validation_metrics
                )
                # Send the latest averaged validation metrics only at each iteration
            else:
                new_parameters = self.algorithm.run(update=parameter_update)

            logger.federated_info("Sending updated parameters")
            await self._send_parameters(
                new_parameters
            )  # Workers end up with final model

            # TODO: [BIT-970] consider moving early stopping to be handled in a side
            #       channel as part of handler based approach
            training_complete = False
            if self.early_stopping is not None:
                training_complete = self.early_stopping.check(self.validation_results)
            await self.mailbox.send_training_iteration_complete_update(
                training_complete
            )
            if training_complete:
                logger.info("Early stopping criterion met. Stopping training.")
                break
        await self.mailbox.send_task_complete_message()
        modeller_results = self.validation_results
        return modeller_results


class _WorkerSide(_BaseWorkerProtocol, _BaseFederatedAveragingMixIn):
    """Worker side of the FederatedAveraging protocol."""

    aggregator: _BaseWorkerAggregator
    algorithm: _FederatedAveragingCompatibleWorker

    def __init__(
        self,
        *,
        algorithm: _FederatedAveragingCompatibleWorker,
        mailbox: _WorkerMailbox,
        aggregator: _BaseWorkerAggregator,
        steps_between_parameter_updates: Optional[int],
        epochs_between_parameter_updates: Optional[int],
        auto_eval: bool = True,
        **kwargs: Any,
    ):
        super().__init__(
            algorithm=algorithm,
            mailbox=mailbox,
            aggregator=aggregator,
            steps_between_parameter_updates=steps_between_parameter_updates,
            epochs_between_parameter_updates=epochs_between_parameter_updates,
            auto_eval=auto_eval,
            **kwargs,
        )
        self.auto_eval = auto_eval

    async def _receive_parameters(self) -> _SerializedWeights:
        """Receives new global model parameters."""
        logger.debug("Receiving global parameters")
        return await _get_model_parameters(self.mailbox)

    async def _send_training_metrics(
        self,
        validation_metrics: Optional[Mapping[str, str]] = None,
    ) -> None:
        """Sends training metrics update."""
        if validation_metrics:
            logger.debug("Sending validation metrics to modeller")
            await _send_training_metrics(validation_metrics, self.mailbox)

    async def _send_parameter_update(
        self, parameter_update: _SerializedWeights
    ) -> None:
        """Sends parameter update."""
        logger.debug("Sending parameter update to modeller")
        await _send_parameter_update(parameter_update, self.mailbox)

    async def run(
        self,
        datasource: _BaseSource,
        pod_dp: Optional[DPPodConfig] = None,
        pod_vitals: Optional[_PodVitals] = None,
        pod_identifier: Optional[str] = None,
        **kwargs: Any,
    ) -> None:
        """Receives parameters and sends updates in a loop."""
        self.algorithm.initialise(datasource=datasource, pod_dp=pod_dp)
        self.perform_iterations_checks()
        serialized_model_params = await self._receive_parameters()

        num_federated_iterations = self.get_num_federated_iterations()
        for i in range(1, num_federated_iterations + 1):
            if self.algorithm.epochs:
                logger.info(f"Federated Epoch {i}")
                iterations = self.epochs_between_parameter_updates
            else:
                logger.info(f"Federated Step {i}")
                iterations = self.steps_between_parameter_updates
            iterations = cast(int, iterations)
            logger.federated_info("Running algorithm")
            if pod_vitals:
                pod_vitals.last_task_execution_time = time.time()
            parameter_update, validation_metrics = self.algorithm.run(
                datasource, serialized_model_params, iterations
            )

            # Aggregator returns the difference between the new and old model parameters
            aggregated_parameter_update = await self.aggregator.run(
                parameter_update=parameter_update
            )

            if self.auto_eval:
                logger.info(
                    f"Validation Metrics at iteration {i}: {validation_metrics}"
                )
                await self._send_training_metrics(validation_metrics)
            await self._send_parameter_update(aggregated_parameter_update)
            serialized_model_params = await self._receive_parameters()

            # TODO: [BIT-970] consider moving early stopping to be handled in a side
            # channel as part of handler based approach
            training_complete = (
                await self.mailbox.get_training_iteration_complete_update()
            )
            if training_complete:
                logger.info(
                    "Modeller reporting early stopping criterion met. "
                    + "Stopping training.",
                )
                break
        await self.mailbox.get_task_complete_update()
        self.algorithm.save_final_parameters(serialized_model_params)


class FederatedAveraging(_BaseProtocolFactory):
    """Original Federated Averaging algorithm by McMahan et al. (2017).

    This protocol performs a predetermined number of epochs or steps of training on
    each remote Pod before sending the updated model parameters to the modeller. These
    parameters are then averaged and sent back to the Pods for as many federated
    iterations as the Modeller specifies.

    Args:
        algorithm: The algorithm to use for training. This must be compatible with the
            `FederatedAveraging` protocol.
        aggregator: The aggregator to use for updating the model parameters across all
            Pods participating in the task.
        steps_between_parameter_updates: The number of steps between parameter updates,
            i.e. the number of rounds of local training before parameters are updated.
            If `epochs_between_parameter_updates` is provided,
            `steps_between_parameter_updates` cannot be provided. Defaults to None.
        epochs_between_parameter_updates: The number of epochs between parameter
            updates, i.e. the number of rounds of local training before parameters are
            updated. If `steps_between_parameter_updates` is provided,
            `epochs_between_parameter_updates` cannot be provided. Defaults to None.
        auto_eval: Whether to automatically evaluate the model on the validation
            dataset. Defaults to True.

    Attributes:
        name: The name of the protocol.
        algorithm: The algorithm to use for training
        aggregator: The aggregator to use for updating the model parameters.
        steps_between_parameter_updates: The number of steps between parameter updates.
        epochs_between_parameter_updates: The number of epochs between parameter
            updates.
        auto_eval: Whether to automatically evaluate the model on the validation
            dataset.

    Raises:
        TypeError: If the `algorithm` is not compatible with the protocol.

    :::tip

    For more information, take a look at the seminal paper:
    https://arxiv.org/abs/1602.05629

    :::
    """

    algorithm: _FederatedAveragingCompatibleAlgoFactory
    fields_dict: ClassVar[T_FIELDS_DICT] = {
        "steps_between_parameter_updates": fields.Integer(allow_none=True),
        "epochs_between_parameter_updates": fields.Integer(allow_none=True),
        "auto_eval": fields.Boolean(),
    }
    nested_fields: ClassVar[T_NESTED_FIELDS] = {
        "algorithm": algorithms_registry,
        "aggregator": aggregators_registry,
    }

    def __init__(
        self,
        *,
        algorithm: _FederatedAveragingCompatibleAlgoFactory,
        aggregator: Optional[_BaseAggregatorFactory] = None,
        steps_between_parameter_updates: Optional[int] = None,
        epochs_between_parameter_updates: Optional[int] = None,
        auto_eval: bool = True,
        secure_aggregation: bool = False,
        **kwargs: Any,
    ) -> None:
        if kwargs.get("model"):
            logger.warning("Ignoring provided model. Algorithm already has a model.")
        super().__init__(algorithm=algorithm, **kwargs)
        if aggregator:
            self.aggregator = aggregator
        else:
            self.aggregator = _create_aggregator(secure_aggregation=secure_aggregation)
        self.steps_between_parameter_updates = steps_between_parameter_updates
        self.epochs_between_parameter_updates = epochs_between_parameter_updates
        self.auto_eval = auto_eval
        if not steps_between_parameter_updates and not epochs_between_parameter_updates:
            logger.info(
                "Neither steps_between_parameter_updates or "
                "epochs_between_parameter_updates were set ..."
            )
            if isinstance(algorithm.model, DistributedModelProtocol):
                if bool(algorithm.model.epochs):
                    logger.info("Setting epochs_between_parameter_updates to 1.")
                    self.epochs_between_parameter_updates = 1
                else:
                    logger.info("Setting steps_between_parameter_updates to 1.")
                    self.steps_between_parameter_updates = 1
            elif isinstance(self.algorithm.model, BitfountModelReference):
                if self.algorithm.model.hyperparameters.get("epochs"):
                    logger.info("Setting epochs_between_parameter_updates to 1.")
                    self.epochs_between_parameter_updates = 1
                else:
                    logger.info("Setting steps_between_parameter_updates to 1.")
                    self.steps_between_parameter_updates = 1

    @classmethod
    def _validate_algorithm(cls, algorithm: _BaseCompatibleAlgoFactory) -> None:
        """Checks that `algorithm` is compatible with the protocol.

        Raises:
            TypeError: If the `algorithm` is not compatible with the protocol.
        """
        if not isinstance(algorithm, _FederatedAveragingCompatibleAlgoFactory):
            raise TypeError(
                f"The {cls.__name__} protocol does not support "
                + f"the {type(algorithm).__name__} algorithm.",
            )

    def modeller(
        self,
        mailbox: _ModellerMailbox,
        early_stopping: Optional[FederatedEarlyStopping] = None,
        **kwargs: Any,
    ) -> _ModellerSide:
        """Returns the modeller side of the FederatedAveraging protocol."""
        return _ModellerSide(
            algorithm=self.algorithm.modeller(
                pretrained_file=self.algorithm.pretrained_file
            ),
            aggregator=self.aggregator.modeller(),
            steps_between_parameter_updates=self.steps_between_parameter_updates,
            epochs_between_parameter_updates=self.epochs_between_parameter_updates,
            auto_eval=self.auto_eval,
            mailbox=mailbox,
            early_stopping=early_stopping,
            **kwargs,
        )

    def worker(
        self,
        mailbox: _WorkerMailbox,
        hub: BitfountHub,
        **kwargs: Any,
    ) -> _WorkerSide:
        """Returns the worker side of the FederatedAveraging protocol."""
        if isinstance(self.aggregator, _AggregatorWorkerFactory):
            worker_agg = self.aggregator.worker()
        elif isinstance(self.aggregator, _InterPodAggregatorWorkerFactory):
            if not isinstance(mailbox, _InterPodWorkerMailbox):
                raise TypeError(
                    "Inter-pod aggregators require an inter-pod worker mailbox."
                )
            worker_agg = self.aggregator.worker(mailbox=mailbox)
        else:
            raise TypeError(
                f"Unrecognised aggregator factory ({type(self.aggregator)}); "
                f"unable to determine how to call .worker() factory method."
            )
        return _WorkerSide(
            algorithm=self.algorithm.worker(hub=hub),
            aggregator=worker_agg,
            steps_between_parameter_updates=self.steps_between_parameter_updates,
            epochs_between_parameter_updates=self.epochs_between_parameter_updates,
            auto_eval=self.auto_eval,
            mailbox=mailbox,
            **kwargs,
        )

    def dump(self) -> SerializedProtocol:
        """Returns the JSON-serializable representation of the protocol."""
        return cast(SerializedProtocol, bf_dump(self))
