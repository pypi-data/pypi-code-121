# Docstrings are copied from the original PyTorch implementation.
# See: https://github.com/pytorch/pytorch/blob/master/torch/nn/functional.py

"""
Implementation of framework-agnostic functions.
"""

from typing import Optional

import eagerpy as ep
from eagerpy import Tensor


__all__ = [
    "nll_loss",
    "cross_entropy",
    "accuracy",
]


def _reduction(
    input: Tensor,
    reduction: str,
    mask: Optional[Tensor] = None,
) -> Tensor:
    """
    Reduce the input tensor.

    Args:
        input (Tensor): _description_
        reduction (str, optional): Specifies the reduction to apply to the output:
            ``'none'`` | ``'mean'`` | ``'sum'``. ``'none'``: no reduction will be applied,
            ``'mean'``: the sum of the output will be divided by the number of
            elements in the output, ``'sum'``: the output will be summed. Default: ``'mean'``

    Returns:
        reduced_input (Tensor): _description_
    """

    if reduction == "mean":
        if mask is None:
            return ep.mean(input.float32()).raw
        else:
            return (ep.sum(input * mask) / ep.sum(mask)).raw
    elif reduction == "sum":
        if mask is None:
            return ep.sum(input).raw
        else:
            return ep.sum(input * mask).raw
    elif reduction == "none":
        return input.raw
    else:
        raise ValueError(f"Unknown reduction: {reduction}")


def nll_loss(
    input: Tensor,
    target: Tensor,
    weight: Optional[Tensor] = None,
    ignore_index: int = -100,
    reduction: str = "mean",
) -> Tensor:
    r"""
    Negative log likelihood

    Args:
        input (Tensor): :math:`(N, C)` where `C = number of classes` or :math:`(N, C, H, W)`
            in case of 2D Loss, or :math:`(N, C, d_1, d_2, ..., d_K)` where :math:`K \geq 1`
            in the case of K-dimensional loss. `input` is expected to be log-probabilities.
        target (Tensor): :math:`(N)` where each value is :math:`0 \leq \text{targets}[i] \leq C-1`,
            or :math:`(N, d_1, d_2, ..., d_K)` where :math:`K \geq 1` for K-dimensional loss.
        weight (Tensor, optional): a manual rescaling weight given to each
            class. If given, has to be a Tensor of size `C`. Default: None
        ignore_index (int, optional): Specifies a target value that is ignored
            and does not contribute to the input gradient. When :attr:`size_average` is
            ``True``, the loss is averaged over non-ignored targets. Default: -100
        reduction (str, optional): Specifies the reduction to apply to the output:
            ``'none'`` | ``'mean'`` | ``'sum'``. ``'none'``: no reduction will be applied,
            ``'mean'``: the sum of the output will be divided by the number of
            elements in the output, ``'sum'``: the output will be summed. Default: ``'mean'``

    Returns:
        nll (Tensor)
    """

    input, target = ep.astensors(input, target)
    if weight is not None:
        weight = ep.astensor(weight)

    # TODO: Implement ignore_index
    if ignore_index != -100:
        raise NotImplementedError("ignore_index is not implemented")


    return _reduction(input, reduction)


