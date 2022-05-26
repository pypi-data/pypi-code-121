# Copyright 2021 The KaiJIN Authors. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# ==============================================================================
"""Losses collections
"""

import itertools
import math

import scipy.sparse as sp
import numpy as np

import torch
from torch import nn
import torch.nn.functional as F
from torch.nn.modules.loss import _Loss

# for autograd
from torch.autograd.function import once_differentiable

try:
  from tw import _C
except ImportError:
  _C = None

import tw

__all__ = [
    "L1Loss",
    "WeightedTVLoss",
    "PerceptualLoss",
    "LPIPSLoss",
    "CharbonnierLoss",
    "GeneralGanLoss",
    "GradientPenaltyLoss",
    "ContentLoss",
    "AngleLoss",
    "KLStandardGaussianLoss",
    "LogRatioMetricLoss",
    "PSNRLoss",
    "PixelPositionAwareLoss",
    "ReliabLoss",
    "StructuralSimilarityLoss",
    "SmoothL1Loss",
    "IoULoss",
    "GIoULoss",
    "DIoULoss",
    "CIoULoss",
    "SigmoidFocalLoss",
    "OrderSensitiveMetricLoss",
    "MutualChannelLoss",
    "LabelSmoothLoss",
    "EBMLoss",
    "MonotonicityRelatedLoss",
    "PLCCLoss",
    "LaplacianLoss",
    "NMELoss",
    "WingLoss",
    "SmoothWingLoss",
    "WiderWingLoss",
    "NormalizedWiderWingLoss",
    "MultiLevelEPELoss",
    "MultiLevelCharbonnierLoss",
]


#!<-----------------------------------------------------------------------------
#!<  spatial Loss
#!<-----------------------------------------------------------------------------

class L1Loss(nn.Module):
  """L1 (mean absolute error, MAE) loss.

  Args:
      loss_weight (float): Loss weight for L1 loss. Default: 1.0.
      reduction (str): Specifies the reduction to apply to the output.
          Supported choices are 'none' | 'mean' | 'sum'. Default: 'mean'.
  """

  def __init__(self, loss_weight=1.0, reduction='mean'):
    super(L1Loss, self).__init__()
    if reduction not in ['none', 'mean', 'sum']:
      raise ValueError(f'Unsupported reduction mode: {reduction}. '
                       f'Supported ones are: {_reduction_modes}')

    self.loss_weight = loss_weight
    self.reduction = reduction

  def forward(self, pred, target, weight=None, **kwargs):
    """
    Args:
        pred (Tensor): of shape (N, C, H, W). Predicted tensor.
        target (Tensor): of shape (N, C, H, W). Ground truth tensor.
        weight (Tensor, optional): of shape (N, C, H, W). Element-wise
            weights. Default: None.
    """
    return self.loss_weight * F.l1_loss(pred, target, weight, reduction=self.reduction)


class WeightedTVLoss(L1Loss):
  """Weighted TV loss.

      Args:
          loss_weight (float): Loss weight. Default: 1.0.
  """

  def __init__(self, loss_weight=1.0):
    super(WeightedTVLoss, self).__init__(loss_weight=loss_weight)

  def forward(self, pred, weight=None):
    y_diff = super(WeightedTVLoss, self).forward(pred[:, :, :-1, :], pred[:, :, 1:, :], weight=weight[:, :, :-1, :])
    x_diff = super(WeightedTVLoss, self).forward(pred[:, :, :, :-1], pred[:, :, :, 1:], weight=weight[:, :, :, :-1])

    loss = x_diff + y_diff

    return loss

#!<-----------------------------------------------------------------------------
#!<  LPIPS Loss
#!<-----------------------------------------------------------------------------


class PerceptualLoss(nn.Module):
  """Perceptual loss with commonly used style loss.

  Args:
      layer_weights (dict): The weight for each layer of vgg feature.
          Here is an example: {'conv5_4': 1.}, which means the conv5_4
          feature layer (before relu5_4) will be extracted with weight
          1.0 in calculting losses.
      vgg_type (str): The type of vgg network used as feature extractor.
          Default: 'vgg19'.
      use_input_norm (bool):  If True, normalize the input image in vgg.
          Default: True.
      range_norm (bool): If True, norm images with range [-1, 1] to [0, 1].
          Default: False.
      perceptual_weight (float): If `perceptual_weight > 0`, the perceptual
          loss will be calculated and the loss will multiplied by the
          weight. Default: 1.0.
      style_weight (float): If `style_weight > 0`, the style loss will be
          calculated and the loss will multiplied by the weight.
          Default: 0.
      criterion (str): Criterion used for perceptual loss. Default: 'l1'.
  """

  def __init__(self,
               layer_weights,
               vgg_type='vgg19',
               use_input_norm=True,
               range_norm=False,
               perceptual_weight=1.0,
               style_weight=0.,
               criterion='l1'):
    super(PerceptualLoss, self).__init__()
    self.perceptual_weight = perceptual_weight
    self.style_weight = style_weight
    self.layer_weights = layer_weights
    self.vgg = tw.models.vgg_extractor.VGGFeatureExtractor(
        layer_name_list=list(layer_weights.keys()),
        vgg_type=vgg_type,
        use_input_norm=use_input_norm,
        range_norm=range_norm)

    self.criterion_type = criterion
    if self.criterion_type == 'l1':
      self.criterion = torch.nn.L1Loss()
    elif self.criterion_type == 'l2':
      self.criterion = torch.nn.L2loss()
    elif self.criterion_type == 'fro':
      self.criterion = None
    else:
      raise NotImplementedError(f'{criterion} criterion has not been supported.')

  def forward(self, x, gt):
    """Forward function.

    Args:
        x (Tensor): Input tensor with shape (n, c, h, w).
        gt (Tensor): Ground-truth tensor with shape (n, c, h, w).

    Returns:
        Tensor: Forward results.
    """
    # extract vgg features
    x_features = self.vgg(x)
    gt_features = self.vgg(gt.detach())

    # calculate perceptual loss
    if self.perceptual_weight > 0:
      percep_loss = 0
      for k in x_features.keys():
        if self.criterion_type == 'fro':
          percep_loss += torch.norm(x_features[k] - gt_features[k], p='fro') * self.layer_weights[k]
        else:
          percep_loss += self.criterion(x_features[k], gt_features[k]) * self.layer_weights[k]
      percep_loss *= self.perceptual_weight
    else:
      percep_loss = None

    # calculate style loss
    if self.style_weight > 0:
      style_loss = 0
      for k in x_features.keys():
        if self.criterion_type == 'fro':
          style_loss += torch.norm(self._gram_mat(x_features[k]) -
                                   self._gram_mat(gt_features[k]), p='fro') * self.layer_weights[k]
        else:
          style_loss += self.criterion(self._gram_mat(x_features[k]),
                                       self._gram_mat(gt_features[k])) * self.layer_weights[k]
      style_loss *= self.style_weight
    else:
      style_loss = None

    return percep_loss, style_loss

  def _gram_mat(self, x):
    """Calculate Gram matrix.

    Args:
        x (torch.Tensor): Tensor with shape of (n, c, h, w).

    Returns:
        torch.Tensor: Gram matrix.
    """
    n, c, h, w = x.size()
    features = x.view(n, c, w * h)
    features_t = features.transpose(1, 2)
    gram = features.bmm(features_t) / (c * h * w)
    return gram


class LPIPSLoss(nn.Module):

  r"""Ref: The Unreasonable Effectiveness of Deep Features as a Perceptual Metric

  Usage:
    pip install lpips

    import lpips
    loss_fn_alex = lpips.LPIPS(net='alex') # best forward scores
    loss_fn_vgg = lpips.LPIPS(net='vgg') # closer to "traditional" perceptual loss, when used for optimization

    import torch
    img0 = torch.zeros(1,3,64,64) # image should be RGB, IMPORTANT: normalized to [-1,1]
    img1 = torch.zeros(1,3,64,64)
    d = loss_fn_alex(img0, img1)

  """

  def __init__(self, net='vgg'):
    super(LPIPSLoss, self).__init__()
    assert net in ['vgg', 'alex', 'squeeze']

    import lpips
    self.loss = lpips.LPIPS(net=net)

  def forward(self, inputs1, inputs2):
    """
    """
    return self.loss(inputs1, inputs2, normalize=True)


#!<-----------------------------------------------------------------------------
#!<  Charbonnier Loss
#!<-----------------------------------------------------------------------------


class CharbonnierLoss(nn.Module):
  r"""Charbonnier Loss (L1)

    eps normally in [1e-6, 1e-3]

  """

  def __init__(self, eps=1e-6):
    super(CharbonnierLoss, self).__init__()
    self.eps = eps

  def forward(self, x, y):
    diff = x - y
    loss = torch.sum(torch.sqrt(diff * diff + self.eps))
    return loss

#!<-----------------------------------------------------------------------------
#!<  GAN Loss
#!<-----------------------------------------------------------------------------


