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
"""
    Based on BEiT, timm, DINO and DeiT code bases
    https://github.com/microsoft/unilm/tree/master/beit
    https://github.com/rwightman/pytorch-image-models/tree/master/timm
    https://github.com/facebookresearch/deit
    https://github.com/facebookresearch/dino
"""
import math
import numpy as np

import torch
import torch.nn as nn
import torch.nn.functional as F

from functools import partial
from tw.nn import DropPath
from tw.nn.initialize import trunc_normal

IMAGENET_DEFAULT_MEAN = (0.485, 0.456, 0.406)
IMAGENET_DEFAULT_STD = (0.229, 0.224, 0.225)


def _cfg(url='', **kwargs):
  return {
      'url': url,
      'num_classes': 1000, 'input_size': (3, 224, 224), 'pool_size': None,
      'crop_pct': .9, 'interpolation': 'bicubic', 'fixed_input_size': True,
      'mean': (0.5, 0.5, 0.5), 'std': (0.5, 0.5, 0.5),
      'first_conv': 'patch_embed.proj', 'classifier': 'head',
      **kwargs
  }


default_cfgs = {
    # patch models (weights from official Google JAX impl)
    'vit_tiny_patch16_224': _cfg(
        url='https://storage.googleapis.com/vit_models/augreg/'
            'Ti_16-i21k-300ep-lr_0.001-aug_none-wd_0.03-do_0.0-sd_0.0--imagenet2012-steps_20k-lr_0.03-res_224.npz'),
    'vit_tiny_patch16_384': _cfg(
        url='https://storage.googleapis.com/vit_models/augreg/'
            'Ti_16-i21k-300ep-lr_0.001-aug_none-wd_0.03-do_0.0-sd_0.0--imagenet2012-steps_20k-lr_0.03-res_384.npz',
        input_size=(3, 384, 384), crop_pct=1.0),
    'vit_small_patch32_224': _cfg(
        url='https://storage.googleapis.com/vit_models/augreg/'
            'S_32-i21k-300ep-lr_0.001-aug_light1-wd_0.03-do_0.0-sd_0.0--imagenet2012-steps_20k-lr_0.03-res_224.npz'),
    'vit_small_patch32_384': _cfg(
        url='https://storage.googleapis.com/vit_models/augreg/'
            'S_32-i21k-300ep-lr_0.001-aug_light1-wd_0.03-do_0.0-sd_0.0--imagenet2012-steps_20k-lr_0.03-res_384.npz',
        input_size=(3, 384, 384), crop_pct=1.0),
    'vit_small_patch16_224': _cfg(
        url='https://storage.googleapis.com/vit_models/augreg/'
            'S_16-i21k-300ep-lr_0.001-aug_light1-wd_0.03-do_0.0-sd_0.0--imagenet2012-steps_20k-lr_0.03-res_224.npz'),
    'vit_small_patch16_384': _cfg(
        url='https://storage.googleapis.com/vit_models/augreg/'
            'S_16-i21k-300ep-lr_0.001-aug_light1-wd_0.03-do_0.0-sd_0.0--imagenet2012-steps_20k-lr_0.03-res_384.npz',
        input_size=(3, 384, 384), crop_pct=1.0),
    'vit_base_patch32_224': _cfg(
        url='https://storage.googleapis.com/vit_models/augreg/'
            'B_32-i21k-300ep-lr_0.001-aug_medium1-wd_0.03-do_0.0-sd_0.0--imagenet2012-steps_20k-lr_0.03-res_224.npz'),
    'vit_base_patch32_384': _cfg(
        url='https://storage.googleapis.com/vit_models/augreg/'
            'B_32-i21k-300ep-lr_0.001-aug_light1-wd_0.1-do_0.0-sd_0.0--imagenet2012-steps_20k-lr_0.03-res_384.npz',
        input_size=(3, 384, 384), crop_pct=1.0),
    'vit_base_patch16_224': _cfg(
        url='https://storage.googleapis.com/vit_models/augreg/'
            'B_16-i21k-300ep-lr_0.001-aug_medium1-wd_0.1-do_0.0-sd_0.0--imagenet2012-steps_20k-lr_0.01-res_224.npz'),
    'vit_base_patch16_384': _cfg(
        url='https://storage.googleapis.com/vit_models/augreg/'
            'B_16-i21k-300ep-lr_0.001-aug_medium1-wd_0.1-do_0.0-sd_0.0--imagenet2012-steps_20k-lr_0.01-res_384.npz',
        input_size=(3, 384, 384), crop_pct=1.0),
    'vit_base_patch8_224': _cfg(
        url='https://storage.googleapis.com/vit_models/augreg/'
            'B_8-i21k-300ep-lr_0.001-aug_medium1-wd_0.1-do_0.0-sd_0.0--imagenet2012-steps_20k-lr_0.01-res_224.npz'),
    'vit_large_patch32_224': _cfg(
        url='',  # no official model weights for this combo, only for in21k
    ),
    'vit_large_patch32_384': _cfg(
        url='https://github.com/rwightman/pytorch-image-models/releases/download/v0.1-vitjx/jx_vit_large_p32_384-9b920ba8.pth',
        input_size=(3, 384, 384), crop_pct=1.0),
    'vit_large_patch16_224': _cfg(
        url='https://storage.googleapis.com/vit_models/augreg/'
            'L_16-i21k-300ep-lr_0.001-aug_medium1-wd_0.1-do_0.1-sd_0.1--imagenet2012-steps_20k-lr_0.01-res_224.npz'),
    'vit_large_patch16_384': _cfg(
        url='https://storage.googleapis.com/vit_models/augreg/'
            'L_16-i21k-300ep-lr_0.001-aug_medium1-wd_0.1-do_0.1-sd_0.1--imagenet2012-steps_20k-lr_0.01-res_384.npz',
        input_size=(3, 384, 384), crop_pct=1.0),

    # patch models, imagenet21k (weights from official Google JAX impl)
    'vit_tiny_patch16_224_in21k': _cfg(
        url='https://storage.googleapis.com/vit_models/augreg/Ti_16-i21k-300ep-lr_0.001-aug_none-wd_0.03-do_0.0-sd_0.0.npz',
        num_classes=21843),
    'vit_small_patch32_224_in21k': _cfg(
        url='https://storage.googleapis.com/vit_models/augreg/S_32-i21k-300ep-lr_0.001-aug_light1-wd_0.03-do_0.0-sd_0.0.npz',
        num_classes=21843),
    'vit_small_patch16_224_in21k': _cfg(
        url='https://storage.googleapis.com/vit_models/augreg/S_16-i21k-300ep-lr_0.001-aug_light1-wd_0.03-do_0.0-sd_0.0.npz',
        num_classes=21843),
    'vit_base_patch32_224_in21k': _cfg(
        url='https://storage.googleapis.com/vit_models/augreg/B_32-i21k-300ep-lr_0.001-aug_medium1-wd_0.03-do_0.0-sd_0.0.npz',
        num_classes=21843),
    'vit_base_patch16_224_in21k': _cfg(
        url='https://storage.googleapis.com/vit_models/augreg/B_16-i21k-300ep-lr_0.001-aug_medium1-wd_0.1-do_0.0-sd_0.0.npz',
        num_classes=21843),
    'vit_base_patch8_224_in21k': _cfg(
        url='https://storage.googleapis.com/vit_models/augreg/B_8-i21k-300ep-lr_0.001-aug_medium1-wd_0.1-do_0.0-sd_0.0.npz',
        num_classes=21843),
    'vit_large_patch32_224_in21k': _cfg(
        url='https://github.com/rwightman/pytorch-image-models/releases/download/v0.1-vitjx/jx_vit_large_patch32_224_in21k-9046d2e7.pth',
        num_classes=21843),
    'vit_large_patch16_224_in21k': _cfg(
        url='https://storage.googleapis.com/vit_models/augreg/L_16-i21k-300ep-lr_0.001-aug_medium1-wd_0.1-do_0.1-sd_0.1.npz',
        num_classes=21843),
    'vit_huge_patch14_224_in21k': _cfg(
        url='https://storage.googleapis.com/vit_models/imagenet21k/ViT-H_14.npz',
        hf_hub='timm/vit_huge_patch14_224_in21k',
        num_classes=21843),

    # SAM trained models (https://arxiv.org/abs/2106.01548)
    'vit_base_patch32_sam_224': _cfg(
        url='https://storage.googleapis.com/vit_models/sam/ViT-B_32.npz'),
    'vit_base_patch16_sam_224': _cfg(
        url='https://storage.googleapis.com/vit_models/sam/ViT-B_16.npz'),

    # deit models (FB weights)
    'deit_tiny_patch16_224': _cfg(
        url='https://dl.fbaipublicfiles.com/deit/deit_tiny_patch16_224-a1311bcf.pth',
        mean=IMAGENET_DEFAULT_MEAN, std=IMAGENET_DEFAULT_STD),
    'deit_small_patch16_224': _cfg(
        url='https://dl.fbaipublicfiles.com/deit/deit_small_patch16_224-cd65a155.pth',
        mean=IMAGENET_DEFAULT_MEAN, std=IMAGENET_DEFAULT_STD),
    'deit_base_patch16_224': _cfg(
        url='https://dl.fbaipublicfiles.com/deit/deit_base_patch16_224-b5f2ef4d.pth',
        mean=IMAGENET_DEFAULT_MEAN, std=IMAGENET_DEFAULT_STD),
    'deit_base_patch16_384': _cfg(
        url='https://dl.fbaipublicfiles.com/deit/deit_base_patch16_384-8de9b5d1.pth',
        mean=IMAGENET_DEFAULT_MEAN, std=IMAGENET_DEFAULT_STD, input_size=(3, 384, 384), crop_pct=1.0),
    'deit_tiny_distilled_patch16_224': _cfg(
        url='https://dl.fbaipublicfiles.com/deit/deit_tiny_distilled_patch16_224-b40b3cf7.pth',
        mean=IMAGENET_DEFAULT_MEAN, std=IMAGENET_DEFAULT_STD, classifier=('head', 'head_dist')),
    'deit_small_distilled_patch16_224': _cfg(
        url='https://dl.fbaipublicfiles.com/deit/deit_small_distilled_patch16_224-649709d9.pth',
        mean=IMAGENET_DEFAULT_MEAN, std=IMAGENET_DEFAULT_STD, classifier=('head', 'head_dist')),
    'deit_base_distilled_patch16_224': _cfg(
        url='https://dl.fbaipublicfiles.com/deit/deit_base_distilled_patch16_224-df68dfff.pth',
        mean=IMAGENET_DEFAULT_MEAN, std=IMAGENET_DEFAULT_STD, classifier=('head', 'head_dist')),
    'deit_base_distilled_patch16_384': _cfg(
        url='https://dl.fbaipublicfiles.com/deit/deit_base_distilled_patch16_384-d0272ac0.pth',
        mean=IMAGENET_DEFAULT_MEAN, std=IMAGENET_DEFAULT_STD, input_size=(3, 384, 384), crop_pct=1.0,
        classifier=('head', 'head_dist')),

    # ViT ImageNet-21K-P pretraining by MILL
    'vit_base_patch16_224_miil_in21k': _cfg(
        url='https://miil-public-eu.oss-eu-central-1.aliyuncs.com/model-zoo/ImageNet_21K_P/models/timm/vit_base_patch16_224_in21k_miil.pth',
        mean=(0, 0, 0), std=(1, 1, 1), crop_pct=0.875, interpolation='bilinear', num_classes=11221,
    ),
    'vit_base_patch16_224_miil': _cfg(
        url='https://miil-public-eu.oss-eu-central-1.aliyuncs.com/model-zoo/ImageNet_21K_P/models/timm'
            '/vit_base_patch16_224_1k_miil_84_4.pth',
        mean=(0, 0, 0), std=(1, 1, 1), crop_pct=0.875, interpolation='bilinear',
    ),
}


