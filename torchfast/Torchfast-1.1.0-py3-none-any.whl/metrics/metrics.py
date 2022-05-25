from abc import abstractmethod, ABCMeta
import torch as T
from . import functional as F
from ..misc.misc import all_reduce_mean, distributed
from sklearn.metrics import multilabel_confusion_matrix
from typing import Optional
# 替换现有传入fit中的metrics参数为:[(0, 'acc', BinaryAccuracy())]。原有写法现在会自动转化为LambdaAverageMeter。Meter构造函数尽量不要有参数，保持简洁。


class BaseMeter(metaclass=ABCMeta):
    def to(self, device):
        for k in self.__dict__.keys():
            if isinstance(self.__dict__[k], T.Tensor):
                self.__dict__[k] = self.__dict__[k].to(device)
        return self
    
    @abstractmethod
    def sync(self) -> None:
        # sync 本身并不返回值，只是同步一些统计变量。需要再用value属性获得度量值。
        raise NotImplementedError("Not Implememted `sync` method for your metric.")

    @abstractmethod
    def reset(self) -> "BaseMeter":
        # 要把self返回
        raise NotImplementedError("Not Implememted `reset` method for your metric.")

    @abstractmethod
    def __call__(self, *args, **kwargs):
        raise NotImplementedError("Not Implememted `__call__` method for your metric.")

    @property
    @abstractmethod
    def value(self) -> T.Tensor:
        raise NotImplementedError("Not Implememted `value` method for your metric.")


class AverageMeter(BaseMeter):
    """
    在forward里实现一步的计算，__call__里实现如移动平均等统计，并返回（平均后的）结果。
    """
    def __init__(self):
        self.reset()
    
    def __call__(self, *args, **kwargs):
        v = self.forward(*args, **kwargs)
        self._val = (self._val * self.n + v) / (self.n + 1)
        self.n += 1
        return self._val

    def reset(self):
        self.n = 0
        self._val = T.zeros(1)
        return self

    def sync(self):
        all_reduce_mean(self._val)

    @property
    def value(self):
        return self._val


class LambdaAverageMeter(AverageMeter):
    def __init__(self, fn):
        super().__init__()
        self.fn = fn

    def forward(self, *args, **kwargs):
        return self.fn(*args, **kwargs)


class BinaryAccuracy(AverageMeter):
    def forward(self, input, target):
        return F.binary_accuracy(input, target)


class BinaryAccuracyWithLogits(AverageMeter):
    def forward(self, input, target):
        return F.binary_accuracy_with_logits(input, target)


class SparseCategoricalAccuracy(AverageMeter):
    def forward(self, input: T.Tensor, target: T.Tensor):
        return F.sparse_categorical_accuracy(input, target)


class MeanSquaredError(AverageMeter):
    def forward(self, input: T.Tensor, target: T.Tensor):
        return F.mean_squared_error(input, target)


class RootMeanSquaredError(AverageMeter):
    def forward(self, input: T.Tensor, target: T.Tensor):
        return F.root_mean_squared_error(input, target)


class MeanAbsoluteError(AverageMeter):
    def forward(self, input: T.Tensor, target: T.Tensor):
        return F.mean_absolute_error(input, target)