class GeneralGanLoss(nn.Module):

  def __init__(self, real_label=1.0, fake_label=0.0, gan_type='gan', loss_weight=1.0):
    super(GeneralGanLoss, self).__init__()
    assert gan_type in ['gan', 'ragan', 'lsgan', 'wgan', 'wgan_softplus', 'hinge']

    self.gan_type = gan_type
    self.loss_weight = loss_weight
    self.real_label_val = real_label
    self.fake_label_val = fake_label

    if self.gan_type in ['gan', 'ragan']:
      self.loss = nn.BCEWithLogitsLoss()
    elif self.gan_type == 'lsgan':
      self.loss = nn.MSELoss()
    elif self.gan_type == 'wgan':
      self.loss = self._wgan_loss
    elif self.gan_type == 'wgan_softplus':
      self.loss = self._wgan_softplus_loss
    elif self.gan_type == 'hinge':
      self.loss = nn.ReLU()
    else:
      NotImplementedError(self.gan_type)

  def _wgan_loss(self, input, target):
    r"""wgan loss.

    Args:
        input (Tensor): Input tensor.
        target (bool): Target label.

    Returns:
        Tensor: wgan loss.
    """
    return -input.mean() if target else input.mean()

  def _wgan_softplus_loss(self, input, target):
    r"""wgan loss with soft plus. softplus is a smooth approximation to the
    ReLU function.

    In StyleGAN2, it is called:
        Logistic loss for discriminator;
        Non-saturating loss for generator.

    Args:
        input (Tensor): Input tensor.
        target (bool): Target label.

    Returns:
        Tensor: wgan loss.
    """
    return F.softplus(-input).mean() if target else F.softplus(
        input).mean()

  def get_target_label(self, input, target_is_real):
    r"""Get target label.

    Args:
        input (Tensor): Input tensor.
        target_is_real (bool): Whether the target is real or fake.

    Returns:
        (bool | Tensor): Target tensor. Return bool for wgan, otherwise,
            return Tensor.
    """

    if self.gan_type in ['wgan', 'wgan_softplus']:
      return target_is_real
    target_val = (
        self.real_label_val if target_is_real else self.fake_label_val)
    return input.new_ones(input.size()) * target_val

  def forward(self, input, target_is_real, is_disc=False):
    r"""
    Args:
        input (Tensor): The input for the loss module, i.e., the network
            prediction.
        target_is_real (bool): Whether the targe is real or fake.
        is_disc (bool): Whether the loss for discriminators or not.
            Default: False.

    Returns:
        Tensor: GAN loss value.
    """
    target_label = self.get_target_label(input, target_is_real)
    if self.gan_type == 'hinge':
      if is_disc:  # for discriminators in hinge-gan
        input = -input if target_is_real else input
        loss = self.loss(1 + input).mean()
      else:  # for generators in hinge-gan
        loss = -input.mean()
    else:  # other gan types
      loss = self.loss(input, target_label)

    # loss_weight is always 1.0 for discriminators
    return loss if is_disc else loss * self.loss_weight

  def _get_target_label(self, inputs, target_is_real):
    """prepare target label
    """
    if self.gan_type == 'wgan-gap':
      return target_is_real

    if target_is_real:
      return torch.empty_like(inputs).fill_(self.real_label)
    else:
      return torch.empty_like(inputs).fill_(self.fake_label)


#!<-----------------------------------------------------------------------------
#!<  Gradient Penalty Loss
#!<-----------------------------------------------------------------------------


class GradientPenaltyLoss(nn.Module):

  def __init__(self, device='cpu'):
    super(GradientPenaltyLoss, self).__init__()
    self.register_buffer('grad_outputs', torch.Tensor())
    self.grad_outputs = self.grad_outputs.to(device)

  def get_grad_outputs(self, input):
    if self.grad_outputs.size() != input.size():
      self.grad_outputs.resize_(input.size()).fill_(1.0)
    return self.grad_outputs

  def forward(self, interp, interp_crit):
    grad_outputs = self.get_grad_outputs(interp_crit)
    grad_interp = torch.autograd.grad(outputs=interp_crit,
                                      inputs=interp,
                                      grad_outputs=grad_outputs,
                                      create_graph=True,
                                      retain_graph=True,
                                      only_inputs=True)[0]
    grad_interp = grad_interp.view(grad_interp.size(0), -1)
    grad_interp_norm = grad_interp.norm(2, dim=1)

    loss = ((grad_interp_norm - 1) ** 2).mean()
    return loss

#!<-----------------------------------------------------------------------------
#!<  Content Loss
#!<-----------------------------------------------------------------------------


class ContentLoss(nn.Module):

  def __init__(self, f=2):
    super(ContentLoss, self).__init__()
    self.f = f

  def forward(self, im_batch1, im_batch2):
    r"""im_batch1, im_batch2 should be in N C H W, or N C S H W shape
    """
    assert im_batch1.shape == im_batch2.shape

    # find channel dimension
    dims = len(im_batch1.shape)
    assert dims in (4, 5)

    # get mean L2 loss
    if self.f == 2:
      content_loss = (im_batch1 - im_batch2).power(2).sum(dim=1).mean()
    elif self.f == 1:
      content_loss = (im_batch1 - im_batch2).abs().sum(dim=1).mean()
    return content_loss


#!<-----------------------------------------------------------------------------
#!<  Angle Loss
#!<-----------------------------------------------------------------------------


class AngleLoss(nn.Module):
  def __init__(self, gamma=0):
    super(AngleLoss, self).__init__()
    self.gamma = gamma
    self.it = 0
    self.LambdaMin = 5.0
    self.LambdaMax = 1500.0
    self.lamb = 1500.0

  def forward(self, input, target):
    self.it += 1
    cos_theta, phi_theta = input
    target = target.view(-1, 1)  # size=(B,1)

    index = cos_theta.data * 0.0  # size=(B,Classnum)
    index.scatter_(1, target.data.view(-1, 1), 1)
    index = index.bool()
    index = torch.autograd.Variable(index)

    self.lamb = max(self.LambdaMin, self.LambdaMax / (1 + 0.1 * self.it))
    output = cos_theta * 1.0  # size=(B,Classnum)
    output[index] -= cos_theta[index] * (1.0 + 0) / (1 + self.lamb)
    output[index] += phi_theta[index] * (1.0 + 0) / (1 + self.lamb)

    logpt = F.log_softmax(output)
    logpt = logpt.gather(1, target)
    logpt = logpt.view(-1)
    pt = torch.autograd.Variable(logpt.data.exp())

    loss = -1 * (1 - pt)**self.gamma * logpt
    loss = loss.mean()

    return loss


#!<-----------------------------------------------------------------------------
#!< KL Loss with standard deviation
#!<-----------------------------------------------------------------------------

class KLStandardGaussianLoss(nn.Module):
  r""" -KL[q(x)|N(0, I)] Loss
  """

  def __init__(self):
    super(KLStandardGaussianLoss, self).__init__()

  def forward(self, mean: torch.Tensor, var: torch.Tensor):
    mean = mean.squeeze()
    var = var.squeeze()
    assert len(mean.shape) == 2 and mean.shape == var.shape
    assert isinstance(mean, torch.Tensor) and isinstance(var, torch.Tensor)
    return (-0.5 * (1 + var.log() - mean.pow(2) - var)).sum(dim=1).mean()


#!<-----------------------------------------------------------------------------
#!< Log Ratio Metric Learning Loss
#!<-----------------------------------------------------------------------------


class LogRatioMetricLoss(nn.Module):
  r"""Paper [CVPR 2019]:
    Title: Deep metric learning beyond binary supervision
    Author: S.Kim, M. Seo, I. Laptev et al.
  """

  def __init__(self, device):
    super(LogRatioMetricLoss, self).__init__()
    self.device = device

  def forward(self, features, labels):
    r"""dense triplet sample + log ratio loss

    Args:
      features: [N, num_feature] [0 ~ 1]
      labels: [N, num_classes] [0, 1]

    Returns:
      losses:

    """
    bs, num_feature = features.shape
    labels = labels.float()

    _i = torch.randperm(bs).to(self.device)
    _j = torch.randperm(bs).to(self.device)

    f_ai = (features - features[_i]).pow(2).sum(dim=1)
    f_aj = (features - features[_j]).pow(2).sum(dim=1)
    y_ai = (labels - labels[_i]).pow(2).sum(dim=1)
    y_aj = (labels - labels[_j]).pow(2).sum(dim=1)

    # dense sample
    inds = y_ai > torch.tensor(0.0).to(self.device)
    inds &= y_ai < y_aj
    f_ai = f_ai[inds]
    f_aj = f_aj[inds]
    y_ai = y_ai[inds]
    y_aj = y_aj[inds]

    # dense sample again for features
    inds = f_ai > torch.tensor(0.0).to(self.device)
    inds &= f_aj > torch.tensor(0.0).to(self.device)
    f_ai = f_ai[inds]
    f_aj = f_aj[inds]
    y_ai = y_ai[inds]
    y_aj = y_aj[inds]

    # compute dist
    d_part_1 = f_ai.log() - y_ai.log()
    d_part_2 = f_aj.log() - y_aj.log()
    log_ratio_loss = (d_part_1 - d_part_2).pow(2)

    if f_ai.size(0) == 0:
      loss = 0.0
    else:
      loss = log_ratio_loss.sum() / f_ai.size(0)

    return loss


#!<-----------------------------------------------------------------------------
#!< Peak Signal to Noise Ratio
#!<-----------------------------------------------------------------------------