class Mlp(nn.Module):
  def __init__(self, in_features, hidden_features=None, out_features=None, act_layer=nn.GELU, drop=0.):
    super().__init__()
    out_features = out_features or in_features
    hidden_features = hidden_features or in_features
    self.fc1 = nn.Linear(in_features, hidden_features)
    self.act = act_layer()
    self.fc2 = nn.Linear(hidden_features, out_features)
    self.drop = nn.Dropout(drop)

  def forward(self, x):
    x = self.fc1(x)
    x = self.act(x)
    # x = self.drop(x)
    # commit this for the orignal BERT implement
    x = self.fc2(x)
    x = self.drop(x)
    return x


class Attention(nn.Module):
  def __init__(
          self, dim, num_heads=8, qkv_bias=False, qk_scale=None, attn_drop=0.,
          proj_drop=0., attn_head_dim=None):
    super().__init__()
    self.num_heads = num_heads
    head_dim = dim // num_heads
    if attn_head_dim is not None:
      head_dim = attn_head_dim
    all_head_dim = head_dim * self.num_heads
    self.scale = qk_scale or head_dim ** -0.5

    self.qkv = nn.Linear(dim, all_head_dim * 3, bias=False)
    if qkv_bias:
      self.q_bias = nn.Parameter(torch.zeros(all_head_dim))
      self.v_bias = nn.Parameter(torch.zeros(all_head_dim))
    else:
      self.q_bias = None
      self.v_bias = None

    self.attn_drop = nn.Dropout(attn_drop)
    self.proj = nn.Linear(all_head_dim, dim)
    self.proj_drop = nn.Dropout(proj_drop)

  def forward(self, x):
    B, N, C = x.shape
    qkv_bias = None
    if self.q_bias is not None:
      qkv_bias = torch.cat((self.q_bias, torch.zeros_like(self.v_bias, requires_grad=False), self.v_bias))
    # qkv = self.qkv(x).reshape(B, N, 3, self.num_heads, C // self.num_heads).permute(2, 0, 3, 1, 4)
    qkv = F.linear(input=x, weight=self.qkv.weight, bias=qkv_bias)
    qkv = qkv.reshape(B, N, 3, self.num_heads, -1).permute(2, 0, 3, 1, 4)
    q, k, v = qkv[0], qkv[1], qkv[2]   # make torchscript happy (cannot use tensor as tuple)

    q = q * self.scale
    attn = (q @ k.transpose(-2, -1))

    attn = attn.softmax(dim=-1)
    attn = self.attn_drop(attn)

    x = (attn @ v).transpose(1, 2).reshape(B, N, -1)
    x = self.proj(x)
    x = self.proj_drop(x)
    return x


