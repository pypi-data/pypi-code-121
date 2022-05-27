"""Results Only protocol."""
from __future__ import annotations

import os
import time
from typing import (
    TYPE_CHECKING,
    Any,
    ClassVar,
    List,
    Optional,
    Protocol,
    Union,
    cast,
    overload,
    runtime_checkable,
)

from bitfount.data.datasources.base_source import _BaseSource
import bitfount.federated.algorithms.base as algorithms
from bitfount.federated.algorithms.model_algorithms.base import (
    _BaseModellerModelAlgorithm,
    _BaseWorkerModelAlgorithm,
)
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
    _ModellerMailbox,
    _send_model_parameters,
)
from bitfount.federated.transport.worker_transport import (
    _get_model_parameters,
    _WorkerMailbox,
)
from bitfount.federated.types import SerializedProtocol
from bitfount.schemas.utils import bf_dump
from bitfount.types import (
    T_FIELDS_DICT,
    T_NESTED_FIELDS,
    DistributedModelProtocol,
    _SerializedWeights,
    _Weights,
)

if TYPE_CHECKING:
    from bitfount.hub.api import BitfountHub

logger = _get_federated_logger(__name__)


@runtime_checkable
class _ResultsOnlyCompatibleModeller(Protocol):
    """Defines modeller-side algorithm compatibility."""

    def initialise(
        self,
        **kwargs: Any,
    ) -> None:
        """Initialise the modeller-side algorithm."""
        ...

    def run(self, results: List[Any]) -> List[Any]:
        """Run the modeller-side algorithm."""
        ...


@runtime_checkable
class _ResultsOnlyCompatibleWorker(Protocol):
    @overload
    def initialise(
        self,
        datasource: _BaseSource,
        **kwargs: Any,
    ) -> None:
        ...

    @overload
    def initialise(
        self,
        datasource: _BaseSource,
        pod_dp: Optional[DPPodConfig] = None,
        **kwargs: Any,
    ) -> None:
        ...

    def initialise(
        self,
        datasource: _BaseSource,
        pod_dp: Optional[DPPodConfig] = None,
        model_params: Optional[_SerializedWeights] = None,
        **kwargs: Any,
    ) -> None:
        """Initialise the worker-side algorithm."""
        ...


@runtime_checkable
class _ResultsOnlyDataIncompatibleWorker(_ResultsOnlyCompatibleWorker, Protocol):
    """Defines modeller-side algorithm compatibility without datasource.."""

    def run(self) -> Any:
        """Run the worker-side algorithm."""
        ...


@runtime_checkable
class _ResultsOnlyDataCompatibleWorker(_ResultsOnlyCompatibleWorker, Protocol):
    """Defines modeller-side algorithm compatibility with datasource needed."""

    def run(self, data: _BaseSource) -> Any:
        """Run the worker-side algorithm."""
        ...


class _ModellerSide(_BaseModellerProtocol):
    """Modeller side of the ResultsOnly protocol."""

    algorithm: _ResultsOnlyCompatibleModeller

    def __init__(
        self,
        *,
        algorithm: _ResultsOnlyCompatibleModeller,
        mailbox: _ModellerMailbox,
        **kwargs: Any,
    ):
        super().__init__(algorithm=algorithm, mailbox=mailbox, **kwargs)

    async def _send_parameters(self, new_parameters: _SerializedWeights) -> None:
        """Sends central model parameters to workers."""
        logger.debug("Sending global parameters to workers")
        await _send_model_parameters(new_parameters, self.mailbox)

    async def run(
        self,
        **kwargs: Any,
    ) -> List[Any]:
        """Runs Modeller side of the protocol."""
        self.algorithm.initialise()
        if isinstance(self.algorithm, _BaseModellerModelAlgorithm):
            initial_parameters: _Weights = self.algorithm.model.get_param_states()
            serialized_params = self.algorithm.model.serialize_params(
                initial_parameters
            )
            await self._send_parameters(serialized_params)
        eval_results = await self.mailbox.get_evaluation_results_from_workers()
        modeller_results = self.algorithm.run(eval_results)
        await self.mailbox.send_task_complete_message()
        return modeller_results


class _WorkerSide(_BaseWorkerProtocol):
    """Worker side of the ResultsOnly protocol."""

    algorithm: Union[
        _ResultsOnlyDataIncompatibleWorker, _ResultsOnlyDataCompatibleWorker
    ]

    def __init__(
        self,
        *,
        algorithm: Union[
            _ResultsOnlyDataIncompatibleWorker, _ResultsOnlyDataCompatibleWorker
        ],
        mailbox: _WorkerMailbox,
        **kwargs: Any,
    ):
        super().__init__(algorithm=algorithm, mailbox=mailbox, **kwargs)

    async def _receive_parameters(self) -> _SerializedWeights:
        """Receives new global model parameters."""
        logger.debug("Receiving global parameters")
        return await _get_model_parameters(self.mailbox)

    async def run(
        self,
        datasource: _BaseSource,
        pod_dp: Optional[DPPodConfig] = None,
        pod_vitals: Optional[_PodVitals] = None,
        pod_identifier: Optional[str] = None,
        **kwargs: Any,
    ) -> None:
        """Runs Worker side of the protocol."""
        if isinstance(self.algorithm, _BaseWorkerModelAlgorithm):
            # Recieve the intial parameters here from the Modeller
            model_params = await self._receive_parameters()
        else:
            model_params = None

        # Pass model_params to initialise where we update the parameters
        self.algorithm.initialise(
            datasource=datasource,
            pod_dp=pod_dp,
            pod_identifier=pod_identifier,
            model_params=model_params,
        )

        if pod_vitals:
            pod_vitals.last_task_execution_time = time.time()
        try:
            self.algorithm = cast(_ResultsOnlyDataCompatibleWorker, self.algorithm)
            results = self.algorithm.run(data=datasource)
        except TypeError:
            self.algorithm = cast(_ResultsOnlyDataIncompatibleWorker, self.algorithm)
            results = self.algorithm.run()
        await self.mailbox.send_evaluation_results(results)
        await self.mailbox.get_task_complete_update()