class PSNRLoss(nn.Module):
  r"""Peak Signal to Noise Ratio
    reference: https://github.com/huster-wgm/Pytorch-metrics/blob/master/metrics.py
  """

  def __init__(self):
    super(PSNRLoss, self).__init__()

  @staticmethod
  def binarize(y_data, threshold):
    r"""

    Args:
      y_data : [float] 4-d tensor in [batch_size, channels, img_rows, img_cols]
      threshold : [float] [0.0, 1.0]

    Returns:
      4-d binarized y_data

    """
    y_data[y_data < threshold] = 0.0
    y_data[y_data >= threshold] = 1.0
    return y_data

  @staticmethod
  def psnr(y_pred, y_true, dim=1, threshold=None):
    r"""

    Args:
      y_true : 4-d ndarray in [batch_size, channels, img_rows, img_cols]
      y_pred : 4-d ndarray in [batch_size, channels, img_rows, img_cols]
      threshold : [0.0, 1.0]

    Returns:
      PSNR, larger the better

    """
    if threshold:
      y_pred = PSNRLoss.binarize(y_pred, threshold)
    mse = torch.mean((y_pred - y_true) ** 2)
    return 10 * torch.log10(1 / mse)

  def forward(self, y_pred, y_true, dim=1, threshold=None):
    return PSNRLoss.psnr(y_pred, y_true, dim, threshold)


#!<-----------------------------------------------------------------------------
#!<
#!<-----------------------------------------------------------------------------

class PixelPositionAwareLoss(nn.Module):
  r"""Pixel Position Aware Loss:
    Titel: F3Net: Fusion, Feedback and Focus for Salient Object Detection
    Reference: https://github.com/weijun88/F3Net
  """

  def __init__(self, gamma=5, side=15, reduction=None):
    super(PixelPositionAwareLoss, self).__init__()
    self.gamma = gamma
    self.side = side
    self.reduction = reduction

  @staticmethod
  def pixel_position_aware_loss(pred, mask, gamma=5, side=15, reduction='mean'):
    weit = 1 + gamma * torch.abs(F.avg_pool2d(mask, kernel_size=int(side * 2 + 1), stride=1, padding=side) - mask)  # nopep8
    wbce = F.binary_cross_entropy_with_logits(pred, mask, reduce='none')
    wbce = (weit * wbce).sum(dim=(2, 3)) / weit.sum(dim=(2, 3))
    pred = torch.sigmoid(pred)
    inter = ((pred * mask) * weit).sum(dim=(2, 3))
    union = ((pred + mask) * weit).sum(dim=(2, 3))
    wiou = 1 - (inter + 1) / (union - inter + 1)

    if reduction == 'mean':
      return (wbce + wiou).mean()
    elif reduction == 'sum':
      return (wbce + wiou).sum()
    else:
      return (wbce + wiou)

  def forward(self, pred, mask):
    return PixelPositionAwareLoss.pixel_position_aware_loss(
        pred, mask,
        gamma=self.gamma,
        side=self.side,
        reduction=self.reduction)


#!<-----------------------------------------------------------------------------
#!< Reliab Loss
#!<-----------------------------------------------------------------------------


class ReliabLoss(nn.Module):
  r"""Leveraging Implicit Relative Labeling-Importance Information for Effective Multi-label Learning

    * Note: the version is modifed ReliabLoss
    1. the diagonal value of W is not set to zero.
    2. emp loss (due to negative loss, change to)
      emp_pos = max(f(y0) - f(y), 0), if y is positive label
      emp_neg = max(f(y) - f(y0), 0), if y is negative label
      r = |Yi| / |non Yi|
      emp_loss = emp_pos + r * emp_neg

  """

  def __init__(self, device, tao=0.2, alpha=0.5):
    super(ReliabLoss, self).__init__()
    self.tao = tao
    self.alpha = alpha
    self.device = device
    self.kl_loss = nn.KLDivLoss(reduction='batchmean')

  def forward(self, images, preds, labels):
    r"""

    Args:
      images: [N, C, H, W] the last layer of backbone conv
        NOTE: require input should normalized to [0, 1]
      preds: [N, C] classification prediction
      labels: [N, C] classification groundtruth

    Returns:
      loss_reliab: reliab loss

    """
    bs, nclass = labels.shape

    # * construct similarity matrix
    Xi = images.reshape(bs, 1, -1)
    Xj = images.reshape(1, bs, -1)
    W = torch.exp(-0.5 * (Xi - Xj).mean(dim=2).pow(2))  # .fill_diagonal_(0)
    # print_matrix(W)

    # * construct labeling-importance matrix
    D = W.sum(dim=1)
    D = torch.diag(D)
    # print_matrix(D)
    P = D.sqrt() * W * D.sqrt()
    # print_matrix(P)

    I = torch.ones(bs, 1).to(self.device)
    phi = torch.cat([I * self.tao, labels], dim=1)

    # * construct label propagation
    I = torch.eye(bs).to(self.device)
    F = ((1.0 - self.alpha) * (I - self.alpha * P)).inverse()
    F = torch.mm(F, phi)

    # print_matrix(phi)
    # print_matrix(F)

    # * estimate RLI degree
    U = F / F.sum(dim=1, keepdim=True)
    # print_matrix(U)

    # * compute normalized Z*
    preds = preds.exp() / preds.exp().sum(dim=1, keepdim=True)
    # print_matrix(preds)

    # * compute KL-div
    loss_reliab_dis = self.kl_loss((preds + 1e-5).log(), U)
    # print(loss_reliab_dis)

    # * compute emp loss
    r = labels.sum(dim=1, keepdim=True) / (nclass - labels.sum(dim=1, keepdim=True))  # nopep8
    preds_y0 = preds[..., 0].unsqueeze_(-1)
    preds_wo_y0 = preds[..., 1:]
    # print_matrix(preds_wo_y0 - preds_y0)

    # * compute rel and irrel
    emp_rel = torch.relu((preds_y0 - preds_wo_y0)[labels == 1]).mean()
    emp_irrel = torch.relu((r * (preds_wo_y0 - preds_y0))[labels == 0]).mean()
    loss_reliab_emp = (emp_rel + emp_irrel) * bs

    return loss_reliab_dis, loss_reliab_emp


#!<-----------------------------------------------------------------------------
#!< SSIM Loss
#!<-----------------------------------------------------------------------------

