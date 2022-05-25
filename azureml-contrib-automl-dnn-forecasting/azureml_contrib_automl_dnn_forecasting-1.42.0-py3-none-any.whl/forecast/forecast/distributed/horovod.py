from typing import List, Optional, Sequence

try:
    import horovod.torch as hvd  # type: ignore
except ImportError:
    hvd = None

from overrides import overrides
import torch
from torch.utils.data import BatchSampler, DataLoader, DistributedSampler, RandomSampler, SequentialSampler

from forecast.callbacks import Callback, CallbackDistributedExecMode
from forecast.distributed.base import Communicator, DistributionStrategy


class _HorovodCommunicator:
    def allgather(self, t: torch.Tensor) -> torch.Tensor:
        return hvd.allgather(t)

    def allreduce(self, t: torch.Tensor) -> torch.Tensor:
        return hvd.allreduce(t)


class HorovodDistributionStrategy(DistributionStrategy):
    def __init__(self, *, set_device: bool = True):
        if not hvd:
            raise ImportError("Cannot leverage the HorovodDistributionStrategy if horovod is not installed.")
        if not hvd.is_initialized():
            hvd.init()
        self._communicator = _HorovodCommunicator()
        super().__init__(set_device=set_device)

    def get_callback(self, set_device: bool = True) -> Optional[Callback]:
        return HorovodCallback()

    def filter_callbacks(self, callbacks: Sequence[Callback]) -> List[Callback]:
        rank = self.rank()
        local_rank = self.local_rank()
        out = []
        for cb in callbacks:
            cb_mode = cb.get_distributed_exec_mode()
            if cb_mode is CallbackDistributedExecMode.ALL:
                out.append(cb)
            elif cb_mode is CallbackDistributedExecMode.RANK_0 and rank == 0:
                out.append(cb)
            elif cb_mode is CallbackDistributedExecMode.LOCAL_RANK_0 and local_rank == 0:
                out.append(cb)
            elif cb_mode is CallbackDistributedExecMode.INCOMPATIBLE:
                raise ValueError(f"Cannot run callback of type {type(cb)} in a distributed setting via Horovod.")
        return out

    def size(self) -> int:
        return hvd.size()

    def rank(self) -> int:
        return hvd.rank()

    def local_rank(self) -> int:
        return hvd.local_rank()

    @property
    def communicator(self) -> Communicator:
        return self._communicator


