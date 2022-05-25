import warnings
from functools import partial
from concurrent.futures import ThreadPoolExecutor
from copy import deepcopy
from pathlib import Path
from typing import Dict, Iterable, TYPE_CHECKING, Optional, List
import shutil
import numpy as np
import torch as T
from torch.optim import lr_scheduler
from torch import profiler
from torch.nn.utils import clip_grad_norm_
from torch.optim.swa_utils import SWALR, AveragedModel, update_bn
from torch.nn.parallel import DistributedDataParallel
from torch.utils.tensorboard import SummaryWriter
from ..misc.misc import Stage, safe_type_cast

# deal with cyclic imports
# reference: https://stackoverflow.com/questions/63234592/python-type-hints-with-imported-class-methods
if TYPE_CHECKING:
    from ..learner import Learner


class BaseCallback:
    def __init__(self):
        self.learner: Optional["Learner"] = None
        self.params = {}

    def set_model(self, learner: "Learner"):
        self.learner = learner

    def set_params(self, params: Dict):
        for k, v in params.items():
            if k in self.__dict__:
                self.__dict__[k] = v

    def on_epoch_begin(self, training_log, validation_log):
        pass

    def on_epoch_end(self, training_log, validation_log):
        pass

    def on_train_begin(self, **kwargs):
        pass

    def on_train_end(self, training_log, validation_log):
        pass

    def on_batch_begin(self, stage, epoch, idx, niter, batch_data, training_log, validation_log):
        pass

    def on_batch_end(self, stage, epoch, idx, niter, metrics, training_log, validation_log):
        pass

    def after_backward(self):
        pass


class CallbackList(BaseCallback):
    def __init__(self, callbacks):
        super().__init__()
        assert isinstance(callbacks, Iterable)
        self.callbacks = callbacks

    def set_model(self, learner):
        for cbk in self.callbacks:
            cbk.set_model(learner)

    def set_params(self, params):
        for cbk in self.callbacks:
            cbk.set_params(params)

    def on_epoch_begin(self, training_log, validation_log):
        for cbk in self.callbacks:
            cbk.on_epoch_begin(training_log, validation_log)

    def on_epoch_end(self, training_log, validation_log):
        for cbk in self.callbacks:
            cbk.on_epoch_end(training_log, validation_log)

    def on_train_begin(self, **kwargs):
        for cbk in self.callbacks:
            cbk.on_train_begin(**kwargs)

    def on_train_end(self, training_log, validation_log):
        for cbk in self.callbacks:
            cbk.on_train_end(training_log, validation_log)

    def on_batch_begin(self, stage, epoch, idx, niter, batch_data, training_log, validation_log):
        for cbk in self.callbacks:
            cbk.on_batch_begin(stage, epoch, idx, niter, batch_data, training_log, validation_log)

    def on_batch_end(self, stage, epoch, idx, niter, metrics, training_log, validation_log):
        for cbk in self.callbacks:
            cbk.on_batch_end(stage, epoch, idx, niter, metrics, training_log, validation_log)

    def after_backward(self):
        for cbk in self.callbacks:
            cbk.after_backward()

    def __iter__(self):
        return iter(self.callbacks)

    def __next__(self):
        return next(self)


class ReduceLROnPlateau(BaseCallback):
    def __init__(self, monitor='val_loss', mode='min', factor=0.1, patience=10, verbose=False, threshold=1e-4,
                 threshold_mode='rel', cooldown=0, min_lr=0, eps=1e-8):
        super().__init__()
        self.monitor = monitor
        self.schedule = None
        self.__schdule_fn = partial(lr_scheduler.ReduceLROnPlateau, mode=mode, factor=factor, patience=patience,
                 verbose=verbose, threshold=threshold, threshold_mode=threshold_mode,
                 cooldown=cooldown, min_lr=min_lr, eps=eps)

    def on_train_begin(self, **kwargs):
        super().on_train_begin(**kwargs)
        self.schedule = self.__schdule_fn(kwargs['optimizer'])

    def on_epoch_end(self, training_log, validation_log):
        cur_log = training_log[-1]
        if validation_log:
            cur_log.update(validation_log[-1])
        self.schedule.step(cur_log[self.monitor])


