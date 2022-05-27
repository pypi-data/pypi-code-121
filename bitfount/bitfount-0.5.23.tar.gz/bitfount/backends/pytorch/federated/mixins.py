"""PyTorch implementations of the federated learning mixin classes."""
from __future__ import annotations

from abc import ABC
from typing import TYPE_CHECKING, Any, Dict, Mapping, Optional, Sequence, cast

import pytorch_lightning as pl
import torch

from bitfount.backends.pytorch.federated.shim import PyTorchBackendTensorShim
from bitfount.backends.pytorch.types import _AdaptorForPyTorchTensor
from bitfount.federated.mixins import _DistributedModelMixIn
from bitfount.federated.shim import _load_default_tensor_shim
from bitfount.types import (
    T_DTYPE,
    _Residuals,
    _SerializedWeights,
    _TensorLike,
    _Weights,
)

if TYPE_CHECKING:
    from bitfount.backends.pytorch.data.dataloaders import (
        _BasePyTorchBitfountDataLoader,
    )


class _PyTorchDistributedModelMixIn(_DistributedModelMixIn, ABC):
    """PyTorch implementation of the DistributedModelMixIn."""

    epochs: Optional[int]
    steps: Optional[int]
    train_dl: _BasePyTorchBitfountDataLoader
    _pl_trainer: pl.Trainer
    _total_num_batches_trained: int

    def get_param_states(self) -> Dict[str, _TensorLike]:
        """See base class.

        Wrapping the state dictionary with `dict` ensures we return a `dict` rather than
        an `OrderedDict`.
        """
        aux = dict(self._model.state_dict())  # type: ignore[attr-defined] # Reason: _model is initialised in subclass # noqa: B950

        return self._get_torch_adapter_states(aux)

    def _get_torch_tensor_states(
        self, adapted_params: Mapping[str, _TensorLike]
    ) -> Dict[str, torch.Tensor]:
        """Get the tensors out of our adapter."""
        tensor_dict: Dict[str, torch.Tensor] = {}
        for k, v in adapted_params.items():
            if isinstance(v, _AdaptorForPyTorchTensor):
                tensor_dict[k] = v.torchtensor
        return tensor_dict

    def _get_torch_adapter_states(
        self, torch_tensor_params: Mapping[str, torch.Tensor]
    ) -> Dict[str, _TensorLike]:
        """Put tensors in our torch.Tensor adapter."""
        return {k: _AdaptorForPyTorchTensor(v) for k, v in torch_tensor_params.items()}

    def apply_weight_updates(self, weight_updates: Sequence[_Weights]) -> _Weights:
        """See base class."""
        params_to_update_adapted = self.get_param_states()
        params_to_update = self._get_torch_tensor_states(params_to_update_adapted)
        tensor_weight_updates = [
            self._get_torch_tensor_states(params) for params in weight_updates
        ]
        weight = 1 / len(weight_updates)
        for name in tensor_weight_updates[0]:
            params_to_update[name].data.copy_(
                params_to_update[name]
                + torch.stack(
                    [weight * params[name].data for params in tensor_weight_updates],
                    dim=0,
                ).sum(dim=0)
            )
        adapted_params: _Weights = self._get_torch_adapter_states(params_to_update)
        return adapted_params

    def update_params(self, new_model_params: _Weights) -> None:
        """See base class."""
        current_params_adapted = self.get_param_states()
        current_params = self._get_torch_tensor_states(current_params_adapted)
        new_model_params_torch = self._get_torch_tensor_states(new_model_params)
        for name in new_model_params_torch:
            current_params[name].data.copy_(new_model_params_torch[name].data)

    def deserialize_params(self, serialized_weights: _SerializedWeights) -> _Weights:
        """Convert serialized model params to tensors."""
        backend_tensor_shim = cast(
            PyTorchBackendTensorShim, _load_default_tensor_shim()
        )

        weights = {
            name: backend_tensor_shim.to_tensor(param)
            for name, param in serialized_weights.items()
        }

        return weights

    def serialize_params(self, weights: _Weights) -> _SerializedWeights:
        """Serialize model params."""
        backend_tensor_shim = cast(
            PyTorchBackendTensorShim, _load_default_tensor_shim()
        )

        serialized_weights = {
            name: backend_tensor_shim.to_list(param) for name, param in weights.items()
        }

        return serialized_weights

    @staticmethod
    def diff_params(
        old_params: _Weights,
        new_params: _Weights,
    ) -> _Residuals:
        """See base class."""
        old_params_torch: Dict[str, torch.Tensor] = {}
        for k, v in old_params.items():
            if isinstance(v, _AdaptorForPyTorchTensor):
                old_params_torch[k] = v.torchtensor
        new_params_torch: Dict[str, torch.Tensor] = {}
        for k, v in new_params.items():
            if isinstance(v, _AdaptorForPyTorchTensor):
                new_params_torch[k] = v.torchtensor
        for name in new_params:
            old_params_torch[name].data.copy_(
                new_params_torch[name].data - old_params_torch[name].data
            )
        old_params_adapted: _Residuals = {
            k: _AdaptorForPyTorchTensor(v) for k, v in old_params_torch.items()
        }
        return old_params_adapted

    def set_model_training_iterations(self, iterations: int) -> None:
        """See base class."""
        if self.epochs:
            self.epochs = iterations
            if hasattr(self, "_pl_trainer"):
                self._pl_trainer.fit_loop.max_epochs = iterations
        else:
            self.steps = iterations
            if hasattr(self, "_pl_trainer"):
                self._pl_trainer.fit_loop.epoch_loop.max_steps = iterations

    def reset_trainer(self) -> None:
        """See base class."""
        # `trainer_init()` comes from `BasePyTorchModel` or `PyTorchBitfountModel`
        # This is a standard pattern for MixIn classes.
        self._pl_trainer: pl.Trainer = self.trainer_init()  # type: ignore[attr-defined] # Reason: see above. # noqa: B950

        # The `max_epochs` attribute on the trainer does not need to be reset for
        # epochs. This behaviour is only for steps. See pytorch-lightning issue #11425
        if self.steps:
            # `max_steps` must be set to however number of steps we want to train
            # greater than the number of batches already trained
            self._pl_trainer.fit_loop.epoch_loop.max_steps = self.steps + (
                self._total_num_batches_trained % len(self.train_dl)
            )

    def tensor_precision(self) -> T_DTYPE:
        """Returns torch default dtype.

        This is `torch.float32` by default unless changed. This method should be
        overridden in the subclass if the model supports non-32-bit model tensors.
        """
        return cast(T_DTYPE, torch.get_default_dtype())

    def log_(self, name: str, value: Any, **kwargs: Any) -> Any:
        """Simple wrapper around the pytorch lightning `log` method."""
        # Method is present on `BasePyTorchModel` inherited from `pl.LightningModule`.
        self.log(name, value, **kwargs)  # type: ignore[attr-defined] # Reason: see above. # noqa: B950
