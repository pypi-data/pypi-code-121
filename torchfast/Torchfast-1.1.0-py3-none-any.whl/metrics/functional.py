import torch as T
import warnings
from typing import List


def binary_accuracy(input: T.Tensor, target: T.Tensor):
    return (input.float().round() == target).float().mean()


def binary_accuracy_with_logits(input: T.Tensor, target: T.Tensor):
    return ((input>0).float() == target).float().mean()


def sparse_categorical_accuracy(input: T.Tensor, target: T.Tensor):
    """
    :param input: (N, c) Tensor
    :param target: (N, ) Tensor
    :return: numpy float
    """
    return (input.argmax(dim=-1) == target).float().mean()


def mean_squared_error(input: T.Tensor, target: T.Tensor):
    if not (target.size() == input.size()):
        warnings.warn(
            "Using a target size ({}) that is different to the input size ({}). "
            "This will likely lead to incorrect results due to broadcasting. "
            "Please ensure they have the same size.".format(target.size(), input.size()),
            stacklevel=2,
        )
    return ((input - target)**2).mean()


def root_mean_squared_error(input: T.Tensor, target: T.Tensor):
    if not (target.size() == input.size()):
        warnings.warn(
            "Using a target size ({}) that is different to the input size ({}). "
            "This will likely lead to incorrect results due to broadcasting. "
            "Please ensure they have the same size.".format(target.size(), input.size()),
            stacklevel=2,
        )
    return T.sqrt(((input - target)**2).mean())


def mean_absolute_error(input: T.Tensor, target: T.Tensor):
    if not (target.size() == input.size()):
        warnings.warn(
            "Using a target size ({}) that is different to the input size ({}). "
            "This will likely lead to incorrect results due to broadcasting. "
            "Please ensure they have the same size.".format(target.size(), input.size()),
            stacklevel=2,
        )
    return (input - target).abs().mean()


def multilab_confusion_matrix_at_threshold(input: T.Tensor, target: T.Tensor, threshold: T.tensor):
    """
    给定一个概率矩阵，一个目标矩阵和一个阈值列表，计算在各给定阈值下的confusion matrix。

    Args:
        input (T.Tensor): (n_samples,) or (n_samples, n_labels). [0, 1]的实数，表示概率。 float tesnor.
        target (T.Tensor): same as input. 0/1矩阵。
        threshold (T.Tensor): 1d float tensor.
    Returns:
        shape: 4 x #label x #thres. dim 0: tp, fp, fn, tn
    """
    input = input.reshape(len(input), -1)
    target = target.reshape(len(target), -1)
    nsample, nlabel = target.shape
    nthres = len(threshold)
    thres_tiled = threshold.reshape(1, 1, -1).tile(nlabel, nsample, 1)  # #label x #sample x #thres

    pred = input.T.unsqueeze(-1).tile(1, 1, nthres)  # #label x #sample x #thres
    label = target.T.unsqueeze(-1).tile(1, 1, nthres).bool()

    pred_is_pos = pred >= thres_tiled
    tp = pred_is_pos & label
    fp = pred_is_pos & (~label)
    fn = (~pred_is_pos) & label
    tn = (~pred_is_pos) & (~label)

    return T.vstack([
        tp.sum(1).unsqueeze(0),
        fp.sum(1).unsqueeze(0),
        fn.sum(1).unsqueeze(0),
        tn.sum(1).unsqueeze(0)
    ])