@runtime_checkable
class _ResultsOnlyCompatibleAlgoFactory(_BaseCompatibleAlgoFactory, Protocol):
    """Defines algo factory compatibility."""

    def modeller(self, **kwargs: Any) -> _ResultsOnlyCompatibleModeller:
        """Create a modeller-side algorithm."""
        ...


@runtime_checkable
class _ResultsOnlyCompatibleAlgoFactory_(_ResultsOnlyCompatibleAlgoFactory, Protocol):
    """Defines algo factory compatibility."""

    def worker(
        self, **kwargs: Any
    ) -> Union[_ResultsOnlyDataIncompatibleWorker, _ResultsOnlyDataCompatibleWorker]:
        """Create a worker-side algorithm."""
        ...


@runtime_checkable
class _ResultsOnlyCompatibleModelAlgoFactory(
    _ResultsOnlyCompatibleAlgoFactory, Protocol
):
    """Defines algo factory compatibility."""

    model: Union[DistributedModelProtocol, BitfountModelReference]
    pretrained_file: Optional[Union[str, os.PathLike]] = None

    def worker(
        self, hub: BitfountHub, **kwargs: Any
    ) -> Union[_ResultsOnlyDataIncompatibleWorker, _ResultsOnlyDataCompatibleWorker]:
        """Create a worker-side algorithm."""
        ...


class ResultsOnly(_BaseProtocolFactory):
    """Simply returns the results from the provided algorithm.

    This protocol is the most permissive protocol and only involves one round of
    communication. It simply runs the algorithm on the `Pod`(s) and returns the
    results as a list (one element for every pod).

    Args:
        algorithm: The algorithm to run.

    Attributes:
        name: The name of the protocol.
        algorithm: The algorithm to run. This must be compatible with the `ResultsOnly`
            protocol.

    Raises:
        TypeError: If the `algorithm` is not compatible with the protocol.
    """

    # TODO: [BIT-1047] Consider separating this protocol into two separate protocols
    #       for each algorithm. The algorithms may not be similar enough to benefit
    #       from sharing one protocol.

    algorithm: Union[
        _ResultsOnlyCompatibleAlgoFactory_, _ResultsOnlyCompatibleModelAlgoFactory
    ]
    fields_dict: ClassVar[T_FIELDS_DICT] = {}
    nested_fields: ClassVar[T_NESTED_FIELDS] = {"algorithm": algorithms.registry}

    def __init__(
        self,
        *,
        algorithm: Union[
            _ResultsOnlyCompatibleAlgoFactory_, _ResultsOnlyCompatibleModelAlgoFactory
        ],
        **kwargs: Any,
    ) -> None:
        super().__init__(algorithm=algorithm, **kwargs)

    @classmethod
    def _validate_algorithm(
        cls,
        algorithm: _BaseCompatibleAlgoFactory,
    ) -> None:
        """Checks that `algorithm` is compatible with the protocol."""
        if not isinstance(
            algorithm,
            (
                _ResultsOnlyCompatibleAlgoFactory_,
                _ResultsOnlyCompatibleModelAlgoFactory,
            ),
        ):
            raise TypeError(
                f"The {cls.__name__} protocol does not support "
                + f"the {type(algorithm).__name__} algorithm.",
            )

    def dump(self) -> SerializedProtocol:
        """Returns the JSON-serializable representation of the protocol."""
        return cast(SerializedProtocol, bf_dump(self))

    def modeller(self, mailbox: _ModellerMailbox, **kwargs: Any) -> _ModellerSide:
        """Returns the modeller side of the ResultsOnly protocol."""
        if isinstance(self.algorithm, _ResultsOnlyCompatibleModelAlgoFactory):
            algorithm = self.algorithm.modeller(
                pretrained_file=self.algorithm.pretrained_file
            )
        else:
            algorithm = self.algorithm.modeller()
        return _ModellerSide(
            algorithm=algorithm,
            mailbox=mailbox,
            **kwargs,
        )

    def worker(
        self, mailbox: _WorkerMailbox, hub: BitfountHub, **kwargs: Any
    ) -> _WorkerSide:
        """Returns the worker side of the ResultsOnly protocol."""
        return _WorkerSide(
            algorithm=self.algorithm.worker(hub=hub),
            mailbox=mailbox,
            **kwargs,
        )