class Block(nn.Module):

  def __init__(self, dim, num_heads, mlp_ratio=4., qkv_bias=False, qk_scale=None, drop=0., attn_drop=0.,
               drop_path=0., init_values=None, act_layer=nn.GELU, norm_layer=nn.LayerNorm,
               attn_head_dim=None):
    super().__init__()
    self.norm1 = norm_layer(dim)
    self.attn = Attention(
        dim, num_heads=num_heads, qkv_bias=qkv_bias, qk_scale=qk_scale,
        attn_drop=attn_drop, proj_drop=drop, attn_head_dim=attn_head_dim)
    # NOTE: drop path for stochastic depth, we shall see if this is better than dropout here
    self.drop_path = DropPath(drop_path) if drop_path > 0. else nn.Identity()
    self.norm2 = norm_layer(dim)
    mlp_hidden_dim = int(dim * mlp_ratio)
    self.mlp = Mlp(in_features=dim, hidden_features=mlp_hidden_dim, act_layer=act_layer, drop=drop)

    if init_values > 0:
      self.gamma_1 = nn.Parameter(init_values * torch.ones((dim)), requires_grad=True)
      self.gamma_2 = nn.Parameter(init_values * torch.ones((dim)), requires_grad=True)
    else:
      self.gamma_1, self.gamma_2 = None, None

  def forward(self, x):
    if self.gamma_1 is None:
      x = x + self.drop_path(self.attn(self.norm1(x)))
      x = x + self.drop_path(self.mlp(self.norm2(x)))
    else:
      x = x + self.drop_path(self.gamma_1 * self.attn(self.norm1(x)))
      x = x + self.drop_path(self.gamma_2 * self.mlp(self.norm2(x)))
    return x