def cross_entropy(
    input: Tensor,
    target: Tensor,
    weight: Optional[Tensor] = None,
    ignore_index: int = -100,
    reduction: str = "mean",
    label_smoothing: float = 0.0,
):
    r"""
    Cross entropy

    Args:
        input (Tensor) : Predicted unnormalized scores (often referred to as logits);
            see Shape section below for supported shapes.
        target (Tensor) : Ground truth class indices or class probabilities;
            see Shape section below for supported shapes.
        weight (Tensor, optional): a manual rescaling weight given to each
            class. If given, has to be a Tensor of size `C`. Default: None
        ignore_index (int, optional): Specifies a target value that is ignored
            and does not contribute to the input gradient. When :attr:`size_average` is
            ``True``, the loss is averaged over non-ignored targets. Note that
            :attr:`ignore_index` is only applicable when the target contains class indices.
            Default: -100
        reduction (str, optional): Specifies the reduction to apply to the output:
            ``'none'`` | ``'mean'`` | ``'sum'``. ``'none'``: no reduction will be applied,
            ``'mean'``: the sum of the output will be divided by the number of
            elements in the output, ``'sum'``: the output will be summed. Default: ``'mean'``
        label_smoothing (float, optional): A float in [0.0, 1.0]. Specifies the amount
            of smoothing when computing the loss, where 0.0 means no smoothing. The targets
            become a mixture of the original ground truth and a uniform distribution as described in
            `Rethinking the Inception Architecture for Computer Vision <https://arxiv.org/abs/1512.00567>`__.
            Default: :math:`0.0`.

    Shape:
        - Input: Shape :math:`(C)`, :math:`(N, C)` or :math:`(N, C, d_1, d_2, ..., d_K)` with
            :math:`K \geq 1` in the case of `K`-dimensional loss.
        - Target: If containing class indices, shape :math:`()`, :math:`(N)` or
            :math:`(N, d_1, d_2, ..., d_K)` with :math:`K \geq 1` in the case of K-dimensional loss
            where each value should be between :math:`[0, C)`. If containing class probabilities,
            same shape as the input and each value should be between :math:`[0, 1]`.

        where:

        .. math::
            \begin{aligned}
                C ={} & \text{number of classes} \\
                N ={} & \text{batch size} \\
            \end{aligned}

    Returns:
        cross_entropy (Tensor)
    """

    input, target = ep.astensors(input, target)
    if weight is not None:
        weight = ep.astensor(weight)

    is_target_indices = ("int" in str(target.dtype))  # NOTE: This is workaround for dtype decision

    if is_target_indices and input.ndim != target.ndim + 1:
        raise RuntimeError(
            f"Expected input.ndim == target.ndim + 1, got {input.ndim} != {target.ndim + 1}"
        )
    elif not is_target_indices and input.ndim != target.ndim:
        raise RuntimeError(
            f"Expected input.ndim == target.ndim, got {input.ndim} != {target.ndim}"
        )

    if input.ndim == 1 and target.ndim == 0:
        input = ep.expand_dims(input, axis=0)
        target = ep.expand_dims(target, axis=0)

    num_classes = input.shape[1]
    class_shape = (1, num_classes) + (1,) * (input.ndim - 2)

    if is_target_indices:
        indices = ep.reshape(target.arange(num_classes), class_shape)
        label = (indices == ep.expand_dims(target, axis=1))
    else:
        label = target

    log_prob = ep.log_softmax(input, axis=1)
    smooth_label = label * (1.0 - label_smoothing) + label_smoothing / num_classes

    if weight is None:
        ce = -ep.sum(log_prob * smooth_label, axis=1)
    else:
        raise NotImplementedError("weight is not properly implemented")
        # weight = weight / ep.sum(weight)
        # weight = ep.reshape(weight, class_shape)
        # ce = -ep.sum(log_prob * smooth_label * weight, axis=1)

    if is_target_indices:
        mask = (target != ignore_index) if ignore_index >= 0 else None
    elif ignore_index >= 0:
        raise RuntimeError("ignore_index is only applicable when the target contains class indices")
    else:
        mask = None

    return _reduction(ce, reduction, mask)


def accuracy(
    input: Tensor,
    target: Tensor,
    topk: int = 1,
    ignore_index: int = -100,
    reduction: str = "mean",
) -> Tensor:
    r"""
    Classification accuracy

    Args:
        input (Tensor): :math:`(C)`, :math:`(N, C)` or :math:`(N, C, d_1, d_2, ..., d_K)` with
            :math:`K \geq 1` where `C = number of classes` and `N = batch size`. `input` is expected
            to be logits, log-probabilities or probabilities.
        target (Tensor): :math:`()`, :math:`(N)` or :math:`(N, d_1, d_2, ..., d_K)` with
            :math:`K \geq 1` in the case of K-dimensional loss where each value is
            :math:`0 \leq \text{targets}[i] \leq C-1`.
        topk (int, optional): Default: 1
        ignore_index (int, optional): Specifies a target value that is ignored
            and does not contribute to the input gradient. When :attr:`size_average` is
            ``True``, the loss is averaged over non-ignored targets. Default: -100
        reduction (str, optional): Specifies the reduction to apply to the output:
            ``'none'`` | ``'mean'`` | ``'sum'``. ``'none'``: no reduction will be applied,
            ``'mean'``: the sum of the output will be divided by the number of
            elements in the output, ``'sum'``: the output will be summed. Default: ``'mean'``

    Returns:
        accuracy (Tensor)
    """

    input, target = ep.astensors(input, target)

    if input.ndim != target.ndim + 1:
        raise RuntimeError(
            f"Expected input.ndim == target.ndim + 1, got {input.ndim} != {target.ndim + 1}"
        )

    if input.ndim == 1 and target.ndim == 0:
        input = ep.expand_dims(input, axis=0)
        target = ep.expand_dims(target, axis=0)
    elif input.ndim > 2:
        input = ep.transpose(input, (0,) + tuple(range(2, input.ndim)) + (1,))

    if topk == 1:
        indices = ep.argmax(input, axis=-1)
        correct = (indices == target)
    else:
        _, indices = ep.topk(input, k=topk, sorted=False)
        correct = ep.any((indices == ep.expand_dims(target, axis=-1)), axis=-1)

    mask = (target != ignore_index) if ignore_index >= 0 else None

    return _reduction(correct, reduction, mask)