class StructuralSimilarityLoss(torch.nn.Module):

  def __init__(self, window_size=11, size_average=True):
    super(StructuralSimilarityLoss, self).__init__()
    self.window_size = window_size
    self.size_average = size_average
    self.channel = 1
    self.window = StructuralSimilarityLoss.create_window(window_size, self.channel)

  @staticmethod
  def gaussian(window_size, sigma):
    gauss = torch.Tensor([math.exp(-(x - window_size // 2)**2 / float(2 * sigma**2)) for x in range(window_size)])  # nopep8
    return gauss / gauss.sum()

  @staticmethod
  def create_window(window_size, channel):
    _1D_window = StructuralSimilarityLoss.gaussian(window_size, 1.5).unsqueeze(1)
    _2D_window = _1D_window.mm(_1D_window.t()).float().unsqueeze(0).unsqueeze(0)
    window = torch.autograd.Variable(_2D_window.expand(channel, 1, window_size, window_size).contiguous())  # nopep8
    return window

  @staticmethod
  def ssim(img1, img2, window, window_size, channel, size_average=True):
    mu1 = F.conv2d(img1, window, padding=window_size // 2, groups=channel)
    mu2 = F.conv2d(img2, window, padding=window_size // 2, groups=channel)

    mu1_sq = mu1.pow(2)
    mu2_sq = mu2.pow(2)
    mu1_mu2 = mu1 * mu2

    sigma1_sq = F.conv2d(img1 * img1, window, padding=window_size // 2, groups=channel) - mu1_sq  # nopep8
    sigma2_sq = F.conv2d(img2 * img2, window, padding=window_size // 2, groups=channel) - mu2_sq  # nopep8
    sigma12 = F.conv2d(img1 * img2, window, padding=window_size // 2, groups=channel) - mu1_mu2  # nopep8

    C1 = 0.01**2
    C2 = 0.03**2

    ssim_map = ((2 * mu1_mu2 + C1) * (2 * sigma12 + C2)) / ((mu1_sq + mu2_sq + C1) * (sigma1_sq + sigma2_sq + C2))  # nopep8

    if size_average:
      return ssim_map.mean()
    else:
      return ssim_map.mean(1).mean(1).mean(1)

  @staticmethod
  def structural_similarity(img1, img2, window_size=11, size_average=True):
    (_, channel, _, _) = img1.size()
    window = StructuralSimilarityLoss.create_window(window_size, channel)

    if img1.is_cuda:
      window = window.cuda(img1.get_device())
    window = window.type_as(img1)

    return StructuralSimilarityLoss.ssim(img1, img2, window, window_size, channel, size_average)

  def forward(self, img1, img2):
    r"""

    Args:
      img1: [N, C, H, W]
      img2: [N, C, H, W]

    Returns:
      ssim loss:

    """

    (_, channel, _, _) = img1.size()

    if channel == self.channel and self.window.data.type() == img1.data.type():
      window = self.window
    else:
      window = StructuralSimilarityLoss.create_window(self.window_size, channel)

      if img1.is_cuda:
        window = window.cuda(img1.get_device())
      window = window.type_as(img1)

      self.window = window
      self.channel = channel

    return StructuralSimilarityLoss.ssim(img1, img2, window, self.window_size, channel, self.size_average)


#!<-----------------------------------------------------------------------------
#!< Smooth L1 Loss
#!<-----------------------------------------------------------------------------

class SmoothL1Loss(nn.Module):
  r"""very similar to the smooth_l1_loss from pytorch, but with the extra
    beta parameter.
  """

  def __init__(self, beta=1. / 9, reduction=None):
    super(SmoothL1Loss, self).__init__()
    self.beta = beta
    self.reduction = reduction

  def forward(self, inputs, targets):
    n = torch.abs(inputs - targets)
    cond = n < self.beta
    loss = torch.where(cond, 0.5 * n ** 2 / self.beta, n - 0.5 * self.beta)
    return loss

#!<-----------------------------------------------------------------------------
#!< IoU Losses
#!<-----------------------------------------------------------------------------


class IoULoss(nn.Module):

  def __init__(self, method='linear', reduction=None):
    super(IoULoss, self).__init__()
    self.reduction = reduction
    self.method = method
    assert self.method in ['linear', 'log']
    assert self.reduction in ['none', 'mean', 'sum', None]

  def forward(self, preds, targets, **kwargs):
    """Computing the IoU loss between a set of predicted bboxes and target bboxes.
      The loss is calculated as negative log of IoU.

    Args:
        preds ([torch.Tensor]): [N, 4] (x1, y1, x2, y2)
        targets ([torch.Tensor]): [N, 4] (x1, y1, x2, y2)

    Returns:
        [losses]: [N, ]
    """
    ious = tw.transform.bbox.aligned_iou(preds, targets, mode='iou').clamp(min=1e-6)
    if self.method == 'linear':
      loss = 1 - ious
    elif self.method == 'log':
      loss = -ious.log()
    else:
      raise NotImplementedError
    return loss


class GIoULoss(nn.Module):

  def __init__(self, reduction=None):
    super(GIoULoss, self).__init__()
    self.reduction = reduction

  def forward(self, preds, targets, **kwargs):
    """Generalized Intersection over Union: A Metric and A Loss for Bounding
      Box Regression <https://arxiv.org/abs/1902.09630>

    Args:
        preds ([torch.Tensor]): [N, 4] (x1, y1, x2, y2)
        targets ([torch.Tensor]): [N, 4] (x1, y1, x2, y2)

    Returns:
        [losses]: [N, ]
    """
    gious = tw.transform.bbox.aligned_iou(preds, targets, mode='giou')
    loss = 1 - gious
    return loss


class DIoULoss(nn.Module):

  def __init__(self, reduction=None):
    super(DIoULoss, self).__init__()
    self.reduction = reduction

  def forward(self, preds, targets, **kwargs):
    """Implementation of Distance-IoU Loss: Faster and Better
      Learning for Bounding Box Regression, https://arxiv.org/abs/1911.08287`_.

      Code is modified from https://github.com/Zzh-tju/DIoU.

    Args:
        preds ([torch.Tensor]): [N, 4] (x1, y1, x2, y2)
        targets ([torch.Tensor]): [N, 4] (x1, y1, x2, y2)

    Returns:
        [losses]: [N, ]
    """
    dious = tw.transform.bbox.aligned_iou(preds, targets, mode='diou')
    loss = 1 - dious
    return loss


class CIoULoss(nn.Module):

  def __init__(self, reduction=None):
    super(CIoULoss, self).__init__()
    self.reduction = reduction

  def forward(self, preds, targets, **kwargs):
    """

    Args:
        preds ([torch.Tensor]): [N, 4]
        targets ([torch.Tensor]): [N, 4]

    Returns:
        [losses]: [N, ]
    """
    cious = tw.transform.bbox.aligned_iou(preds, targets, mode='ciou')
    loss = 1 - cious
    return loss

#!<-----------------------------------------------------------------------------
#!<
#!<-----------------------------------------------------------------------------


# TODO: Use JIT to replace CUDA implementation in the future.
class _SigmoidFocalLoss(torch.autograd.Function):

  @staticmethod
  def forward(ctx, logits, targets, gamma, alpha):
    ctx.save_for_backward(logits, targets)
    num_classes = logits.shape[1]
    ctx.num_classes = num_classes
    ctx.gamma = gamma
    ctx.alpha = alpha
    losses = _C.sigmoid_focalloss_forward(logits, targets, num_classes, gamma, alpha)
    return losses

  @staticmethod
  @once_differentiable
  def backward(ctx, d_loss):
    logits, targets = ctx.saved_tensors
    num_classes = ctx.num_classes
    gamma = ctx.gamma
    alpha = ctx.alpha
    d_loss = d_loss.contiguous()
    d_logits = _C.sigmoid_focalloss_backward(logits, targets, d_loss, num_classes, gamma, alpha)
    return d_logits, None, None, None, None


def sigmoid_focal_loss_cpu(logits, targets, gamma, alpha):
  num_classes = logits.shape[1]
  gamma = gamma[0]
  alpha = alpha[0]
  dtype = targets.dtype
  device = targets.device
  class_range = torch.arange(1, num_classes + 1, dtype=dtype, device=device).unsqueeze(0)
  t = targets.unsqueeze(1)
  p = torch.sigmoid(logits)
  term1 = (1 - p) ** gamma * torch.log(p)
  term2 = p ** gamma * torch.log(1 - p)
  return -(t == class_range).float() * term1 * alpha - ((t != class_range) * (t >= 0)).float() * term2 * (1 - alpha)


class SigmoidFocalLoss(nn.Module):
  def __init__(self, gamma, alpha):
    super(SigmoidFocalLoss, self).__init__()
    self.gamma = gamma
    self.alpha = alpha

  def forward(self, input, target):
    if input.is_cuda:
      loss_func = _SigmoidFocalLoss.apply
    else:
      loss_func = sigmoid_focal_loss_cpu

    loss = loss_func(input.float(), target.int(), self.gamma, self.alpha)
    return loss.sum(dim=1)

  def __repr__(self):
    tmpstr = self.__class__.__name__ + "("
    tmpstr += "gamma=" + str(self.gamma)
    tmpstr += ", alpha=" + str(self.alpha)
    tmpstr += ")"
    return tmpstr


#!<-----------------------------------------------------------------------------
#!< OSDH Loss
#!<-----------------------------------------------------------------------------


class OrderSensitiveMetricLoss(nn.Module):
  r"""Order-Sensitive Deep Hashing for Multimorbidity Medical Image Retrieval.
  """

  def __init__(self, device, p=3, rho=5, alpha=0.5, ri_method='hamming'):
    super(OrderSensitiveMetricLoss, self).__init__()
    self.p = p
    self.rho = rho
    self.ri_method = ri_method
    self.alpha = alpha
    self.device = device

  def dist_hamming(self, x, y):
    r""" hamming distance between x and y.

    Where, dist = x * y^T

    Examples:
      1 1 0 0 1 1 1 1 0 0 0 0 0 1 1 0
      1 1 0 0 1 1 1 1 0 0 0 0 0 1 1 0
      0 0 2 0 1 0 2 0 0 0 0 0 0 1 1 0
      0 0 0 1 0 0 0 0 0 0 1 0 0 0 0 0
      1 1 1 0 4 1 3 1 0 0 0 1 0 1 1 0
      1 1 0 0 1 1 1 1 0 0 0 0 0 1 1 0
      1 1 2 0 3 1 4 1 0 0 0 0 0 2 2 0
      1 1 0 0 1 1 1 2 0 0 0 0 0 1 1 1
      0 0 0 0 0 0 0 0 2 0 0 0 1 0 0 1
      0 0 0 0 0 0 0 0 0 1 0 0 0 0 0 0
      0 0 0 1 0 0 0 0 0 0 1 0 0 0 0 0
      0 0 0 0 1 0 0 0 0 0 0 1 0 0 0 0
      0 0 0 0 0 0 0 0 1 0 0 0 1 0 0 1
      1 1 1 0 1 1 2 1 0 0 0 0 0 2 2 0

    Arguments:
      x: [N, num_classes]
      y: [M, num_classes]

    Returns:
      dist: [N, M]

    """
    return torch.mm(x, y.t()).float()

  def dist_importance_hamming(self, x, y, importance):
    r""" hamming importance between x, y

    where:
      \sum{m=0->13}(sum(ri_m, rj_m))/2, m in label * label > 0

    """
    x1 = torch.unsqueeze(x, dim=1)
    y1 = torch.unsqueeze(y, dim=0)
    x_imp = x1 * importance.unsqueeze(dim=1)
    y_imp = y1 * importance.unsqueeze(dim=0)
    dist = x_imp + y_imp
    dist[x1 * y1 == 0] = 0.0
    dist = dist.sum(dim=2) / 2.0
    return dist

  def dist_min_hamming(self, x, y, importance):
    r""" hamming importance with min area

    where:
      \sum{m=0->13}(min(ri_m, rj_m)), m in label * label > 0

    """
    x1 = torch.unsqueeze(x, dim=1)
    y1 = torch.unsqueeze(y, dim=0)
    x_imp = x1 * importance.unsqueeze(dim=1)
    y_imp = y1 * importance.unsqueeze(dim=0)
    dist = torch.min(x_imp, other=y_imp)
    dist[x1 * y1 == 0] = 0.0
    dist = dist.sum(dim=2)
    # print_matrix(dist)
    # print_matrix(self.dist_hamming(x, y))
    # print_matrix(self.dist_importance_hamming(x, y, importance))
    return dist

  def dist_similarity(self, x, y, num_hash_code):
    r"""cosine similarity distance between x and y.

    Examples:
      00.00 11.00 13.91 14.00 11.03
      11.00 00.00 10.90 11.00 08.04
      13.91 10.90 00.18 12.09 14.94
      14.00 11.00 12.09 00.00 14.96
      11.03 08.04 14.94 14.96 00.07

    Arguments:
      x: [N, num_classes]
      y: [M, num_classes]

    Returns:
      dist: [N, M]

    """
    return 0.5 * (num_hash_code - torch.mm(x, y.t()))

  def forward(self, hash_features, labels, preds=None):
    r"""compute order sensitive loss

    Docs:
    (1) Sample Routine:
      For each sample (idx), we first compute its hamming distance between others,
      then search for triplet (idx, i) and (idx, j) requires:
        $ hamming_dist(idx, i) > hamming_dist(idx, j)

      Note: maybe existing multiple (i) for multiple sample with same hamming dist
      For example:
        hamming(idx): 2, 1, 1, 0
        pairs: [idx, 2, 1], [idx, 2, 1], [idx, 2, 0]
               [idx, 1, 0], [idx, 1, 0]

    (2) Compute Loss:
      D(x, y) = 0.5 * (num_hash_code - dot<x, y>)
      Z(idx) = \sum{(2^ri - 2^rj)}
      L(idx) = (2^ri - 2^rj / Z(idx))max(0, D(bq, bi) - D(bq, bj) + rho)

    Arguments:
      hash_features: [N, hash_code] (0 ~ 1)
      labels: [N, num_classes] [0, 1]

    Returns:
      losses

    """
    # * compute similarity dist
    bs, num_hash = hash_features.shape

    with torch.no_grad():
      # * compute hamming dist, dist_gt should be [bs, bs] shape
      if self.ri_method == 'hamming':
        dist_gt = self.dist_hamming(labels, labels)
      elif self.ri_method == 'importance_hamming':
        dist_gt = self.dist_importance_hamming(labels, labels, preds)
      elif self.ri_method == 'min_hamming':
        dist_gt = self.dist_min_hamming(labels, labels, preds)
      else:
        raise NotImplementedError(self.ri_method)

      # * sample i, j in terms of q
      dist_gt = dist_gt.cpu()
      positions = []
      for idx in range(bs):
        dist_gt[idx, idx] = 0  # remove out self match
        r_val, r_ind = dist_gt[idx].sort(descending=True)

        unique_sets = r_val.unique()
        unique_size = len(unique_sets)
        position = []
        # print(unique_sets)
        if unique_size > 1:
          for i in range(unique_size - 1, -1, -1):
            ri_inds = r_ind[r_val == unique_sets[i]]
            for j in range(i - 1, -1, -1):
              rj_inds = r_ind[r_val == unique_sets[j]]
              for _i, _j in itertools.product(ri_inds, rj_inds):
                position.append([_i, _j])

        # * record current sample position and rij2
        positions.append(torch.tensor(position).to(self.device))

    #!< CUDA AREA
    # * dist sim between hash features
    dist_sim = self.dist_similarity(hash_features, hash_features, num_hash)
    dist_gt = dist_gt.to(self.device)
    dist_gt2 = 2 ** dist_gt

    # * compute loss
    losses = torch.zeros(1).to(self.device)
    counts = 0
    for idx, pos in enumerate(positions):

      # * number of sample, element of tuple
      n = pos.shape[0]

      # * skip empty
      if n == 0:
        continue

      # * index
      pos_i = pos[:, 0].long()
      pos_j = pos[:, 1].long()

      # * fetch similarity
      d_qi = dist_sim[idx][pos_i]
      d_qj = dist_sim[idx][pos_j]
      d_ri = dist_gt[idx][pos_i]
      d_rj = dist_gt[idx][pos_j]

      # * compute left term: 1/z * (2^ri - 2^rj)
      rij2 = dist_gt2[idx][pos_i] - dist_gt2[idx][pos_j]
      inv_z = 1.0 / rij2.sum()

      # * compute right term
      triplet_loss = torch.relu(d_qi - d_qj + self.rho)

      # * total
      loss = inv_z * rij2 * triplet_loss

      # * select parts
      if self.ri_method == 'hamming':
        loss = loss[(d_ri - d_rj) <= 2]
      elif self.ri_method == 'min_hamming':
        loss = loss[(d_ri - d_rj) > 0.7]

      losses += loss.sum()
      counts += loss.shape[0]

    if counts == 0:
      return losses
    return losses / counts


#!<-----------------------------------------------------------------------------
#!< Mutual Channel Loss
#!<-----------------------------------------------------------------------------

class MutualChannelLoss(nn.Module):
  r"""Paper:
    Title: The Devil is in the Channels: Mutual-Channel Loss for Fine-Grained Image Classification
    Author: Beijing University of Posts and Telecommunications
  """

  def __init__(self, device, cnum=20, reduction=None):
    super(MutualChannelLoss, self).__init__()
    from tw.nn.pooling import ChannelMaxPool

    self.cnum = cnum
    self.reduction = reduction
    self.ccmp = ChannelMaxPool(kernel_size=cnum, stride=cnum)
    self.gap = nn.AdaptiveAvgPool2d(output_size=(1, 1))
    self.device = device

  def forward(self, features, labels):
    r"""MC-Loss boost the backbone extractor ability.

    Arguments:
      features: [N, C, H, W] the last layer of backbone conv
      labels: [N, C] classification groundtruth

    Returns:
      loss_dis: discriminitive loss
      loss_div: diverse loss

    """
    assert len(features) == 4
    n, c, h, w = features.shape

    # dynamic generate mask
    with torch.no_grad():
      submask = [1] * (self.cnum - int(self.cnum / 2))
      submask += [0] * int(self.cnum / 2)
      mask = []
      for i in range(self.num_classes):
        random.shuffle(submask)
        mask += submask
      mask = [mask for i in range(self.bs)]
      mask = torch.tensor(mask).float()
      mask = mask.reshape(self.bs, self.num_classes * self.cnum, 1, 1)
      mask = mask.to(self.device)

    # diveristy branch
    b1 = features.resize(n, c, h * w)
    b1 = b1.softmax(dim=2)
    b1 = b1.resize(n, c, h, w)
    b1 = self.ccmp(b1)
    b1 = b1.resize(n, self.num_classes, h * w)
    loss_div = 1.0 - 1.0 * b1.sum(dim=2).mean() / self.cnum

    # discriminted branch
    b0 = features * mask
    b0 = self.ccmp(b0)
    b0 = self.gap(b0)
    b0 = torch.flatten(b0, 1).sigmoid()
    loss_dis = nn.functional.binary_cross_entropy(b0, labels)

    return loss_dis, loss_div


#!<-----------------------------------------------------------------------------
#!< Label Smooth Loss
#!<-----------------------------------------------------------------------------

class LabelSmoothLoss(nn.modules.loss._WeightedLoss):

  def __init__(self, weight=None, reduction='mean', smoothing=0.0):
    super().__init__(weight=weight, reduction=reduction)
    self.smoothing = smoothing
    self.weight = weight
    self.reduction = reduction

  @staticmethod
  def _smooth_one_hot(targets: torch.Tensor, n_classes: int, smoothing=0.0):
    assert 0 <= smoothing < 1
    with torch.no_grad():
      targets = torch.empty(size=(targets.size(0), n_classes), device=targets.device) \
          .fill_(smoothing / (n_classes - 1)) \
          .scatter_(1, targets.data.unsqueeze(1), 1. - smoothing)
    return targets

  def forward(self, inputs, targets):
    r"""

    Args:
      inputs:
      targets:

    Returns:
      loss:

    """
    targets = LabelSmoothLoss._smooth_one_hot(targets, inputs.size(-1), self.smoothing)
    lsm = F.log_softmax(inputs, -1)

    if self.weight is not None:
      lsm = lsm * self.weight.unsqueeze(0)

    loss = -(targets * lsm).sum(-1)

    if self.reduction == 'sum':
      loss = loss.sum()
    elif self.reduction == 'mean':
      loss = loss.mean()

    return loss


#!<-----------------------------------------------------------------------------
#!< Energy based loss
#!<-----------------------------------------------------------------------------


class EBMLoss(nn.Module):
  r"""Energy Based Loss"""

  def __init__(self, num_samples, gmm_stds, method='nce', **kwargs):
    super(EBMLoss, self).__init__()
    from tw.nn import GMMSampler

    self.num_samples = num_samples
    self.sampler = GMMSampler(gmm_stds)

    # select method
    if method == 'mcis':
      self.ebm_loss = self.mcis
    elif method == 'mcis_hybrid':
      self.ebm_loss = self.mcis_hybrid
    elif method == 'kldis':
      self.prior_dist = torch.distributions.normal.Normal(loc=0.0, scale=0.025)
      self.ebm_loss = self.kldis
    elif method == 'dsm':
      pass
    elif method == 'mcmc':
      self.step = 16  # Langevin dynamics
      self.alpha = 0.05
      self.ebm_loss = self.mcmc
    elif method == 'nce':
      self.ebm_loss = self.nce
    elif method == 'nce+':
      pass
    elif method == 'sm':
      pass
    else:
      raise NotImplementedError(method)

  def forward(self, predictor, features, labels):
    r"""Energy-based Loss

      Args:
        features: [N, C]
        labels: [N, ]

      Returns:
        loss:
    """
    features = features.squeeze()
    labels = labels.squeeze()

    if features.dim() == 4:  # [N, C, H, W]
      features = features.mean(dim=(2, 3))
    elif features.dim() == 3:
      features = features.mean(dim=2)

    assert features.dim() == 2
    assert len(labels.shape) == 1

    labels = labels.float().unsqueeze(1).to(features.device)

    return self.ebm_loss(predictor, features, labels, features.device)

  def mcis(self, predictor, features, labels, device):
    r"""Monte-Carlo Importance Sampler: Negative Log-Likehood Minimize"""
    # predictor
    targets = labels  # [bs, 1]
    scores_gt = predictor(features, targets).squeeze()  # [bs, ]

    # sample center value and dist
    center, prob = self.sampler(self.num_samples)  # [k, 1], [k, ]
    prob = prob.unsqueeze(0).to(device)  # [1, k]
    center = center.to(device).squeeze(1).unsqueeze(0)  # [1, k]

    # offset to y
    y = targets + center  # [bs, k]
    score_samples = predictor(features, y)  # [bs, k]

    # logz
    logz = (score_samples.exp() / prob).mean(dim=1).log()  # [bs, ]

    # sum
    loss = torch.mean(logz - scores_gt)

    return loss

  def mcis_hybrid(self, predictor, features, labels, device):
    r"""-log(e^f(x,y) / sum(e^f(x_i, y)))"""
    scores_gt = predictor(features, labels).squeeze()  # [bs, ]
    bs = scores_gt.size(0)
    return torch.stack([predictor(features, labels[i].repeat(bs, 1)).logsumexp(dim=0) - scores_gt for i in range(bs)], dim=0).mean()  # nopep8

  def kldis(self, predictor, features, labels, device):
    r"""KL Divergence with Importance Sampling"""
    # predictor
    targets = labels  # [bs, 1]
    # scores_gt = predictor(features, targets).squeeze()  # [bs, ]

    # sample center value and dist
    center, prob = self.sampler(self.num_samples)  # [k, 1], [k, ]
    prob = prob.unsqueeze(0).to(device)  # [1, k]
    center = center.to(device).squeeze(1).unsqueeze(0)  # [1, k]

    # p(y|yi) from Normal distribution
    # we sample from center is identical to center + offset
    p_y_samples = self.prior_dist.log_prob(center).exp().to(device)  # [1, k]

    # offset to y
    y = targets + center  # [bs, k]
    score_samples = predictor(features, y)  # [bs, k]

    # logz
    logz = (score_samples.exp() / prob).mean(dim=1).log()  # [bs, ]

    # sum
    loss = torch.mean(logz - (score_samples * (p_y_samples / prob)).mean(dim=1))  # nopep8

    return loss

  def nce(self, predictor, features, labels, device):
    r"""Noise Contrastive Estimation
    """
    # predictor
    targets = labels  # [bs, 1]
    scores_gt = predictor(features, targets).squeeze()  # [bs, ]

    # sample center value and dist
    center, prob = self.sampler(self.num_samples)  # [k, 1], [k, ]
    prob0 = self.sampler.gmm_density_centered(torch.zeros_like(center), self.sampler.stds)  # nopep8

    # to device
    prob0 = (prob0[0] * torch.ones(scores_gt.size(0))).to(device)  # [k, ]
    prob = prob.unsqueeze(0).to(device)  # [1, k]
    center = center.to(device).squeeze(1).unsqueeze(0)  # [1, k]

    # offset to y
    y = targets + center  # [bs, k]
    score_samples = predictor(features, y)  # [bs, k]

    # sum
    up = scores_gt - prob0.log()
    down = up.exp() + torch.sum((score_samples - prob.log()).exp(), dim=1)
    loss = - torch.mean(up - torch.log(down))

    return loss

  def mcmc(self, predictor, features, labels, device):
    r"""ML with MCMC"""
    # predictor
    targets = labels  # [bs, 1]
    scores_gt = predictor(features, targets).squeeze()  # [bs, ]

    # sample center value and dist
    center, prob = self.sampler(self.num_samples)  # [k, 1], [k, ]
    prob = prob.unsqueeze(0).to(device)  # [1, k]
    center = center.to(device).squeeze(1).unsqueeze(0)  # [1, k]

    # offset to y
    y = targets + center  # [bs, k]

    # mcmc
    for _ in range(self.step):
      y.requires_grad_(True)
      scores = predictor(features, y)
      grad_y = torch.autograd.grad(scores.sum(), y, create_graph=True)[0]
      y = y + (0.5 * self.alpha ** 2) * grad_y + self.alpha * torch.randn(y.size()).to(device)  # nopep8
      y.detach_()

    # select last one
    scores = predictor(features, y)
    loss = torch.mean(torch.mean(scores, dim=1) - scores_gt)

    return loss

#!<-----------------------------------------------------------------------------
#!< Related Loss
#!< https://github.com/lidq92/MDTVSFA/blob/main/VQAloss.py
#!<-----------------------------------------------------------------------------


class MonotonicityRelatedLoss(nn.Module):

  def __init__(self):
    super(MonotonicityRelatedLoss, self).__init__()

  def forward(self, inputs, targets):
    """L = max{(y_i - y_j) * sign(y_j' - y_i'), 0}
      it will take effects only for the un-consistent between prediction order
      and groundtruth order.

    Args:
        inputs ([N, C]): inputs value
        targets ([N, C]): targets value
    """
    bs = inputs.size(0)
    assert inputs.ndim == targets.ndim == 2
    assert bs > 1, "at least input number larger than 2."
    loss = torch.sum(F.relu((inputs - inputs.t()) * torch.sign(targets.t() - targets)))
    return loss / bs / (bs - 1)


class PLCCLoss(nn.Module):

  def __init__(self):
    super(PLCCLoss, self).__init__()

  def forward(self, inputs, targets):
    """PLCC = \frac{(y-y_mean)(y'-y'_mean)}{(y-y_mean)^2(y'-y'_mean)^2}
      it could be seen as cosine_similarity metric.

    Args:
        inputs ([N, C]): inputs value
        targets ([N, C]): targets value
    """
    bs = inputs.size(0)
    assert inputs.ndim == targets.ndim == 2
    assert bs > 1, "at least input number larger than 2."
    return (1 - torch.cosine_similarity(inputs.t() - torch.mean(inputs), targets.t() - torch.mean(targets))[0]) / 2

#!<-----------------------------------------------------------------------------
#!< Face alignment related loss
#!< https://github.com/BeierZhu/Sturcture-Coherency-Face-Alignment
#!<-----------------------------------------------------------------------------


def gen_laplacian_matrix(num_points, top_k):
  """
  Return 106 x 106 matrix
  """
  if num_points == 98:
    connection = np.loadtxt(f'utils/face_graph/{num_points}pts_top{top_k}.txt')
  else:
    connection = np.loadtxt(f'utils/face_graph/{num_points}pts.txt')

  return adj_mx_from_list(connection, num_points)


def adj_mx_from_list(connection, num_points):
  edges = connection[:, :2]
  return adj_mx_from_weighted_edges(num_points, edges)


def adj_mx_from_weighted_edges(num_pts, edges):
  edges = np.array(edges, dtype=np.int32)
  weights = np.ones(edges.shape[0])
  data, i, j = weights, edges[:, 0], edges[:, 1]
  adj_mx = sp.coo_matrix((data, (i, j)), shape=(num_pts, num_pts), dtype=np.float32).todense()

  np.fill_diagonal(adj_mx, 0)
  row_sum = adj_mx.sum(axis=1)
  row_sum[row_sum == 0] = 1
  adj_mx /= row_sum
  np.fill_diagonal(adj_mx, -1)

  adj_mx = torch.tensor(adj_mx, dtype=torch.float)
  return adj_mx.unsqueeze(0)


class LaplacianLoss(_Loss):
  def __init__(self, loss, num_points, reduction="mean"):
    super(LaplacianLoss, self).__init__(reduction=reduction)
    self.loss = loss
    self.num_points = num_points
    self.laplacian_matrix = gen_laplacian_matrix(num_points, 3).cuda()  # 106x106

  def forward(self, prediction, target):
    prediction = prediction.reshape(-1, self.num_points, 2)
    target = target.reshape(-1, self.num_points, 2)
    prediction = torch.matmul(self.laplacian_matrix, prediction)
    target = torch.matmul(self.laplacian_matrix, target)
    prediction = prediction.reshape(-1, self.num_points*2)
    target = target.reshape(-1, self.num_points*2)

    return self.loss(prediction, target)


def nme_loss(prediction: torch.Tensor, target: torch.Tensor, num_points, image_size=256, reduction="mean"):
  """
  normalized_wider_wing = 
      1. C/d * |x|                           , if |x| < thres1
      2. C/d * (thres2*ln(1+|x|/curvature) + B), if |x| >= thres2
  """
  assert prediction.size() == target.size(), 'input tensors must have the same size'

  # Calculate Euclidean distances between actual and target locations
  diff = prediction - target
  diff = diff.reshape(diff.size(0), -1, 2)
  dist_sq = diff.pow(2).sum(-1, keepdim=False)
  loss = dist_sq.sqrt()  # shape (B x N)

  if num_points == 29:
    le_idx = [8]
    re_idx = [9]

  if num_points == 68:
    le_idx = [36]  # le = left eye
    re_idx = [45]  # re = right eye

  if num_points == 98:
    le_idx = [60]
    re_idx = [72]

  target = target.reshape(-1, num_points, 2)
  le_loc = torch.mean(target[:, le_idx, :], dim=1)  # batchsize x 2
  re_loc = torch.mean(target[:, re_idx, :], dim=1)

  norm_dist = torch.sqrt(torch.sum((le_loc - re_loc)**2, dim=1))  # batchsize
  factor = image_size/norm_dist

  if reduction == "sum":
    loss = loss.sum(dim=1)
    loss *= factor
    loss = loss.sum()

  if reduction == "mean":
    loss = loss.mean(dim=1)
    loss *= factor
    loss = loss.mean()

  return loss


class NMELoss(_Loss):
  """docstring for NMELoss"""

  def __init__(self, num_points, image_size, reduction="mean"):
    super(NMELoss, self).__init__(reduction=reduction)
    self.num_points = num_points
    self.image_size = image_size

  def forward(self, prediction, target):
    return nme_loss(prediction, target,
                    num_points=self.num_points,
                    image_size=self.image_size,
                    reduction=self.reduction)


def wing_loss(prediction: torch.Tensor, target: torch.Tensor, width=5, curvature=0.5, reduction="mean"):
  """
  https://arxiv.org/pdf/1711.06753.pdf
  :param prediction:
  :param target:
  :param width:
  :param curvature:
  :param reduction:
  :return:
  """
  diff_abs = (target - prediction).abs()
  loss = diff_abs.clone()

  idx_smaller = diff_abs < width
  idx_bigger = diff_abs >= width

  loss[idx_smaller] = width * torch.log(1 + diff_abs[idx_smaller] / curvature)

  C = width - width * math.log(1 + width / curvature)
  loss[idx_bigger] = loss[idx_bigger] - C

  if reduction == "sum":
    loss = loss.sum()

  if reduction == "mean":
    loss = loss.mean()

  return loss


class WingLoss(_Loss):
  def __init__(self, width=5, curvature=0.5, reduction="mean"):
    super(WingLoss, self).__init__(reduction=reduction)
    self.width = width
    self.curvature = curvature

  def forward(self, prediction, target):
    return wing_loss(prediction, target, self.width, self.curvature, self.reduction)


def smooth_wing_loss(prediction: torch.Tensor, target: torch.Tensor, thres1=2, thres2=20, curvature=2, reduction="mean"):
  """
  smooth_wing = 
      1. |x|                           , if |x| < thres1
      2. thres2*ln(1+|x|/curvature) + B, if A <= |x| < thres2
      3. |x| - C                       , if |x| >= thres2
  """
  loss = (target - prediction).abs()

  idx_small = loss < thres1
  idx_normal = (loss >= thres1) * (loss < thres2)
  idx_big = loss >= thres2

  B = thres1 - thres2 * math.log(1 + thres1 / curvature)
  loss[idx_normal] = thres2 * torch.log(1 + loss[idx_normal] / curvature) + B

  C = thres2 - thres2 * math.log(1 + thres2 / curvature) - B
  loss[idx_big] = loss[idx_big] - C

  if reduction == "sum":
    loss = loss.sum()
  if reduction == "mean":
    loss = loss.mean()

  return loss


class SmoothWingLoss(_Loss):
  """docstring for SmoothWingLoss"""

  def __init__(self, thres1=2, thres2=20, curvature=2, reduction="mean"):
    super(SmoothWingLoss, self).__init__(reduction=reduction)
    self.thres1 = thres1
    self.thres2 = thres2
    self.curvature = curvature

  def forward(self, prediction, target):
    return smooth_wing_loss(prediction, target, self.thres1, self.thres2, self.curvature, self.reduction)


def wider_wing_loss(prediction: torch.Tensor, target: torch.Tensor, thres1=2, thres2=20, curvature=2, reduction="mean"):
  """
  wider_wing = 
      1. |x|                           , if |x| < thres1
      2. thres2*ln(1+|x|/curvature) + B, if |x| >= thres2
  """
  loss = (target - prediction).abs()

  idx_small = loss < thres1
  idx_big = loss >= thres1

  B = thres1 - thres2 * math.log(1 + thres1 / curvature)
  loss[idx_big] = thres2 * torch.log(1 + loss[idx_big] / curvature) + B

  if reduction == "sum":
    loss = loss.sum()
  if reduction == "mean":
    loss = loss.mean()

  return loss


class WiderWingLoss(_Loss):
  """docstring for WiderWingLoss"""

  def __init__(self, thres1=2, thres2=20, curvature=2, reduction="mean"):
    super(WiderWingLoss, self).__init__(reduction=reduction)
    self.thres1 = thres1
    self.thres2 = thres2
    self.curvature = curvature

  def forward(self, prediction, target):
    return wider_wing_loss(prediction, target, self.thres1, self.thres2, self.curvature, self.reduction)


def normalized_wider_wing_loss(prediction: torch.Tensor, target: torch.Tensor, num_points, image_size=256, thres1=2, thres2=20, curvature=2, reduction="mean"):
  """
  normalized_wider_wing = 
      1. C/d * |x|                           , if |x| < thres1
      2. C/d * (thres2*ln(1+|x|/curvature) + B), if |x| >= thres2
  """
  loss = (target - prediction).abs()

  idx_small = loss < thres1
  idx_big = loss >= thres1

  B = thres1 - thres2 * math.log(1 + thres1 / curvature)
  loss[idx_big] = thres2 * torch.log(1 + loss[idx_big] / curvature) + B

  if num_points == 29:
    le_idx = [8]
    re_idx = [9]

  if num_points == 68:
    le_idx = [36]  # le = left eye
    re_idx = [45]  # re = right eye

  if num_points == 98:
    le_idx = [60]
    re_idx = [72]

  target = target.reshape(-1, num_points, 2)
  le_loc = torch.mean(target[:, le_idx, :], dim=1)  # batchsize x 2
  re_loc = torch.mean(target[:, re_idx, :], dim=1)

  norm_dist = torch.sqrt(torch.sum((le_loc - re_loc)**2, dim=1))  # batchsize
  factor = image_size/norm_dist

  if reduction == "sum":
    loss = loss.sum(dim=1)
    loss *= factor
    loss = loss.sum()

  if reduction == "mean":
    loss = loss.mean(dim=1)
    loss *= factor
    loss = loss.mean()

  return loss


class NormalizedWiderWingLoss(_Loss):
  """docstring for NormalizedWiderWingLoss"""

  def __init__(self, thres1=2, thres2=20, curvature=2, num_points=98, image_size=256, reduction="mean"):
    super(NormalizedWiderWingLoss, self).__init__(reduction=reduction)
    self.thres1 = thres1
    self.thres2 = thres2
    self.curvature = curvature

    self.num_points = num_points
    self.image_size = image_size

  def forward(self, prediction, target):
    return normalized_wider_wing_loss(prediction, target, self.num_points, self.image_size, self.thres1, self.thres2, self.curvature, self.reduction)

#!<-----------------------------------------------------------------------------
#!< EPE error: optical flow
#!<-----------------------------------------------------------------------------


def endpoint_error(pred, target, p=2, q=None, eps=None):
  """Calculate end point errors between prediction and ground truth.

  If not define q, the loss function is
  .. math::
    loss = \Vert \mathbf{u}-\mathbf{u_gt} \Vert^p

  otherwise,
  .. math::
    loss = (\Vert \mathbf{u}-\mathbf{u_gt} \Vert^p+eps)^q

  For PWC-Net L2 norm loss: p=2, for the robust loss function p=1, q=0.4,
  eps=0.01.

  Args:
      pred (torch.Tensor): output flow map from flow_estimator
          shape(B, 2, H, W).
      target (torch.Tensor): ground truth flow map shape(B, 2, H, W).
      p (int): norm degree for loss. Options are 1 or 2. Defaults to 2.
      q (float, optional): used to give less penalty to outliers when
          fine-tuning model. Defaults to 0.4.
      eps (float, optional): a small constant to numerical stability when
          fine-tuning model. Defaults to 0.01.

  Returns:
      Tensor: end-point error map with the shape (B, H, W).
  """

  assert pred.shape == target.shape, (f'pred shape {pred.shape} does not match target shape {target.shape}.')

  epe_map = torch.norm(pred - target, p, dim=1)  # shape (B, H, W).

  if q is not None and eps is not None:
    epe_map = (epe_map + eps)**q

  return epe_map


class MultiLevelEPELoss(nn.Module):
  """Multi-level end point error loss.

  Args:

    p (int): norm degree for loss. Options are 1 or 2. Defaults to 2.
    q (float): used to give less penalty to outliers when fine-tuning model. Defaults to None.
    eps (float): a small constant to numerical stability when fine-tuning model. Defaults to None.
    weights (dict): manual rescaling weights given to the loss of flow map
        at each level, and the keys in weights must correspond to predicted
        dict. Defaults to dict(level6=0.32, level5=0.08, level4=0.02, level3=0.01, level2=0.005).
    flow_div (float): the divisor used to scale down ground truth. Defaults to 20.
    max_flow (float): maximum value of optical flow, if some pixel's flow
        of target is larger than it, this pixel is not valid. Default to float('inf').
    resize_flow (str): mode for reszing flow: 'downsample' and 'upsample',
        as multi-level predicted outputs don't match the ground truth.
        If set to 'downsample', it will downsample the ground truth, and
        if set to 'upsample' it will upsample the predicted flow, and
        'upsample' is used for sparse flow map as no generic interpolation
        mode can resize a ground truth of sparse flow correctly. Default to 'downsample'.
    scale_as_level (bool): Whether flow for each level is at its native
        spatial resolution. If `'scale_as_level'` is True, the ground
        truth is scaled at different levels, if it is False, the ground truth will not be scaled. Default to False.
    reduction (str): the reduction to apply to the output:'none', 'mean',
        'sum'. 'none': no reduction will be applied and will return a
        full-size epe map, 'mean': the mean of the epe map is taken, 'sum':
        the epe map will be summed but averaged by batch_size. Default: 'sum'.

    """

  def __init__(self, p=2,
               q=None,
               eps=None,
               weights=[0.32, 0.08, 0.02, 0.01, 0.005],
               flow_div=20.,
               max_flow=float('inf'),
               resize_flow='downsample',
               scale_as_level=False,
               reduction='sum'):
    super(MultiLevelEPELoss, self).__init__()
    assert p == 1 or p == 2
    self.p = p
    self.q = q
    if self.q is not None:
      assert self.q > 0

    self.eps = eps
    if self.eps is not None:
      assert eps > 0

    assert flow_div > 0
    self.flow_div = flow_div

    assert isinstance(weights, list)
    self.weights = weights

    assert max_flow > 0.
    self.max_flow = max_flow

    assert resize_flow in ('downsample', 'upsample')
    self.resize_flow = resize_flow

    assert isinstance(scale_as_level, bool)
    self.scale_as_level = scale_as_level

    assert reduction in ('mean', 'sum')
    self.reduction = reduction

  def forward(self, pred_list, target, valid=None):
    """Forwar function for MultiLevelCharbonnierLoss.

    Args:
        pred_list (list): Multi-level output of predicted optical flow,
            and the contain in dict is a Tensor or list of Tensor with
            shape (B, 2, H_l, W_l), where l indicates the level.
        target (Tensor): Ground truth of optical flow with shape (B, 2, H, W).
        valid (Tensor, optional): Valid mask for optical flow. Defaults to None.

    Returns:
        Tensor: value of pixel-wise generalized Charbonnier loss.

    """
    # compute valid optical flow (avoid to outlier)
    if valid is None:
      valid = torch.ones_like(target[:, 0, :, :])
    else:
      mag = torch.sum(target**2, dim=1).sqrt()
      valid = ((valid >= 0.5) & (mag < self.max_flow)).to(target)

    # normalize
    th, tw = target.shape[2:]
    target_div = target / self.flow_div

    # optical flow target shape
    c_org, h_org, w_org = target.shape[1:]
    assert c_org == 2, f'The channels ground truth must be 2, but got {c_org}'

    # over for each level: from top to bottom
    loss = 0
    for level, cur_weight in enumerate(self.weights):
      cur_pred = pred_list[level] / self.flow_div
      b, _, h, w = cur_pred.shape

      if self.resize_flow == 'downsample':
        # down sample ground truth following irr solution
        # https://github.com/visinf/irr/blob/master/losses.py#L16
        cur_target = F.adaptive_avg_pool2d(target_div, [h, w])
        if self.scale_as_level:
          cur_target[:, 0] /= (tw / w)
          cur_target[:, 1] /= (th / h)
        cur_valid = F.adaptive_max_pool2d(valid, [h, w])
      else:
        cur_target = target_div
        cur_valid = valid

      if self.resize_flow == 'upsample':
        # up sample predicted flow following pwcnet and irr solution
        # https://github.com/visinf/irr/blob/master/losses.py#L20
        # when training sparse flow dataset, as no generic
        # interpolation mode can resize a ground truth of sparse flow correctly.
        cur_pred = F.interpolate(cur_pred, size=cur_target.shape[2:], mode='bilinear', align_corners=False)
        if self.scale_as_level:
          cur_pred[:, 0] *= (tw / w)
          cur_pred[:, 1] *= (th / h)

      loss_map = endpoint_error(cur_pred, cur_target, p=self.p, q=self.q, eps=self.eps) * cur_valid

      if self.reduction == 'mean':
        loss += loss_map.sum() / (cur_valid.sum() + 1e-8) * cur_weight
      elif self.reduction == 'sum':
        loss += loss_map.sum() / b * cur_weight

    return loss


def charbonnier_loss(pred, target, q=0.2, eps=0.01):
  """Generalized Charbonnier loss function between output and ground truth.

  The loss function is
  .. math::
    loss = ((u-u_gt)^2+(v-v_gt)^2+eps)^q

  Generalized Charbonnier loss was used in LiteFlowNet when fine tuning,
  with eps=0.01 q=0.2.

  Args:
      pred (torch.Tensor): output flow map from flow_estimator
          shape(B, 2, H, W).
      target (torch.Tensor): ground truth flow map shape(B, 2, H, W).
      q (float): the exponent in charbonnier loss.
      eps (float): small constant to numerical stability when
          fine-tuning model. Defaults to 0.01.

  Returns:
      Tensor: loss map with the shape (B, H, W).
  """

  assert pred.shape == target.shape, (f'pred shape {pred.shape} does not match target shape {target.shape}.')
  diff = torch.add(pred, -target)
  loss_map = (torch.sum(diff * diff, dim=1) + eps)**q  # shape (B, H, W).
  return loss_map


class MultiLevelCharbonnierLoss(nn.Module):

  def __init__(self, q=0.2,
               eps=0.01,
               flow_div=20.,
               weights=[0.32, 0.08, 0.02, 0.01, 0.005],
               max_flow=float('inf'),
               resize_flow='downsample',
               scale_as_level=False,
               reduction='sum'):
    super(MultiLevelCharbonnierLoss, self).__init__()

    assert isinstance(q, float) and q > 0.
    self.q = q

    assert isinstance(eps, float) and eps > 0.
    self.eps = eps

    assert flow_div > 0
    self.flow_div = flow_div

    assert isinstance(weights, list)
    self.weights = weights

    assert max_flow > 0.
    self.max_flow = max_flow

    assert resize_flow in ('downsample', 'upsample')
    self.resize_flow = resize_flow

    assert isinstance(scale_as_level, bool)
    self.scale_as_level = scale_as_level

    assert reduction in ('mean', 'sum')
    self.reduction = reduction

  def forward(self, pred_list, target, valid=None):
    """Forwar function for MultiLevelCharbonnierLoss.

    Args:
        preds_list (list): Multi-level output of predicted optical flow,
            and the contain in dict is a Tensor or list of Tensor with
            shape (B, 2, H_l, W_l), where l indicates the level.
        target (Tensor): Ground truth of optical flow with shape (B, 2, H, W).
        valid (Tensor, optional): Valid mask for optical flow. Defaults to None.

    Returns:
        Tensor: value of pixel-wise generalized Charbonnier loss.

    """
    # compute valid optical flow (avoid to outlier)
    if valid is None:
      valid = torch.ones_like(target[:, 0, :, :])
    else:
      mag = torch.sum(target**2, dim=1).sqrt()
      valid = ((valid >= 0.5) & (mag < self.max_flow)).to(target)

    # normalize
    th, tw = target.shape[2:]
    target_div = target / self.flow_div

    # optical flow target shape
    c_org, h_org, w_org = target.shape[1:]
    assert c_org == 2, f'The channels ground truth must be 2, but got {c_org}'

    # over for each level: from top to bottom
    loss = 0
    for level, cur_weight in enumerate(self.weights):
      cur_pred = pred_list[level] / self.flow_div
      b, _, h, w = cur_pred.shape

      if self.resize_flow == 'downsample':
        # down sample ground truth following irr solution
        # https://github.com/visinf/irr/blob/master/losses.py#L16
        cur_target = F.adaptive_avg_pool2d(target_div, [h, w])
        if self.scale_as_level:
          cur_target[:, 0] /= (tw / w)
          cur_target[:, 1] /= (th / h)
        cur_valid = F.adaptive_max_pool2d(valid, [h, w])
      else:
        cur_target = target_div
        cur_valid = valid

      if self.resize_flow == 'upsample':
        # up sample predicted flow following pwcnet and irr solution
        # https://github.com/visinf/irr/blob/master/losses.py#L20
        # when training sparse flow dataset, as no generic
        # interpolation mode can resize a ground truth of sparse flow correctly.
        cur_pred = F.interpolate(cur_pred, size=cur_target.shape[2:], mode='bilinear', align_corners=False)
        if self.scale_as_level:
          cur_pred[:, 0] *= (tw / w)
          cur_pred[:, 1] *= (th / h)

      loss_map = charbonnier_loss(cur_pred, cur_target, q=self.q, eps=self.eps) * cur_valid

      if self.reduction == 'mean':
        loss += loss_map.sum() / (cur_valid.sum() + 1e-8) * cur_weight
      elif self.reduction == 'sum':
        loss += loss_map.sum() / b * cur_weight

    return loss
