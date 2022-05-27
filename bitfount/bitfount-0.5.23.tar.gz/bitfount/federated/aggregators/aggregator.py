"""Vanilla model parameter aggregators for Federated Averaging."""
from __future__ import annotations

from typing import Any, ClassVar, Iterable, List, Mapping, Optional, Union

import numpy as np

from bitfount.federated.aggregators.base import (
    _AggregatorWorkerFactory,
    _BaseAggregatorFactory,
    _BaseModellerAggregator,
    _BaseWorkerAggregator,
)
from bitfount.federated.exceptions import AggregatorError
from bitfount.federated.shim import BackendTensorShim, _load_default_tensor_shim
from bitfount.types import (
    T_DTYPE,
    T_FIELDS_DICT,
    T_NESTED_FIELDS,
    _SerializedWeights,
    _Weights,
)


class _ModellerSide(_BaseModellerAggregator[T_DTYPE]):
    """Modeller-side of the vanilla aggregator."""

    def __init__(
        self,
        *,
        tensor_shim: BackendTensorShim,
        weights: Optional[Mapping[str, Union[float, int]]] = None,
        **kwargs: Any,
    ):
        """Create a new modeller-side instance of the vanilla aggregator.

        Args:
            tensor_shim: A shim providing methods to convert to/from
                tensor-like objects.
            weights: A mapping of pod identifiers to the desired weighting to give
                them in the averaging. If not supplied, all will be equally weighted.
                Weights will be normalised so that they sum to 1.0.
            **kwargs: Other keyword arguments.
        """
        super().__init__(tensor_shim=tensor_shim, **kwargs)
        self._weights: Optional[Mapping[str, float]] = self._normalise_weights(weights)

    @property
    def weights(self) -> Optional[Mapping[str, float]]:
        """The per-pod update weights for this aggregator.

        None if no weights were specified.
        """
        if self._weights:
            return dict(self._weights)
        else:
            return None

    @staticmethod
    def _normalise_weights(
        weights: Optional[Mapping[str, Union[float, int]]]
    ) -> Optional[Mapping[str, float]]:
        """Normalises the supplied weights to sum to 1.0.

        If no weights supplied, returns None.
        """
        if not weights:
            return None

        weight_sum = sum(weights.values())
        return {pod_id: weight / weight_sum for pod_id, weight in weights.items()}

    def run(
        self,
        parameter_updates: Mapping[str, _SerializedWeights],
        tensor_dtype: Optional[T_DTYPE] = None,
        **kwargs: Any,
    ) -> _Weights:
        """Averages parameters, converts to tensors and return them."""
        # Use provided weights or, if none provided, use equal weights.
        weights = self._get_weights(parameter_updates)

        average_update = {}
        for param_name in self._extract_param_names(parameter_updates.values()):
            average_update[param_name] = self._tensor_shim.to_tensor(
                np.stack(
                    [
                        weights[pod_id] * np.asarray(params[param_name])
                        for pod_id, params in parameter_updates.items()
                    ],
                    axis=0,
                ).sum(axis=0),
                dtype=tensor_dtype,
            )
        return average_update

    def _get_weights(
        self, parameter_updates: Mapping[str, _SerializedWeights]
    ) -> Mapping[str, float]:
        """Gets the supplied weights or creates equal weights.

        Will raise appropriate errors if the pods in the supplied weights and
        the pods in the parameter updates don't match.
        """
        weights = self.weights

        if weights is None:
            # Use equal weights
            weights = {
                pod_id: 1 / len(parameter_updates)
                for pod_id in parameter_updates.keys()
            }
        else:
            # If using provided weights, check we have updates for each pod
            parameter_update_pods = set(parameter_updates.keys())
            weights_pods = set(weights.keys())

            extra_in_update = parameter_update_pods.difference(weights_pods)
            missing_in_update = weights_pods.difference(parameter_updates)

            if extra_in_update:
                raise AggregatorError(
                    f"Aggregation weightings provided but found updates from "
                    f"unweighted pods in received parameter updates: "
                    f"{';'.join(extra_in_update)}"
                )
            if missing_in_update:
                raise AggregatorError(
                    f"Aggregation weightings provided but missing updates from "
                    f"expected pods in received parameter updates: "
                    f"{';'.join(missing_in_update)}"
                )

        return weights

    @staticmethod
    def _extract_param_names(param_updates: Iterable[_SerializedWeights]) -> List[str]:
        """Extracts the parameter names from the updates.

        Will throw an exception if the parameter names differ between the
        supplied updates.
        """
        # Get expected parameter names from first update
        param_updates_iter = iter(param_updates)
        first = next(param_updates_iter)
        param_names = first.keys()

        # Check that these are the same in all others
        if not all(param_names == other.keys() for other in param_updates_iter):
            raise AggregatorError(
                f"Parameter names are not consistent between updates: "
                f"all updates should match {set(param_names)}"
            )

        return list(param_names)


class _WorkerSide(_BaseWorkerAggregator):
    """Worker-side of the vanilla aggregator."""

    def __init__(self, *, tensor_shim: BackendTensorShim, **kwargs: Any):
        super().__init__(tensor_shim=tensor_shim, **kwargs)

    async def run(
        self, parameter_update: _Weights, **kwargs: Any
    ) -> _SerializedWeights:
        """Converts tensors to list of floats and returns them."""
        serialized_params = {
            name: self._tensor_shim.to_list(param)
            for name, param in parameter_update.items()
        }

        return serialized_params


class Aggregator(_BaseAggregatorFactory, _AggregatorWorkerFactory):
    """Vanilla model parameter aggregator for Federated Averaging.

    Performs simple arithmetic mean of unencrypted model parameters.

    Args:
        tensor_shim: The tensor shim to use to perform operations on backend tensors
            of the appropriate type. The `backend_tensor_shim` method on the model
            can be called to get this shim.

    Attributes:
        name: The name of the aggregator.

    :::danger

    This aggregator is not secure. Parameter updates are shared with participants in an
    unencrypted manner. It is not recommended to use this aggregator in a zero-trust
    setting.

    :::
    """

    fields_dict: ClassVar[T_FIELDS_DICT] = {}
    nested_fields: ClassVar[T_NESTED_FIELDS] = {}

    def __init__(self, **kwargs: Any):
        super().__init__(**kwargs)
        self._tensor_shim = _load_default_tensor_shim()

    def modeller(self, **kwargs: Any) -> _ModellerSide:
        """Returns the modeller side of the Aggregator."""
        return _ModellerSide(tensor_shim=self._tensor_shim, **kwargs)

    def worker(self, **kwargs: Any) -> _WorkerSide:
        """Returns the worker side of the Aggregator."""
        return _WorkerSide(tensor_shim=self._tensor_shim, **kwargs)