class F1Score(BaseMeter):
    @staticmethod
    def f1(mcm: T.Tensor, average: Optional[str]):
        tp = mcm[:, 1, 1]
        fp = mcm[:, 0, 1]
        fn = mcm[:, 1, 0]
        if average == 'macro':
            p = tp / (tp + fp)
            r = tp / (tp + fn)
            score = (2*p*r / (p + r)).mean()
        elif average == 'micro':
            p = tp.sum() / (tp.sum() + fp.sum())
            r = tp.sum() / (tp.sum() + fn.sum())
            score = 2*p*r / (p + r)
        elif average is None:
            p = tp / (tp + fp)
            r = tp / (tp + fn)
            score = (2*p*r / (p + r))
        else:
            raise RuntimeError(f"Unknown average method: {average}")
        return score

    def __init__(self, threshold=.0,  average='macro'):
        """
        目前只支持average in {'macro', 'micro', None}。用于二分类、多分类或多标记下的f1计算。

        Args:
            threshold (int, optional): 二值化inputs的阈值。>threshold为1，否则为0，形状需要兼容inputs。Defaults to 'macro'.
            average (str, optional): `macro`: 各个类分别计算f1，然后求平均。`micro`：统一计算tp/fp/fn，然后直接求f1. Defaults to 'macro'.
        
        Inputs:
            input: (n_sample) or (n_sample x n_label). float array
            targets: same as input. 0-1 array.
        """
        assert average in {'macro', 'micro', None}
        self.average = average
        self.threshold = T.tensor(threshold)
        self.reset()

    def reset(self):
        self.confusion_mat = T.zeros(1)
        return self

    def __call__(self, input: T.Tensor, target: T.Tensor):
        # binary/multi-label: input: [N, *], target: [N, *]
        # multi-class: input: [N, c], target: [N, ]
        if not (input.ndim - 1 == target.ndim or input.ndim == target.ndim):
            raise RuntimeError(f"The ndim is mismatch of input: {input.ndim} and target: {target.ndim}.")
        if input.ndim != target.ndim:
            labels = list(range(input.shape[-1]))
            pred = input.argmax(-1).cpu().numpy().astype('int')
        else:
            labels = None
            pred = (input > self.threshold).cpu().numpy().astype('int')
        mcm = T.tensor(multilabel_confusion_matrix(target.cpu().numpy().astype('int'), pred, labels=labels), device=self.confusion_mat.device)
        self.confusion_mat = self.confusion_mat + mcm
        return self.value

    def sync(self):
        distributed.all_reduce(self.confusion_mat, op=distributed.ReduceOp.SUM)

    @property
    def value(self):
        return F1Score.f1(self.confusion_mat, self.average)


class ROCAUC(BaseMeter):
    @staticmethod
    def auc(mcmt: T.Tensor):
        tp, fp, fn, tn = mcmt
        x = fp / (fp + tn) # [c, #thres]
        y = tp / (tp + fn)
        num_thres = x.shape[1]
        assert y.shape[1] == num_thres
        area = 0.5 * (x[:, :num_thres - 1] - x[:, 1:]) * (y[:, :num_thres - 1] + y[:, 1:])
        return area.sum(1).mean()

    def __init__(self, num_thresholds=200):
        """
        用于二分类或多标记下的ROC AUC计算。多标记下取各标记下的auc平均值，即macro方式。

        Args:
            num_thresholds (int, optional): [0, 1]分成多少个区间. Defaults to 200.

        Inputs:
            input: (n_sample) or (n_sample x n_label). float array
            targets: same as input. 0-1 array.

        Example:
            ```
                auc = ROCAUC(10)
                auc(T.tensor([0.9, 0.8, 0.7, 0.6, 0.5]), T.tensor([1, 1, 0, 1, 1]))
                print(auc.value) # 0.5
                auc(T.tensor([0.4, 0.3, 0.2, 0.1, 0]), T.tensor([0, 0, 1, 0, 0]))
                print(auc.value) # 0.8
            ```
        """
        self.threshold = T.linspace(0, 1, num_thresholds+1)
        self.reset()

    def reset(self):
        self.confusion_mat = T.zeros(1)

    def __call__(self, input: T.tensor, target: T.tensor):
        # multilab_confusion_matrix_at_threshold
        mcmt = F.multilab_confusion_matrix_at_threshold(input, target, self.threshold)  # [tp, fp, fn, tn]
        self.confusion_mat = self.confusion_mat + mcmt
        return self.value

    def sync(self):
        distributed.all_reduce(self.confusion_mat, op=distributed.ReduceOp.SUM)

    @property
    def value(self):
        return ROCAUC.auc(self.confusion_mat)
