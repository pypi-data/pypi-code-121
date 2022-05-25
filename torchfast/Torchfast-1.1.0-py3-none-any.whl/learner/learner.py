import inspect as isp
import sys
from collections import defaultdict

from functools import partial
from pathlib import Path
from typing import Optional, Union, List, Tuple, Iterable, Sequence

import numpy as np
import pandas as pd
import torch as T
from torch import distributed
from torch.nn.parallel import DistributedDataParallel
from torch.utils.data import DataLoader, Dataset, TensorDataset, SubsetRandomSampler, random_split
from torch.utils.data.distributed import DistributedSampler
from torch.optim.swa_utils import AveragedModel
from torch.cuda import amp as torchamp
from tqdm import tqdm
from warnings import warn

from ..callbacks import CallbackList, BaseCallback
from ..data import DistributedSamplerWrapper, TensorDataLoader, SubsetSequentialSampler
from ..misc.misc import seed_everything, Stage, all_reduce_mean
from ..metrics.metrics import BaseMeter, LambdaAverageMeter


class Learner:
    __LOCAL_RANK = None

    @classmethod
    def init_distributed_training(cls, dummy=False, seed=None):
        if not dummy:
            if cls.__LOCAL_RANK is None:
                import os
                local_rank = int(os.environ['LOCAL_RANK'])
                T.cuda.set_device(local_rank)
                seed_everything(seed)
                distributed.init_process_group(backend='nccl')
                cls.__LOCAL_RANK = local_rank
            return cls.__LOCAL_RANK
        else:
            return 0

    @classmethod
    def _make_dataset(cls, dataset) -> Dataset:
        if isinstance(dataset, Dataset):
            pass
        elif isinstance(dataset, (np.ndarray, T.Tensor)):
            dataset = TensorDataset(T.tensor(dataset))
        elif isinstance(dataset, Iterable):
            dataset = TensorDataset(*[T.tensor(a) for a in dataset])
        else:
            raise NotImplementedError(f'Unsported dataset of type: {type(dataset)}.')
        return dataset

    @classmethod
    def _make_dataloader(cls, dataset, batch_size, **kwargs) -> Union[DataLoader, TensorDataLoader]:
        if isinstance(dataset, (DataLoader, TensorDataLoader)):
            return dataset
        prefer_tensorloader = kwargs.get('prefer_tensorloader', True)
        tdl_init_params = isp.signature(TensorDataLoader.__init__).parameters
        dl_init_params = isp.signature(DataLoader.__init__).parameters
        if prefer_tensorloader and all(k in tdl_init_params or k not in dl_init_params for k in kwargs if k not in ('self', 'kwargs', 'batch_size')):
            dl_kwargs = {k: v for k, v in kwargs.items() if k not in ('self', 'kwargs', 'batch_size') and k in tdl_init_params}
            if isinstance(dataset, (np.ndarray, T.Tensor)):
                return TensorDataLoader(dataset, batch_size=batch_size, **dl_kwargs)
            elif isinstance(dataset, Iterable):
                return TensorDataLoader(*dataset, batch_size=batch_size, **dl_kwargs)
            else:
                pass
        dataset = cls._make_dataset(dataset)
        dl_kwargs = {k: v for k, v in kwargs.items() if k not in ('self', 'kwargs', 'batch_size') and k in dl_init_params}
        if cls.__LOCAL_RANK is not None and '__INFERENCE__' not in kwargs:
            if 'sampler' not in dl_kwargs:
                dl_kwargs['sampler'] = DistributedSampler(dataset)
            else:
                if not isinstance(dl_kwargs['sampler'], DistributedSampler):
                    dl_kwargs['sampler'] = DistributedSamplerWrapper(dl_kwargs['sampler'])
        return DataLoader(dataset, batch_size=batch_size, **dl_kwargs)

    @classmethod
    def _move_batch_to_device(cls, batch, device):
        # list or tuple of `Tensor`;
        # single `Tensor` or `np.ndarray`.
        if isinstance(batch, (tuple, list)):
            batch = [c.to(device, non_blocking=True) for c in batch]
        elif isinstance(batch, T.Tensor):
            batch = [batch.to(device, non_blocking=True)]
        elif isinstance(batch, np.ndarray):
            batch = [T.tensor(batch, device=device)]
        else:
            raise NotImplementedError
        return batch

    def __init__(self, module, optimizer_fn=None, loss_fn=None, amp=False):
        """
        :param module:
        :param optimizer_fn: callable or optim instance.
        :param loss_fn: callable (including loss instance), list of callable for multi-target module, or None.
                if loss_fn is a list, the last `len(loss_fn)` components of `training_set` will be considered as
                labels respectively. Besides, `len(loss_fn)` must equal to the number of the module output. and the
                final loss is simply summed. If `loss_fn` is None, you must override `compute_losses` function for
                training.
        :param swa: whether support stochastic weight averaging. If set True, `module` cannot be a `AveragedModel` instance, Fasttorch will wrapper that for you.
        :param avg_fn: will pass to `AveragedModel`. ignored if `swa` is False.
        :param amp: whether to enable Automatic Mixed Precision. if set `True`, the learner should use cuda devices.
        """
        self.module = module
        self.optimizer_fn = optimizer_fn
        self.loss_fn = loss_fn
        self.amp = amp
        self.stop_training = False
        self.train_ld = self.val_ld = None
        self.nloss = None
        self.validation_logging = []
        self.training_logging = []
        self.opt = None
        #self.callbacks = []
        self.scaler = None

    def _iter_one_batch(self, stage, batch, metrics, callbacks, return_output=False):
        with torchamp.autocast(enabled=self.amp):
            res = self.compute_forward(batch, stage)
            if not isinstance(res, tuple):
                res = (res,)
            if stage != Stage.INFERENCE:
                loss = self.compute_losses(res, batch)

        if stage != Stage.INFERENCE:
            if stage == Stage.TRAIN:
                self.opt.zero_grad()
                self.scaler.scale(loss).backward()
                if callbacks:
                    callbacks.after_backward()
                self.scaler.step(self.opt)
                self.scaler.update()
            output = None
            if metrics or return_output:
                detached = tuple(x.detach() for x in res)
                if metrics:
                    for j in range(len(metrics)):
                        self.compute_metric(*metrics[j], detached, batch)
                if return_output:
                    output = self.compute_output(detached, batch)
            return loss, output
        else:
            return self.compute_output(res, batch)

    def _walk_through_data(self, stage, dataloader, cur_epoch, total_epochs, metrics, callbacks, device, verbose, return_output):
        assert stage in (Stage.TRAIN, Stage.VALIDATION)
        prev_grad_enabled = T.is_grad_enabled()
        if stage == Stage.TRAIN:
            self.module.train()
            log_prefix = ''
            T.set_grad_enabled(True)
        else:
            self.module.eval()
            log_prefix = 'val_'
            T.set_grad_enabled(False)
        need_sync = (self.__LOCAL_RANK is not None)

        running_loss = T.tensor(.0, device=device)
        if hasattr(dataloader, 'sampler') and isinstance(dataloader.sampler, DistributedSampler):
            dataloader.sampler.set_epoch(cur_epoch)
        pbar = tqdm(enumerate(dataloader), total=len(dataloader), file=sys.stdout, disable=not verbose, desc=f'Epoch [{cur_epoch}/{total_epochs}]', dynamic_ncols=True)
        # reset metic statistics
        for m in metrics:
            m[2].reset().to(device)
        batch, loss = None, None
        output = []
        for i, batch in pbar:
            batch = self._move_batch_to_device(batch, device)
            callbacks.on_batch_begin(stage, cur_epoch, i, len(dataloader), batch, self.training_logging, self.validation_logging)
            loss, res = self._iter_one_batch(stage, batch, metrics, callbacks, return_output)
            if res:
                output.append(res)
            running_loss = (running_loss * i + float(loss)) / (1 + i)
            # sync metric & loss, if ddp.
            # 只在最后一个 step 同步 metric.
            if need_sync and i == len(dataloader) - 1:
                all_reduce_mean(running_loss)
                for m in metrics:
                    m[2].sync()

            ret = {log_prefix+k: v.value.cpu().numpy() for _, k, v in metrics}
            ret[f'{log_prefix}loss'] = float(running_loss)
            callbacks.on_batch_end(stage, cur_epoch, i, len(dataloader), ret, self.training_logging, self.validation_logging)
            with np.printoptions(precision=5):
                metrics_output = {k: f'{v:.5f}' if np.ndim(v)==0 else f'{v}' for k, v in ret.items()}
            pbar.set_postfix(metrics_output)
        T.set_grad_enabled(prev_grad_enabled)
        del batch, loss
        tmp = tuple(map(np.concatenate, zip(*output)))
        if len(tmp) == 1:
            tmp = tmp[0]
        return ret, tmp

    def compute_forward(self, batch_data, stage=Stage.TRAIN):
        if stage == Stage.INFERENCE:
            m = self.module
            return m(*batch_data)
        return self.module(*batch_data[:-self.nloss])

    def compute_losses(self, forward_results, batch_data):
        """
        :param forward_results: tuple. the output of model forward. single output will be wrap to a tuple with len==1.
               use `forward_result[j]` to get j-th forward output component.
        :param batch_data: the output of data_loader's one iter step.
        :return: loss
        """
        target = batch_data[-self.nloss:]
        loss = sum(self.loss_fn[j](forward_results[j], target[j]) for j in range(self.nloss))
        return loss

    def compute_metric(self, idx, name, func, detached_results, batch_data) -> None:
        """
        Doesn't need to return any value. `func` is a `BaseMeter` object whose `value` property is implemented.
        Learner considers `value` property as the metric output.
        """
        target = batch_data[-self.nloss:]
        func(detached_results[idx], target[idx])

    def compute_output(self, detached_results, batch_data):
        return tuple(c.cpu().numpy() for c in detached_results)

    def fit_one_batch(self, batch, metrics, device='cpu'):
        batch = self._move_batch_to_device(batch, device)
        self.module.train()
        with T.enable_grad():
            loss, metrics_result = self._iter_one_batch(Stage.TRAIN, batch, metrics, None)
            return loss, metrics_result

    def valid_one_batch(self, batch, metrics, device='cpu'):
        batch = self._move_batch_to_device(batch, device)
        self.module.eval()
        with T.no_grad():
            loss, metrics_result = self._iter_one_batch(Stage.VALIDATION, batch, metrics, None)
            return loss, {f'val_{k}': v for k, v in metrics_result.items()}

    def predict_one_batch(self, batch, metrics, device='cpu'):
        batch = self._move_batch_to_device(batch, device)
        self.module.eval()
        with T.no_grad():
            output = self._iter_one_batch(Stage.INFERENCE, batch, metrics, None)
            return output

    def fit(self, training_set: Union[List, Tuple, Dataset, DataLoader, TensorDataLoader],
            epochs: int = 10, batch_size: Optional[int] = 128, metrics: Optional[List[Tuple[int, str, BaseMeter]]] = None,
            dataset_split: Optional[Union[Tuple[float, float], Tuple[int, int], Tuple[Sequence[int], Sequence[int]]]] = None,
            validation_set: Optional[Union[List, Tuple, Dataset, DataLoader, TensorDataLoader]] = None,
            callbacks: Optional[Union[List[BaseCallback], CallbackList]] = None,
            device: Union[int, str, T.device] = None, verbose: bool = True, **kwargs):
        """
        :param training_set: (x1, x2, ..., y1, y2, ...), torch Dataset or DataLoader
        :param epochs: int.
        :param batch_size: int. ignored when training_set is `DataLoader` instance.
        :param metrics: None or list of (output index, 'name', BaseMeter)
        :param dataset_split: Two float or two list of index, specify the size or sample index of training/validation set respectively.
                              In this case, `training_set` will be considered as the whole dataset, and will be used to split to training/validation set.
                              The dataset should be (or could be converted to) a *map-style dataset*.
        :param validation_set: This will be ignored if `dataset_split` is set. the type is same as `training_set`. used for validation.
        :param callbacks: list of `Callback`
        :param device: string, int, or torch.device.
        :param verbose: bool.
        :param kwargs: will passed to build dataloader. # todo: unused kwargs warning.
        :return: tuple. DataFrame of training and validation log.
        """
        assert self.optimizer_fn, 'No optimizer.'
        callbacks = CallbackList(callbacks if callbacks else [])
        metrics = metrics if metrics else []
        for i in range(len(metrics)):
            if not isinstance(metrics[i][2], BaseMeter):
                assert callable(metrics[i][2])
                metrics[i] = (*metrics[i][:2], LambdaAverageMeter(metrics[i][2]))
                warn(f"metric #{i} was converted to a `LambdaAverageMeter` object, it doesn't support multi-gpu sync, which will be inaccuracy or wrong.")
                
        if self.__LOCAL_RANK is not None and not isinstance(self.module, DistributedDataParallel):
            module_ = T.nn.SyncBatchNorm.convert_sync_batchnorm(self.module)
            self.module = DistributedDataParallel(module_.to('cuda'), device_ids=[self.__LOCAL_RANK])
            
        # 可能有一些内部变量需要在每次fit前初始化。
        self.scaler = torchamp.GradScaler(enabled=self.amp)
        if callable(self.optimizer_fn):
            self.opt = self.optimizer_fn(self.module.parameters())    # other parameters could be passed by `partial`
        else:
            assert isinstance(self.optimizer_fn, T.optim.Optimizer)
            self.opt = self.optimizer_fn
        if self.loss_fn:
            if not isinstance(self.loss_fn, Iterable):
                self.loss_fn = [self.loss_fn]
            assert all(callable(x) or x is None for x in self.loss_fn)
            self.nloss = len(self.loss_fn)
        else:
            self.nloss = None

        self.val_ld = None
        if dataset_split is not None:
            # 如果先检查 validation_set 的话，validation_set为空时，有两种情况：
            # 一种是真的没有验证集，另一种是再看dataset_split。两种情况下对training_set的处理不完全一样（还需要看是否直接转成TensorDataLoader）
            ds = self._make_dataset(training_set)
            x, y = dataset_split
            assert type(x) == type(y)
            if isinstance(x, Sequence):
                kwargs['sampler'] = SubsetRandomSampler(x)
                self.train_ld = self._make_dataloader(ds, batch_size, **kwargs)
                kwargs['sampler'] = SubsetSequentialSampler(y)
                self.val_ld = self._make_dataloader(ds, batch_size, **kwargs)
            else:
                assert isinstance(x, float) or isinstance(x, int)
                if isinstance(x, float):
                    x = int(len(ds)*x)
                    y = len(ds) - x
                train_ds, val_ds = random_split(ds, [x, y])
                self.train_ld = self._make_dataloader(train_ds, batch_size, **kwargs)
                self.val_ld = self._make_dataloader(val_ds, batch_size, **kwargs)
        else:
            # 只有当kwargs不包含TensorDataloader构造函数参数之外的参数、相应的validation_set/training_set是ndarray/tensor、prefer_tensordataloader=True时，
            # 才会尝试构造TensorDataloader。
            self.train_ld = self._make_dataloader(training_set, batch_size, **kwargs)
            if validation_set is not None:
                self.val_ld = self._make_dataloader(validation_set, batch_size, **kwargs)
        if device is None:
            device = 'cuda' if T.cuda.is_available() else 'cpu'

        self.module.to(device)
        self.stop_training = False
        self.training_logging = []
        self.validation_logging = []
        # 应避免循环引用。callbacks不能作为成员变量，否则当dataloader的num_workers>0、且启用ddp时会报CUDA init error，原因不明，像是pytorch的bug。
        callbacks.set_model(self)
        callbacks.on_train_begin(optimizer=self.opt, local_rank=self.__LOCAL_RANK)
        for e in range(epochs):
            if self.stop_training:
                break
            callbacks.on_epoch_begin(self.training_logging, self.validation_logging)
            running_mean, _ = self._walk_through_data(Stage.TRAIN, self.train_ld, e, epochs, metrics, callbacks, device, verbose, False)
            self.training_logging.append({**{'epoch': e}, **running_mean})
            if self.val_ld is not None:
                running_mean, _ = self._walk_through_data(Stage.VALIDATION, self.val_ld, e, epochs, metrics, callbacks, device, verbose, False)
                self.validation_logging.append({**{'epoch': e}, **running_mean})
            callbacks.on_epoch_end(self.training_logging, self.validation_logging)
        callbacks.on_train_end(self.training_logging, self.validation_logging)
        return pd.DataFrame.from_records(self.training_logging), pd.DataFrame.from_records(self.validation_logging)
    
    def predict(self, X: Union[np.ndarray, T.Tensor, Dataset, DataLoader, TensorDataLoader, List, Tuple], batch_size: Optional[int] = 128,
                device: Union[str, T.device] = None, verbose: bool = True, **kwargs):
        kwargs = kwargs.copy()
        kwargs['__INFERENCE__'] = True
        dl = self._make_dataloader(X, batch_size, **kwargs)
        output = []
        module = self.module
        module.eval()
        if device is None:
            device = 'cuda' if T.cuda.is_available() else 'cpu'
        batch = None
        with T.no_grad():
            module.to(device)
            pbar = tqdm(enumerate(dl), total=len(dl), disable=not verbose, file=sys.stdout, desc='predict', dynamic_ncols=True)
            for _, batch in pbar:
                batch = self._move_batch_to_device(batch, device)
                res = self._iter_one_batch(Stage.INFERENCE, batch, None, None)
                output.append(res)
        del batch, dl
        tmp = tuple(map(np.concatenate, zip(*output)))
        if len(tmp) == 1:
            return tmp[0]
        return tmp


    def evaluate(self, X: Union[np.ndarray, T.Tensor, Dataset, DataLoader, TensorDataLoader, List, Tuple], batch_size: Optional[int] = 128,
                 metrics: Optional[List[Tuple[int, str, BaseMeter]]] = None,
                 device: Union[str, T.device] = None, verbose: bool = True, **kwargs):
        # todo: 如果self.module是个ddp怎么办？
        kwargs = kwargs.copy()
        kwargs['__INFERENCE__'] = True
        dl = self._make_dataloader(X, batch_size, **kwargs)

        # deal with metrics
        metrics = metrics if metrics else []
        for i in range(len(metrics)):
            if not isinstance(metrics[i][2], BaseMeter):
                assert callable(metrics[i][2])
                metrics[i] = (*metrics[i][:2], LambdaAverageMeter(metrics[i][2]))
                warn(f"metric #{i} was converted to a `LambdaAverageMeter` object, it doesn't support multi-gpu sync, which will be inaccuracy or wrong.")
        
        # deal with loss_fn
        if self.loss_fn:
            if not isinstance(self.loss_fn, Iterable):
                self.loss_fn = [self.loss_fn]
            assert all(callable(x) or x is None for x in self.loss_fn)
            self.nloss = len(self.loss_fn)
        else:
            self.nloss = None
        
        # deal with device
        if device is None:
            device = 'cuda' if T.cuda.is_available() else 'cpu'
        
        self.module.to(device)
        _, res = self._walk_through_data(Stage.VALIDATION, dl, 0, 1, metrics, CallbackList([]), device, verbose, True)
        return res


    def save(self, fname):
        m = self.module
        if isinstance(m, DistributedDataParallel):
            m = m.module
        p = Path(fname)
        p.parent.mkdir(parents=True, exist_ok=True)
        T.save(m.state_dict(), fname)

    def load(self, fname, map_location=None):
        m = self.module
        if isinstance(m, DistributedDataParallel):
            m = m.module
        m.load_state_dict(T.load(fname, map_location=map_location))
        return self