class HorovodCallback(Callback):
    """Injects distributed training into the forecaster via horovod."""

    def __init__(self) -> None:
        """Creates a callback which integrate horovod into Forecaster training."""
        super().__init__()
        if not hvd:
            raise ImportError("Horovod is not installed and thus cannot instantiate a HorovodCallback")

    @overrides
    def on_train_begin(self) -> None:
        """Prepares model and optimizer for horovod-enabled training.

        Returns
        -------
        None
        """
        if not self.model:
            raise RuntimeError("Training began before setting model for callback.")

        # ensure that all references to parameters in the optimizer point to the model
        # combined with the check below ,this is currently the best method of ensuring that the distribution strategy
        # pinned the correct GPU before the optimizer was created
        model_params = set(self.model.parameters())
        opt_params = set()
        for pg in self.optimizer.param_groups:
            if isinstance(pg["params"], torch.Tensor):
                opt_params.add(pg["params"])
            else:
                opt_params.update(pg["params"])
        if not opt_params.issubset(model_params):
            raise RuntimeError(
                "All optimizer parameters must be present in the model."
                "Did you remember to instantiate the distribution strategy before creating the model/optimizer?"
            )

        # check to ensure all optimizer params are either on the model's GPU(s) or 0-dim on the CPU
        model_devices = {t_.device for t_ in model_params}
        for t_ in self.optimizer.state_dict().values():
            if isinstance(t_, torch.Tensor):
                if t_.device not in model_devices and not (t_.device.type == "cpu" and t_.ndim == 0):
                    raise RuntimeError(
                        "All optimizer state must be on the correct device. "
                        "Did you remember to instantiate the distribution strategy before creating the model/optimizer?"
                    )

        # do we already have a horovod optimizer (i.e., should we patch the optimizer & update the LR?)
        # important to check in case the
        if not hasattr(self.optimizer, "synchronize") or not hasattr(self.optimizer, "_should_synchronize"):
            # explicitly test for the presence of _should_synchronize since it's internal
            # and we don't want to unintentionally break when upgrading to a new version

            # scale the learning rate
            for pg in self.optimizer.param_groups:
                pg["lr"] *= hvd.size()

            # wrap the optimizer
            self.forecaster.optimizer = hvd.DistributedOptimizer(self.optimizer)

        # if we don't already have a distributed sampler, recreate the training dataloader
        # for now at least, we don't shard the validation dataloader as it simplifies some callbacks
        dl = self.forecaster.dataloader_train
        assert dl is not None
        sampler = dl.sampler
        if not isinstance(sampler, DistributedSampler):
            if isinstance(dl.batch_sampler, BatchSampler):
                sampler = dl.batch_sampler.sampler
                if isinstance(sampler, RandomSampler):
                    shuffle = True
                elif isinstance(sampler, SequentialSampler):
                    shuffle = False
                else:
                    raise ValueError("Horovod callback only supports default sampler types.")
                batch_size = dl.batch_sampler.batch_size
                drop_last = dl.batch_sampler.drop_last
            else:
                raise ValueError("Horovod callback only supports the default batch sampler.")

            self.forecaster.dataloader_train = DataLoader(
                dataset=dl.dataset,
                batch_size=batch_size,
                sampler=DistributedSampler(
                    dataset=dl.dataset,
                    num_replicas=hvd.size(),
                    rank=hvd.rank(),
                    shuffle=shuffle,
                    drop_last=drop_last,
                ),
                num_workers=dl.num_workers,
                collate_fn=dl.collate_fn,
                pin_memory=dl.pin_memory,
                drop_last=drop_last,
                timeout=dl.timeout,
                worker_init_fn=dl.worker_init_fn,
                multiprocessing_context=dl.multiprocessing_context,
                generator=dl.generator,
                prefetch_factor=dl.prefetch_factor,
                persistent_workers=dl.persistent_workers,
            )

        # broadcast the state
        hvd.broadcast_parameters(self.model.state_dict(), root_rank=0)
        hvd.broadcast_optimizer_state(self.optimizer, root_rank=0)

    @overrides
    def on_train_epoch_begin(self, epoch: int) -> None:
        assert self.forecaster.dataloader_train is not None
        assert hasattr(self.forecaster.dataloader_train.sampler, "set_epoch"), "DistributedSampler required for Horovod"
        self.forecaster.dataloader_train.sampler.set_epoch(epoch)  # type: ignore

    @overrides
    def on_train_batch_before_unscale(self) -> None:
        """Syncs before step to play nice with torch-native AMP."""
        # failure to explicitly sync will cause horovod to throw an error if zero_grad is called before step
        # (this happens when AMP needs to adjust the scale factor)
        # we explicitly tell the optimize to not sync during step as ew have done so manually
        #
        # this is not an issue if we throw an OOM error and halve the batch size as we'll manually sync again
        # and manual syncs are not impacted by the _should_synchronize flag
        self.optimizer.synchronize()  # type: ignore
        assert hasattr(self.optimizer, "_should_synchronize"), "A Horovod optimizer is required."
        self.optimizer._should_synchronize = False  # type: ignore

    @overrides
    def on_train_batch_end(self, epoch: int, batch: int, loss: float) -> None:
        """Indicate we finished our step."""
        assert hasattr(self.optimizer, "_should_synchronize"), "A Horovod optimizer is required."
        self.optimizer._should_synchronize = True  # type: ignore

    @staticmethod
    @overrides
    def get_distributed_exec_mode() -> CallbackDistributedExecMode:
        return CallbackDistributedExecMode.ALL