class CosineAnnealingWarmRestarts(BaseCallback):
    """
    Adjust the learning rate after each iteration (batch).
    Args:
        T_0 (int): The half of the number of steps between the lr falls down from maximum to minimum. Same as torch.
        T_mult (int, optional): Same as torch. Defaults to 1.
        eta_min (int, optional): Same as torch. Defaults to 0.
        last_epoch (int, optional): Same as torch. Defaults to -1.
        verbose (bool, optional): Same as torch. Defaults to False.
    """
    def __init__(self, T_0, T_mult=1, eta_min=0, last_epoch=-1, verbose=False):
        super().__init__()
        self.T_0 = T_0
        self.T_mult = T_mult
        self.eta_min = eta_min
        self.last_epoch = last_epoch
        self.verbose = verbose
        self.sch = None

    def on_train_begin(self, **kwargs):
        super().on_train_begin(**kwargs)
        self.sch = lr_scheduler.CosineAnnealingWarmRestarts(kwargs['optimizer'], self.T_0, self.T_mult, self.eta_min, self.last_epoch, self.verbose)

    def on_batch_end(self, stage, epoch, idx, niter, metrics, training_log, validation_log):
        if stage != Stage.TRAIN:
            return
        self.sch.step(epoch + idx / niter)


class CosineAnnealingLR(BaseCallback):
    def __init__(self, T_max, eta_min=0, last_epoch=-1, verbose=False):
        super().__init__()
        self.T_max = T_max
        self.eta_min = eta_min
        self.last_epoch = last_epoch
        self.verbose = verbose
        self.sch = None

    def on_train_begin(self, **kwargs):
        super().on_train_begin(**kwargs)
        self.sch = lr_scheduler.CosineAnnealingLR(kwargs['optimizer'], self.T_max, self.eta_min, self.last_epoch, self.verbose)

    def on_batch_end(self, stage, epoch, idx, niter, metrics, training_log, validation_log):
        if stage != Stage.TRAIN:
            return
        self.sch.step()


class StochasticWeightAveraging(BaseCallback):
    """StochasticWeightAveraging

    Args:
        swa_lr (float): [description]
        filepath (str, optional): The path to save the swa model checkpoint, will be overwritten.
        swa_start (int, optional): Begin record weights and adjust lr using `SWALR` at the end of the `#swa_start`-th epoch. Defaults to 1.
        anneal_epochs (int, optional): [description]. Defaults to 10.
        anneal_strategy (str, optional): [description]. Defaults to 'cos'.
        last_epoch (int, optional): [description]. Defaults to -1.
        device (str, optional): [description]. Defaults to None.
        avg_fn (Callable, optional): [description]. Defaults to None.

    Usage:
        ```
        opt = ...
        module = ...
        model = DistributedDataParallel(module)  # optional.
        Learner(..., callback=[StochasticWeightAveraging()]).fit()
        ```

    Reference:
        https://gist.github.com/sayakpaul/97e20e0a18a03f8c960b57a59188bd8b

    Notes:
        When using lr scheduler, like CosineAnnealingLR, you may need to override `on_batch_end` to avoid scheduler adjusts the learning rate after swa begin.
    """
    def __init__(self, swa_lr, savepath=None, swa_start=1, anneal_epochs=10, anneal_strategy='cos', last_epoch=-1, device=None, avg_fn=None, verbose=False):
        super().__init__()
        self.swa_lr = swa_lr
        self.savepath = savepath
        self.swa_start = swa_start
        self.anneal_epochs = anneal_epochs
        self.anneal_strategy = anneal_strategy
        self.last_epoch = last_epoch
        self.device = device
        self.avg_fn = avg_fn
        self.verbose = verbose
        self.swa_sch = None
        self.swa_model = None
        self.async_saver = ThreadPoolExecutor(1)

    def _save_checkpoint(self):
        if self.local_rank:
            return
        if self.savepath:
            m = self.swa_model.module
            if isinstance(m, DistributedDataParallel):
                m = m.module
            p = Path(self.savepath)
            p.parent.mkdir(parents=True, exist_ok=True)
            T.save(m.state_dict(), self.savepath)
            if self.verbose:
                print(f"Save averaged model to: {p}. last learning rate: {self.swa_sch.get_last_lr()}")

    def on_train_begin(self, **kwargs):
        super().on_train_begin(**kwargs)
        self.local_rank = kwargs.get('local_rank')
        self.swa_sch = SWALR(kwargs['optimizer'], self.swa_lr, self.anneal_epochs, self.anneal_strategy, self.last_epoch)
        self.swa_model = AveragedModel(self.learner.module, self.device, self.avg_fn)

    def on_epoch_end(self, training_log, validation_log):
        nepochs = len(training_log)
        if nepochs >= self.swa_start:
            self.swa_model.update_parameters(self.learner.module)
            self.swa_sch.step()
            self.async_saver.submit(self._save_checkpoint)

    def on_train_end(self, training_log, validation_log):
        update_bn(self.learner.train_ld, self.swa_model)
        self.async_saver.shutdown()