class PatchEmbed(nn.Module):
  """ Image to Patch Embedding
  """

  def __init__(self, img_size=224, patch_size=16, in_chans=3, embed_dim=768):
    super().__init__()
    img_size = (img_size, img_size)
    patch_size = (patch_size, patch_size)
    num_patches = (img_size[1] // patch_size[1]) * (img_size[0] // patch_size[0])
    self.patch_shape = (img_size[0] // patch_size[0], img_size[1] // patch_size[1])
    self.img_size = img_size
    self.patch_size = patch_size
    self.num_patches = num_patches

    self.proj = nn.Conv2d(in_chans, embed_dim, kernel_size=patch_size, stride=patch_size)

  def forward(self, x, **kwargs):
    B, C, H, W = x.shape
    # FIXME look at relaxing size constraints
    assert H == self.img_size[0] and W == self.img_size[1], \
        f"Input image size ({H}*{W}) doesn't match model ({self.img_size[0]}*{self.img_size[1]})."
    x = self.proj(x).flatten(2).transpose(1, 2)
    return x

# sin-cos position encoding
# https://github.com/jadore801120/attention-is-all-you-need-pytorch/blob/master/transformer/Models.py#L31


def get_sinusoid_encoding_table(n_position, d_hid):
  ''' Sinusoid position encoding table '''
  # TODO: make it with torch instead of numpy
  def get_position_angle_vec(position):
    return [position / np.power(10000, 2 * (hid_j // 2) / d_hid) for hid_j in range(d_hid)]

  sinusoid_table = np.array([get_position_angle_vec(pos_i) for pos_i in range(n_position)])
  sinusoid_table[:, 0::2] = np.sin(sinusoid_table[:, 0::2])  # dim 2i
  sinusoid_table[:, 1::2] = np.cos(sinusoid_table[:, 1::2])  # dim 2i+1

  return torch.FloatTensor(sinusoid_table).unsqueeze(0)

#!<-------------------------------------------------------------------------------------------------
#!< VISION TRANSFORMER
#!<-------------------------------------------------------------------------------------------------


class VisionTransformer(nn.Module):
  """ Vision Transformer with support for patch or hybrid CNN input stage
  """
  MEAN = [0.5, 0.5, 0.5]
  STD = [0.5, 0.5, 0.5]
  SIZE = [224, 224]
  SCALE = 255
  CROP = 0.9

  def __init__(self,
               img_size=224,
               patch_size=16,
               in_chans=3,
               num_classes=1000,
               embed_dim=768,
               depth=12,
               num_heads=12,
               mlp_ratio=4.,
               qkv_bias=False,
               qk_scale=None,
               drop_rate=0.,
               attn_drop_rate=0.,
               drop_path_rate=0.,
               norm_layer=nn.LayerNorm,
               init_values=0.,
               use_learnable_pos_emb=False,
               init_scale=0.,
               use_mean_pooling=True):
    super().__init__()
    self.num_classes = num_classes
    self.num_features = self.embed_dim = embed_dim  # num_features for consistency with other models

    self.patch_embed = PatchEmbed(
        img_size=img_size, patch_size=patch_size, in_chans=in_chans, embed_dim=embed_dim)
    num_patches = self.patch_embed.num_patches

    # self.cls_token = nn.Parameter(torch.zeros(1, 1, embed_dim))
    if use_learnable_pos_emb:
      self.pos_embed = nn.Parameter(torch.zeros(1, num_patches, embed_dim))
    else:
      # sine-cosine positional embeddings is on the way
      self.pos_embed = get_sinusoid_encoding_table(num_patches, embed_dim)

    self.pos_drop = nn.Dropout(p=drop_rate)

    dpr = [x.item() for x in torch.linspace(0, drop_path_rate, depth)]  # stochastic depth decay rule
    self.blocks = nn.ModuleList([
        Block(
            dim=embed_dim, num_heads=num_heads, mlp_ratio=mlp_ratio, qkv_bias=qkv_bias, qk_scale=qk_scale,
            drop=drop_rate, attn_drop=attn_drop_rate, drop_path=dpr[i], norm_layer=norm_layer,
            init_values=init_values)
        for i in range(depth)])
    self.norm = nn.Identity() if use_mean_pooling else norm_layer(embed_dim)
    self.fc_norm = norm_layer(embed_dim) if use_mean_pooling else None
    self.head = nn.Linear(embed_dim, num_classes) if num_classes > 0 else nn.Identity()

    if use_learnable_pos_emb:
      trunc_normal(self.pos_embed, std=.02)

    # trunc_normal(self.cls_token, std=.02)
    trunc_normal(self.head.weight, std=.02)
    self.apply(self._init_weights)

    self.head.weight.data.mul_(init_scale)
    self.head.bias.data.mul_(init_scale)

  def _init_weights(self, m):
    if isinstance(m, nn.Linear):
      trunc_normal(m.weight, std=.02)
      if isinstance(m, nn.Linear) and m.bias is not None:
        nn.init.constant_(m.bias, 0)
    elif isinstance(m, nn.LayerNorm):
      nn.init.constant_(m.bias, 0)
      nn.init.constant_(m.weight, 1.0)

  def get_num_layers(self):
    return len(self.blocks)

  @torch.jit.ignore
  def no_weight_decay(self):
    return {'pos_embed', 'cls_token'}

  def get_classifier(self):
    return self.head

  def reset_classifier(self, num_classes, global_pool=''):
    self.num_classes = num_classes
    self.head = nn.Linear(self.embed_dim, num_classes) if num_classes > 0 else nn.Identity()

  def forward_features(self, x):
    x = self.patch_embed(x)
    B, _, _ = x.size()

    # cls_tokens = self.cls_token.expand(batch_size, -1, -1)  # stole cls_tokens impl from Phil Wang, thanks
    # x = torch.cat((cls_tokens, x), dim=1)
    if self.pos_embed is not None:
      x = x + self.pos_embed.expand(B, -1, -1).type_as(x).to(x.device).clone().detach()
    x = self.pos_drop(x)

    for blk in self.blocks:
      x = blk(x)

    x = self.norm(x)
    if self.fc_norm is not None:
      # return self.fc_norm(x[:, 1:].mean(1))
      return self.fc_norm(x.mean(1))
    else:
      return x[:, 0]

  def forward(self, x):
    x = self.forward_features(x)
    x = self.head(x)
    return x


def vit_small_patch16_224(pretrained=False, **kwargs):
  model = VisionTransformer(
      patch_size=16, embed_dim=384, depth=12, num_heads=6, mlp_ratio=4, qkv_bias=True,
      norm_layer=partial(nn.LayerNorm, eps=1e-6), **kwargs)
  model.default_cfg = _cfg()
  return model


def vit_base_patch16_224(pretrained=False, **kwargs):
  model = VisionTransformer(
      patch_size=16, embed_dim=768, depth=12, num_heads=12, mlp_ratio=4, qkv_bias=True,
      norm_layer=partial(nn.LayerNorm, eps=1e-6), **kwargs)
  model.default_cfg = _cfg()
  return model


def vit_base_patch16_384(pretrained=False, **kwargs):
  model = VisionTransformer(
      img_size=384, patch_size=16, embed_dim=768, depth=12, num_heads=12, mlp_ratio=4, qkv_bias=True,
      norm_layer=partial(nn.LayerNorm, eps=1e-6), **kwargs)
  model.default_cfg = _cfg()
  return model


def vit_large_patch16_224(pretrained=False, **kwargs):
  model = VisionTransformer(
      patch_size=16, embed_dim=1024, depth=24, num_heads=16, mlp_ratio=4, qkv_bias=True,
      norm_layer=partial(nn.LayerNorm, eps=1e-6), **kwargs)
  model.default_cfg = _cfg()
  return model


def vit_large_patch16_384(pretrained=False, **kwargs):
  model = VisionTransformer(
      img_size=384, patch_size=16, embed_dim=1024, depth=24, num_heads=16, mlp_ratio=4, qkv_bias=True,
      norm_layer=partial(nn.LayerNorm, eps=1e-6), **kwargs)
  model.default_cfg = _cfg()
  return model


def vit_large_patch16_512(pretrained=False, **kwargs):
  model = VisionTransformer(
      img_size=512, patch_size=16, embed_dim=1024, depth=24, num_heads=16, mlp_ratio=4, qkv_bias=True,
      norm_layer=partial(nn.LayerNorm, eps=1e-6), **kwargs)
  model.default_cfg = _cfg()
  return model


#!<-------------------------------------------------------------------------------------------------
#!< PRETRAIN VISION TRANSFORMER
#!<-------------------------------------------------------------------------------------------------


class PretrainVisionTransformerEncoder(nn.Module):
  """ Vision Transformer with support for patch or hybrid CNN input stage
  """

  def __init__(self, img_size=224, patch_size=16, in_chans=3, num_classes=0, embed_dim=768, depth=12,
               num_heads=12, mlp_ratio=4., qkv_bias=False, qk_scale=None, drop_rate=0., attn_drop_rate=0.,
               drop_path_rate=0., norm_layer=nn.LayerNorm, init_values=None,
               use_learnable_pos_emb=False):
    super().__init__()
    self.num_classes = num_classes
    self.num_features = self.embed_dim = embed_dim  # num_features for consistency with other models

    self.patch_embed = PatchEmbed(
        img_size=img_size, patch_size=patch_size, in_chans=in_chans, embed_dim=embed_dim)
    num_patches = self.patch_embed.num_patches

    # TODO: Add the cls token
    # self.cls_token = nn.Parameter(torch.zeros(1, 1, embed_dim))
    if use_learnable_pos_emb:
      self.pos_embed = nn.Parameter(torch.zeros(1, num_patches + 1, embed_dim))
    else:
      # sine-cosine positional embeddings
      self.pos_embed = get_sinusoid_encoding_table(num_patches, embed_dim)

    dpr = [x.item() for x in torch.linspace(0, drop_path_rate, depth)]  # stochastic depth decay rule
    self.blocks = nn.ModuleList([
        Block(
            dim=embed_dim, num_heads=num_heads, mlp_ratio=mlp_ratio, qkv_bias=qkv_bias, qk_scale=qk_scale,
            drop=drop_rate, attn_drop=attn_drop_rate, drop_path=dpr[i], norm_layer=norm_layer,
            init_values=init_values)
        for i in range(depth)])
    self.norm = norm_layer(embed_dim)
    self.head = nn.Linear(embed_dim, num_classes) if num_classes > 0 else nn.Identity()

    if use_learnable_pos_emb:
      trunc_normal(self.pos_embed, std=.02)

    # trunc_normal(self.cls_token, std=.02)
    self.apply(self._init_weights)

  def _init_weights(self, m):
    if isinstance(m, nn.Linear):
      nn.init.xavier_uniform_(m.weight)
      if isinstance(m, nn.Linear) and m.bias is not None:
        nn.init.constant_(m.bias, 0)
    elif isinstance(m, nn.LayerNorm):
      nn.init.constant_(m.bias, 0)
      nn.init.constant_(m.weight, 1.0)

  def get_num_layers(self):
    return len(self.blocks)

  @torch.jit.ignore
  def no_weight_decay(self):
    return {'pos_embed', 'cls_token'}

  def get_classifier(self):
    return self.head

  def reset_classifier(self, num_classes, global_pool=''):
    self.num_classes = num_classes
    self.head = nn.Linear(self.embed_dim, num_classes) if num_classes > 0 else nn.Identity()

  def forward_features(self, x, mask):
    x = self.patch_embed(x)

    # cls_tokens = self.cls_token.expand(batch_size, -1, -1)
    # x = torch.cat((cls_tokens, x), dim=1)
    x = x + self.pos_embed.type_as(x).to(x.device).clone().detach()

    B, _, C = x.shape
    x_vis = x[~mask].reshape(B, -1, C)  # ~mask means visible

    for blk in self.blocks:
      x_vis = blk(x_vis)

    x_vis = self.norm(x_vis)
    return x_vis

  def forward(self, x, mask):
    x = self.forward_features(x, mask)
    x = self.head(x)
    return x


class PretrainVisionTransformerDecoder(nn.Module):
  """ Vision Transformer with support for patch or hybrid CNN input stage
  """

  def __init__(self, patch_size=16, num_classes=768, embed_dim=768, depth=12,
               num_heads=12, mlp_ratio=4., qkv_bias=False, qk_scale=None, drop_rate=0., attn_drop_rate=0.,
               drop_path_rate=0., norm_layer=nn.LayerNorm, init_values=None, num_patches=196,
               ):
    super().__init__()
    self.num_classes = num_classes
    assert num_classes == 3 * patch_size ** 2
    self.num_features = self.embed_dim = embed_dim  # num_features for consistency with other models
    self.patch_size = patch_size

    dpr = [x.item() for x in torch.linspace(0, drop_path_rate, depth)]  # stochastic depth decay rule
    self.blocks = nn.ModuleList([
        Block(
            dim=embed_dim, num_heads=num_heads, mlp_ratio=mlp_ratio, qkv_bias=qkv_bias, qk_scale=qk_scale,
            drop=drop_rate, attn_drop=attn_drop_rate, drop_path=dpr[i], norm_layer=norm_layer,
            init_values=init_values)
        for i in range(depth)])
    self.norm = norm_layer(embed_dim)
    self.head = nn.Linear(embed_dim, num_classes) if num_classes > 0 else nn.Identity()

    self.apply(self._init_weights)

  def _init_weights(self, m):
    if isinstance(m, nn.Linear):
      nn.init.xavier_uniform_(m.weight)
      if isinstance(m, nn.Linear) and m.bias is not None:
        nn.init.constant_(m.bias, 0)
    elif isinstance(m, nn.LayerNorm):
      nn.init.constant_(m.bias, 0)
      nn.init.constant_(m.weight, 1.0)

  def get_num_layers(self):
    return len(self.blocks)

  @torch.jit.ignore
  def no_weight_decay(self):
    return {'pos_embed', 'cls_token'}

  def get_classifier(self):
    return self.head

  def reset_classifier(self, num_classes, global_pool=''):
    self.num_classes = num_classes
    self.head = nn.Linear(self.embed_dim, num_classes) if num_classes > 0 else nn.Identity()

  def forward(self, x, return_token_num):
    for blk in self.blocks:
      x = blk(x)

    if return_token_num > 0:
      x = self.head(self.norm(x[:, -return_token_num:]))  # only return the mask tokens predict pixels
    else:
      x = self.head(self.norm(x))  # [B, N, 3*16^2]

    return x


class PretrainVisionTransformer(nn.Module):
  """ Vision Transformer with support for patch or hybrid CNN input stage
  """

  def __init__(self,
               img_size=224,
               patch_size=16,
               encoder_in_chans=3,
               encoder_num_classes=0,
               encoder_embed_dim=768,
               encoder_depth=12,
               encoder_num_heads=12,
               decoder_num_classes=768,
               decoder_embed_dim=512,
               decoder_depth=8,
               decoder_num_heads=8,
               mlp_ratio=4.,
               qkv_bias=False,
               qk_scale=None,
               drop_rate=0.,
               attn_drop_rate=0.,
               drop_path_rate=0.,
               norm_layer=nn.LayerNorm,
               init_values=0.,
               use_learnable_pos_emb=False,
               num_classes=0,  # avoid the error from create_fn in timm
               in_chans=0,  # avoid the error from create_fn in timm
               ):
    super().__init__()
    self.encoder = PretrainVisionTransformerEncoder(
        img_size=img_size,
        patch_size=patch_size,
        in_chans=encoder_in_chans,
        num_classes=encoder_num_classes,
        embed_dim=encoder_embed_dim,
        depth=encoder_depth,
        num_heads=encoder_num_heads,
        mlp_ratio=mlp_ratio,
        qkv_bias=qkv_bias,
        qk_scale=qk_scale,
        drop_rate=drop_rate,
        attn_drop_rate=attn_drop_rate,
        drop_path_rate=drop_path_rate,
        norm_layer=norm_layer,
        init_values=init_values,
        use_learnable_pos_emb=use_learnable_pos_emb)

    self.decoder = PretrainVisionTransformerDecoder(
        patch_size=patch_size,
        num_patches=self.encoder.patch_embed.num_patches,
        num_classes=decoder_num_classes,
        embed_dim=decoder_embed_dim,
        depth=decoder_depth,
        num_heads=decoder_num_heads,
        mlp_ratio=mlp_ratio,
        qkv_bias=qkv_bias,
        qk_scale=qk_scale,
        drop_rate=drop_rate,
        attn_drop_rate=attn_drop_rate,
        drop_path_rate=drop_path_rate,
        norm_layer=norm_layer,
        init_values=init_values)

    self.encoder_to_decoder = nn.Linear(encoder_embed_dim, decoder_embed_dim, bias=False)

    self.mask_token = nn.Parameter(torch.zeros(1, 1, decoder_embed_dim))

    self.pos_embed = get_sinusoid_encoding_table(self.encoder.patch_embed.num_patches, decoder_embed_dim)

    trunc_normal(self.mask_token, std=.02)

  def _init_weights(self, m):
    if isinstance(m, nn.Linear):
      nn.init.xavier_uniform_(m.weight)
      if isinstance(m, nn.Linear) and m.bias is not None:
        nn.init.constant_(m.bias, 0)
    elif isinstance(m, nn.LayerNorm):
      nn.init.constant_(m.bias, 0)
      nn.init.constant_(m.weight, 1.0)

  def get_num_layers(self):
    return len(self.blocks)

  @torch.jit.ignore
  def no_weight_decay(self):
    return {'pos_embed', 'cls_token', 'mask_token'}

  def forward(self, x, mask):

    x_vis = self.encoder(x, mask)  # [B, N_vis, C_e]
    x_vis = self.encoder_to_decoder(x_vis)  # [B, N_vis, C_d]

    B, N, C = x_vis.shape

    # we don't unshuffle the correct visible token order,
    # but shuffle the pos embedding accorddingly.
    expand_pos_embed = self.pos_embed.expand(B, -1, -1).type_as(x).to(x.device).clone().detach()
    pos_emd_vis = expand_pos_embed[~mask].reshape(B, -1, C)
    pos_emd_mask = expand_pos_embed[mask].reshape(B, -1, C)
    x_full = torch.cat([x_vis + pos_emd_vis, self.mask_token + pos_emd_mask], dim=1)
    # notice: if N_mask==0, the shape of x is [B, N_mask, 3 * 16 * 16]
    x = self.decoder(x_full, pos_emd_mask.shape[1])  # [B, N_mask, 3 * 16 * 16]

    return x


def pretrain_mae_small_patch16_224(pretrained=False, **kwargs):
  model = PretrainVisionTransformer(
      img_size=224,
      patch_size=16,
      encoder_embed_dim=384,
      encoder_depth=12,
      encoder_num_heads=6,
      encoder_num_classes=0,
      decoder_num_classes=768,
      decoder_embed_dim=192,
      decoder_depth=4,
      decoder_num_heads=3,
      mlp_ratio=4,
      qkv_bias=True,
      norm_layer=partial(nn.LayerNorm, eps=1e-6),
      **kwargs)
  model.default_cfg = _cfg()
  if pretrained:
    checkpoint = torch.load(
        kwargs["init_ckpt"], map_location="cpu"
    )
    model.load_state_dict(checkpoint["model"])
  return model


def pretrain_mae_base_patch16_224(pretrained=False, **kwargs):
  model = PretrainVisionTransformer(
      img_size=224,
      patch_size=16,
      encoder_embed_dim=768,
      encoder_depth=12,
      encoder_num_heads=12,
      encoder_num_classes=0,
      decoder_num_classes=768,
      decoder_embed_dim=384,
      decoder_depth=4,
      decoder_num_heads=6,
      mlp_ratio=4,
      qkv_bias=True,
      norm_layer=partial(nn.LayerNorm, eps=1e-6),
      **kwargs)
  model.default_cfg = _cfg()
  if pretrained:
    checkpoint = torch.load(
        kwargs["init_ckpt"], map_location="cpu"
    )
    model.load_state_dict(checkpoint["model"])
  return model


def pretrain_mae_large_patch16_224(pretrained=False, **kwargs):
  model = PretrainVisionTransformer(
      img_size=224,
      patch_size=16,
      encoder_embed_dim=1024,
      encoder_depth=24,
      encoder_num_heads=16,
      encoder_num_classes=0,
      decoder_num_classes=768,
      decoder_embed_dim=512,
      decoder_depth=8,
      decoder_num_heads=8,
      mlp_ratio=4,
      qkv_bias=True,
      norm_layer=partial(nn.LayerNorm, eps=1e-6),
      **kwargs)
  model.default_cfg = _cfg()
  if pretrained:
    checkpoint = torch.load(
        kwargs["init_ckpt"], map_location="cpu"
    )
    model.load_state_dict(checkpoint["model"])
  return model
