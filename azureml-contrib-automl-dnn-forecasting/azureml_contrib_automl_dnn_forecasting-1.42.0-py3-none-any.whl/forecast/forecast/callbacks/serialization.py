"""Creates a checkpoint containing the model state, epoch, and optionally optimizer/other state."""

import os.path as osp
from typing import Any, Optional, Mapping

from overrides import overrides
import torch

from forecast.callbacks.callback import Callback
from forecast.callbacks.utils import CallbackDistributedExecMode


class CheckpointCallback(Callback):
    """Creates a checkpoint containing the model state, epoch, and optionally optimizer/other state."""

    BEST_VAL_CHECKPOINT_FILENAME = "best_val.pt"
    END_TRAIN_CHECKPOINT_FILENAME = "end_of_training.pt"
    MODEL_KEY = "model"
    EPOCH_KEY = "epoch"
    OPTIMIZER_KEY = "optimizer"

    def __init__(
        self,
        checkpoint_epochs: Optional[int],
        out_dir: str,
        include_optim: bool = True,
        ckpt_best_metric: Optional[str] = None,
        minimize_metric: bool = True,
        **kwargs: Any,
    ) -> None:
        """Creates a checkpoint containing the model state, epoch, and optionally optimizer state.

        Parameters
        ----------
        checkpoint_epochs: int
            A checkpoint will be created every `checkpoint_epochs` epochs, None denotes only checkpoint at end of
            training
        out_dir: str
            Checkpoints will be created in this directory
        include_optim: bool, optional
            If True, the optimizer's state will be persisted in the checkpoint. Defaults to True.
        ckpt_best_metric: str, optional
            If specified, checkpoint the best result based on the specified validation metric. Defaults to None.
        minimize_metric: bool, optional
            If log_best_metric is specified, should it be minimized or maximized (defaults to True, minimized).
        kwargs: dict
            A dict of (key, value) paies which will be persisted in the checkpoint with a name of `key` and value of
            `value.state_dict()`.

        """
        super().__init__()
        if checkpoint_epochs is not None and checkpoint_epochs < 1:
            raise ValueError("checkpoint_epochs must either be > 0 or None.")
        self._checkpoint_epochs = checkpoint_epochs
        self._epochs = 0
        self._out_dir = out_dir
        self._include_optim = include_optim
        self._ckpt_best_metric = ckpt_best_metric
        self._minimize_metric = minimize_metric
        self._best_metric_val = float("inf") if minimize_metric else -float("inf")
        self._other_args = kwargs

    @overrides
    def on_val_end(self, epoch: int, loss: float, metrics: Mapping[str, float]) -> None:
        if not self._ckpt_best_metric:
            return

        # self._epochs will be set in on_train_val_epoch_end to same value regardless
        # this early setting ensures the checkpoint has the correct value
        self._epochs = epoch
        metric = loss if self._ckpt_best_metric == "loss" else metrics[self._ckpt_best_metric]
        if (self._minimize_metric and metric < self._best_metric_val) or (
            not self._minimize_metric and metric > self._best_metric_val
        ):
            self._best_metric_val = metric
            self._checkpoint(CheckpointCallback.BEST_VAL_CHECKPOINT_FILENAME)

    @overrides
    def on_train_val_epoch_end(self, epoch: int) -> None:
        """Creates the checkpoint every N epochs.

        Parameters
        ----------
        epoch: int
            The current epoch

        Returns
        -------
        None

        """
        self._epochs = epoch
        if self._checkpoint_epochs is not None and (self._epochs + 1) % self._checkpoint_epochs == 0:
            self._checkpoint(f"epoch_{epoch}.pt")

    @overrides
    def on_train_end(self) -> None:
        """Creates a checkpoint at the end of training.

        Returns
        -------
        None
        """
        self._checkpoint(CheckpointCallback.END_TRAIN_CHECKPOINT_FILENAME)

    def _checkpoint(self, name: str) -> None:
        save_dict = {
            CheckpointCallback.MODEL_KEY: self.model.state_dict(),
            CheckpointCallback.EPOCH_KEY: self._epochs,
        }
        if self._include_optim:
            save_dict[CheckpointCallback.OPTIMIZER_KEY] = self.optimizer.state_dict()
        if self._other_args:
            for k, v in self._other_args.items():
                save_dict[k] = v
        torch.save(save_dict, osp.join(self._out_dir, name))

    @staticmethod
    @overrides
    def get_distributed_exec_mode() -> CallbackDistributedExecMode:
        return CallbackDistributedExecMode.RANK_0