class EarlyStopping(BaseCallback):
    def __init__(self, monitor='val_loss', patience=1, mode='min', verbose=False, restore_best_weights=True):
        super().__init__()
        self.monitor = monitor
        self.patience = patience
        self.mode = mode
        self.epoch = -1
        self.verbose = verbose
        self.restore_best_weights = restore_best_weights
        self.best_model = None
        if mode == 'min':
            self.monitor_op = np.less
            self.best = np.Inf
        elif mode == 'max':
            self.monitor_op = np.greater
            self.best = -np.Inf

    def on_epoch_end(self, training_log, validation_log):
        cur_log = training_log[-1]
        if validation_log:
            cur_log.update(validation_log[-1])
        if self.monitor not in cur_log:
            warnings.warn(f'{self.monitor} is not available, skipping earlystop checking.', RuntimeWarning)
            return
        if self.monitor_op(cur_log[self.monitor], self.best):
            self.best = cur_log[self.monitor]
            self.epoch = len(training_log)
            if self.best_model:
                del self.best_model
            self.best_model = deepcopy(self.learner.module.state_dict())
            if self.verbose:
                print(f'New milestone: {self.best} at Epoch {self.epoch}')
        else:
            if len(training_log) - self.epoch > self.patience:
                self.learner.stop_training = True
                if self.verbose:
                    print("Early stopping")

    def on_train_end(self, training_log, validation_log):
        self.learner.best_epoch = self.epoch
        if self.restore_best_weights and self.best_model:
            self.learner.module.load_state_dict(self.best_model)
            if self.verbose:
                print('Restored from best model.')


class ModelCheckpoint(BaseCallback):
    """Save the model after every epoch.
    `filepath` can contain named formatting options,
    which will be filled the value of `epoch` and
    keys in `logs` (passed in `on_epoch_end`).
    For example: if `filepath` is `weights.{epoch:02d}-{val_loss:.2f}.hdf5`,
    then the model checkpoints will be saved with the epoch number and
    the validation loss in the filename.
    Args:
        filepath: string, path to save the model file. could include format placeholders passwd by log.
                  e.g. model_{epoch}_{val_loss}.pt
        monitor: quantity to monitor.
        verbose: verbosity mode, bool.
        save_best_only: if `save_best_only=True`,
            the latest best model according to
            the quantity monitored will not be overwritten.
        mode: one of {min, max}.
        period: Interval (number of epochs) between checkpoints.
    """

    def __init__(self, filepath: str, monitor='val_loss', verbose=False, save_best_only=True, mode='min', period=1):
        super(ModelCheckpoint, self).__init__()
        self.monitor = monitor
        self.verbose = verbose
        self.filepath = filepath
        self.save_best_only = save_best_only
        self.period = period
        self.epochs_since_last_save = 0
        self.last_save_file = None
        self.best_file = None
        self.local_rank = None
        self.async_saver = ThreadPoolExecutor(1)
        if mode == 'min':
            self.monitor_op = np.less
            self.best = np.Inf
        elif mode == 'max':
            self.monitor_op = np.greater
            self.best = -np.Inf
    
    def _save(self, filepath, remove_old):
        if remove_old:
            if self.last_save_file is not None and self.last_save_file.exists():
                self.last_save_file.unlink()
        self.learner.save(filepath)
        self.last_save_file = Path(filepath)        

    def on_train_begin(self, **kwargs):
        super().on_train_begin(**kwargs)
        self.local_rank = kwargs.get('local_rank')

    def on_epoch_end(self, training_log, validation_log):
        # only write on `local_rank==0` prcess.
        if self.local_rank:
            return
        logs = training_log[-1]
        if validation_log:
            logs.update(validation_log[-1])
        epoch = len(training_log)
        self.epochs_since_last_save += 1
        if self.epochs_since_last_save >= self.period:
            self.epochs_since_last_save = 0
            filepath = self.filepath.format(**logs)
            if self.save_best_only:
                current = logs.get(self.monitor)
                if current is None:
                    warnings.warn(f'Can save best model only with {self.monitor} available, skipping.', RuntimeWarning)
                else:
                    if self.monitor_op(current, self.best):
                        if self.verbose:
                            print(f'Epoch {epoch:05d}: {self.monitor} improved from {self.best:0.5f} to {current:0.5f}, saving model to {filepath}')
                        self.best = current
                        self.async_saver.submit(self._save, filepath, True)
                    else:
                        if self.verbose:
                            print(f'Epoch {epoch:05d}: {self.monitor} did not improve')
            else:
                if self.verbose:
                    print(f'Epoch {epoch:05d}: saving model to {filepath}')
                self.async_saver.submit(self._save, filepath, False)

    def on_train_end(self, training_log, validation_log):
        self.async_saver.shutdown()


class TensorBoard(BaseCallback):
    def __init__(self, logdir: str, batch: Optional[List[str]] = None, epoch: Optional[Dict[str, List[str]]] = None, batch_freq: int = 1, epoch_freq: int = 1, remove_existing=True):
        """Draw metrics to TensorBoard.

        Args:
            logdir (str): tb folder
            batch (Optional[List[str]], optional): The metric names need to be recorded at the end of each batch. Defaults to None.
            epoch (Optional[Dict[str, List[str]]], optional): The metric names need to be recorded at the end of each epoch. Key is the common tag, value is a list of metrics. Defaults to None.
            batch_freq (int, optional): The number of steps between records. Defaults to 1.
            epoch_freq (int, optional): The number of epochs between records. Defaults to 1.
            remove_existing (bool, optional): Wheather remove the older logdir. Defaults to True.
        
        Notes:
            batch metrics are drawn to seperate plots, while epoch metrics are drawn to one figure, grouped by a common tag. The tag specified by the keys of 
            `epoch` params.
        """
        super().__init__()
        self.logdir = logdir
        self.batch = batch
        self.epoch = epoch
        self.batch_freq = batch_freq
        self.epoch_freq = epoch_freq
        self.writer = None
        self.local_rank = None
        self.nbatch = 0
        self.nepoch = 0
        self.remove_existing = remove_existing

    def on_train_begin(self, **kwargs):
        super().on_train_begin(**kwargs)
        if self.remove_existing:
            shutil.rmtree(self.logdir, ignore_errors=True)
        #Path(self.logdir).mkdir(parents=True, exist_ok=True)
        self.writer = SummaryWriter(self.logdir)
        self.local_rank = kwargs.get('local_rank')

    def on_batch_end(self, stage, epoch, idx, niter, metrics, training_log, validation_log):
        # k 折模型用同一个 log_dir，如何区分同一个 monitor: fit 的 metrics参数需要传入 k_i
        # DDP只需要 local_rank==0的进程写。
        # metrics, dict: 只包含 train 异或 validation 上的结果。
        # todo: global_step?
        if self.local_rank or not self.batch:
            return
        self.nbatch += 1
        if self.nbatch == self.batch_freq:
            self.nbatch = 0
            for k in self.batch:
                if k in metrics:
                    f = safe_type_cast(float, metrics[k])
                    if f is not None:
                        self.writer.add_scalar(k, f, global_step=epoch*niter + idx)

    def on_epoch_end(self, training_log, validation_log):
        if self.local_rank or not self.epoch:
            return
        self.nepoch += 1
        if self.nepoch == self.epoch_freq:
            self.nepoch = 0
            logs = training_log[-1]
            if validation_log:
                logs.update(validation_log[-1])
            for tag, keys in self.epoch.items():
                d = {k: safe_type_cast(float, logs[k]) for k in keys if k in logs}
                self.writer.add_scalars(tag, {k: v for k, v in d.items() if v is not None}, global_step=len(training_log))


class GradClipper(BaseCallback):
    def __init__(self, max_norm):
        super().__init__()
        self.max_norm = max_norm

    def after_backward(self):
        clip_grad_norm_(self.learner.module.parameters(), self.max_norm)


class TorchProfile(BaseCallback):
    def __init__(self, activities=None, schedule=None, on_trace_ready=None, record_shapes=False, profile_memory=False, with_stack=False, with_flops=False, with_modules=False):
        super().__init__()
        self.activities = activities
        self.schedule = schedule
        self.on_trace_ready = on_trace_ready
        self.record_shapes = record_shapes
        self.profile_memory = profile_memory
        self.with_stack = with_stack
        self.with_flops = with_flops
        self.with_modules = with_modules
        self.profiler = None

    def on_train_begin(self, **kwargs):
        self.profiler = profiler.profile(
            activities=self.activities,
            schedule=self.schedule,
            on_trace_ready=self.on_trace_ready,
            record_shapes=self.record_shapes,
            profile_memory=self.profile_memory,
            with_stack=self.with_stack,
            with_flops=self.with_flops,
            with_modules=self.with_modules,
        )
        self.profiler.start()

    def on_train_end(self, training_log, validation_log):
        if self.profiler:
            self.profiler.stop()

    def on_batch_end(self, stage, epoch, idx, niter, metrics, training_log, validation_log):
        self.profiler.step()
