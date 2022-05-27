import torch
import numpy as np
import torch.nn.functional as F
from torch import nn
from einops import rearrange
from typing import List, Dict

from .utils import initialize_weights


def get_num_features(backbone_name: str, model_type: str = '') -> List:
    """
    Gives a List of features present in the last 3 blocks of the backbone model
    :param backbone_name: name of the backbone model e.g. 'resnet18' | 'resnet50'
    :param model_type: Type of FCN model(fcn32s | fcn16s | fcn8s)
    :return: List of number of features extracted from last 3 blocks of the backbone model
    """

    if 'resnet18' in backbone_name.lower():
        num_features = [64, 128, 256, 512]
    else:
        num_features = [256, 512, 1024, 2048]

    if 'fcn8s' in model_type.lower():
        num_features = num_features[-3:]
    elif 'fcn16s' in model_type.lower():
        num_features = num_features[-2:]
    elif 'fcn32s' in model_type.lower():
        num_features = num_features[-1:]
    return num_features


class FCN(nn.Module):
    """ Base Class for all FCN Modules """

    def __init__(self,
                 num_classes: int,
                 backbone_name: str,
                 backbone: nn.Module = None,
                 model_type: str = 'fcn8s'):
        super().__init__()
        self.backbone = backbone
        num_features = get_num_features(backbone_name, model_type)
        self.classifier = nn.ModuleList([
            self.upsample_head(num_feature, num_classes)
            for num_feature in num_features
        ])

    def set_backbone(self, backbone):
        self.backbone = backbone

    def upsample_head(self, in_channels: int, channels: int) -> nn.Module:
        """
        :param in_channels: Number of channels in Input
        :param channels: Desired Number of channels in Output
        :return: torch.nn.Module
        """
        inter_channels = in_channels // 8
        layers = [
            nn.Conv2d(in_channels,
                      inter_channels,
                      kernel_size=3,
                      padding=1,
                      bias=False),
            nn.BatchNorm2d(inter_channels),
            nn.ReLU(),
            nn.Conv2d(inter_channels,
                      inter_channels,
                      kernel_size=3,
                      padding=1,
                      bias=False),
            nn.BatchNorm2d(inter_channels),
            nn.ReLU(),
            nn.Conv2d(inter_channels, channels, kernel_size=1),
        ]
        return nn.Sequential(*layers)

    def forward(self, x):
        """ Abstract method to be implemented by child classes"""
        pass


class FCN32s(FCN):
    """ Child FCN class that generates the output only using feature maps from last layer of the backbone """
    def __init__(self,
                 num_classes: int,
                 backbone_name: str,
                 backbone: nn.Module = None):
        super().__init__(num_classes=num_classes,
                         backbone_name=backbone_name,
                         backbone=backbone,
                         model_type='fcn32s')

    def forward(self, x):
        """ Forward pass through FCN32s"""
        h, w = x.shape[-2:]
        if self.backbone is None:
            raise ValueError('Backbone must be set.')
        with torch.no_grad():
            features = self.backbone(x)
        return self.bilinear_upsample(features, h, w)

    def bilinear_upsample(self, features: Dict, h: int, w: int):
        """
        :param features: Backbone's output feature map dict
        :param h: Desired Output Height
        :param w: Desired output Width
        :return: Upsample output of size N x C x H x W where C is the number of classes
        """
        out32s = self.classifier[-1](features['feat5'])
        upsampled_out = F.interpolate(out32s,
                                      size=(h, w),
                                      mode='bilinear',
                                      align_corners=False)
        return upsampled_out


class FCN16s(FCN):
    """ Child FCN class that generates the output only using feature maps from last two layers of the backbone """
    def __init__(self,
                 num_classes: int,
                 backbone_name: str,
                 backbone: nn.Module = None):
        super().__init__(num_classes=num_classes,
                         backbone_name=backbone_name,
                         backbone=backbone,
                         model_type='fcn16s')

    def forward(self, x):
        """ Forward pass through FCN16s"""
        h, w = x.shape[-2:]
        if self.backbone is None:
            raise ValueError('Backbone must be set.')
        with torch.no_grad():
            features = self.backbone(x)
        return self.bilinear_upsample(features, h, w)

    def bilinear_upsample(self, features: Dict, h: int, w: int):
        """
        Bilinear upsample after merging the last 2 feature maps
        :param features: Backbone's output feature map dict
        :param h: Desired Output Height
        :param w: Desired output Width
        :return: Upsample output of size N x C x H x W where C is the number of classes
        """
        out32s = self.classifier[-1](features['feat5'])
        out16s = self.classifier[-2](features['feat4'])
        upsampled_out32s = F.interpolate(out32s,
                                         size=(h // 16, w // 16),
                                         mode='bilinear',
                                         align_corners=False)
        out = upsampled_out32s + out16s
        upsampled_out = F.interpolate(out,
                                      size=(h, w),
                                      mode='bilinear',
                                      align_corners=False)
        return upsampled_out


class FCN8s(FCN):
    """ Child FCN class that generates the output only using feature maps from last three layers of the backbone """
    def __init__(self,
                 num_classes: int,
                 backbone_name: str,
                 backbone: nn.Module = None):
        super().__init__(num_classes=num_classes,
                         backbone_name=backbone_name,
                         backbone=backbone,
                         model_type='fcn8s')

    def forward(self, x):
        """ Forward pass through FCN16s"""
        h, w = x.shape[-2:]
        if self.backbone is None:
            raise ValueError('Backbone must be set.')
        with torch.no_grad():
            features = self.backbone(x)
        return self.bilinear_upsample(features, h, w)

    def bilinear_upsample(self, features: Dict, h: int, w: int):
        """
        Bilinear upsample after merging the last 3 feature maps
        :param features: Backbone's output feature map dict
        :param h: Desired Output Height
        :param w: Desired output Width
        :return: Upsample output of size N x C x H x W where C is the number of classes
        """
        out32s = self.classifier[-1](features['feat5'])
        out16s = self.classifier[-2](features['feat4'])
        out8s = self.classifier[-3](features['feat3'])
        upsampled_out32s = F.interpolate(out32s,
                                         size=(h // 16, w // 16),
                                         mode='bilinear',
                                         align_corners=False)
        out = upsampled_out32s + out16s
        upsampled_out16s = F.interpolate(out,
                                         size=(h // 8, w // 8),
                                         mode='bilinear',
                                         align_corners=False)
        out = upsampled_out16s + out8s
        upsampled_out = F.interpolate(out,
                                      size=(h, w),
                                      mode='bilinear',
                                      align_corners=False)
        return upsampled_out


class DecoderConv(nn.Module):
    """Conv layers on top of the embeddings for segmentation task."""
    def __init__(self, dim_in, num_labels=10):
        super(DecoderConv, self).__init__()
        self.num_labels = num_labels
        self.conv = nn.Conv2d(dim_in,
                              num_labels,
                              kernel_size=1,
                              padding='same')

    def forward(self, x, im_size):
        H, W = im_size
        x = self.conv(x)
        masks = F.interpolate(x, size=(H, W), mode="bilinear")

        return masks


class DecoderLinear(nn.Module):
    def __init__(self, n_cls, patch_size, d_encoder):
        super().__init__()
        self.d_encoder = d_encoder
        self.patch_size = patch_size
        self.n_cls = n_cls

        self.head = nn.Linear(self.d_encoder, n_cls)
        # initialize weights
        initialize_weights(self)

    def forward(self, x, im_size):
        H, W = im_size
        GS = H // self.patch_size
        x = self.head(x)
        masks = rearrange(x, "b (h w) c -> b c h w", h=GS)
        masks = F.interpolate(masks, size=(H, W), mode="bilinear")

        return masks


class Conv2dReLU(nn.Sequential):
    def __init__(
        self,
        in_channels,
        out_channels,
        kernel_size,
        padding=0,
        stride=1,
        use_batchnorm=True,
    ):
        conv = nn.Conv2d(
            in_channels,
            out_channels,
            kernel_size,
            stride=stride,
            padding=padding,
            bias=not use_batchnorm,
        )
        relu = nn.ReLU(inplace=True)

        bn = nn.BatchNorm2d(out_channels)

        super(Conv2dReLU, self).__init__(conv, bn, relu)


class DecoderBlock(nn.Module):
    def __init__(
        self,
        in_channels,
        out_channels,
        skip_channels=0,
        use_batchnorm=True,
    ):
        super().__init__()
        self.conv1 = Conv2dReLU(
            in_channels + skip_channels,
            out_channels,
            kernel_size=3,
            padding=1,
            use_batchnorm=use_batchnorm,
        )
        self.conv2 = Conv2dReLU(
            out_channels,
            out_channels,
            kernel_size=3,
            padding=1,
            use_batchnorm=use_batchnorm,
        )
        self.up = nn.UpsamplingBilinear2d(scale_factor=2)

    def forward(self, x, skip=None):
        x = self.up(x)
        if skip is not None:
            x = torch.cat([x, skip], dim=1)
        x = self.conv1(x)
        x = self.conv2(x)
        return x


class SegmentationHead(nn.Sequential):
    def __init__(self, in_channels, out_channels, kernel_size=3, upsampling=1):
        conv2d = nn.Conv2d(in_channels,
                           out_channels,
                           kernel_size=kernel_size,
                           padding=kernel_size // 2)
        upsampling = nn.UpsamplingBilinear2d(
            scale_factor=upsampling) if upsampling > 1 else nn.Identity()
        super().__init__(conv2d, upsampling)


class DecoderCup(nn.Module):
    def __init__(self, hidden_size: int, decoder_channels: tuple):
        super().__init__()
        head_channels = 512
        self.conv_more = Conv2dReLU(
            hidden_size,
            head_channels,
            kernel_size=3,
            padding=1,
            use_batchnorm=True,
        )
        in_channels = [head_channels] + list(decoder_channels[:-1])
        out_channels = decoder_channels
        skip_channels = [0, 0, 0, 0]

        blocks = [
            DecoderBlock(in_ch, out_ch, sk_ch) for in_ch, out_ch, sk_ch in zip(
                in_channels, out_channels, skip_channels)
        ]
        self.blocks = nn.ModuleList(blocks)

    def forward(self, hidden_states):
        # reshape from (B, n_patch, hidden) to (B, h, w, hidden)
        B, n_patch, hidden = hidden_states.size()
        h, w = int(np.sqrt(n_patch)), int(np.sqrt(n_patch))
        x = hidden_states.permute(0, 2, 1)
        x = x.contiguous().view(B, hidden, h, w)
        x = self.conv_more(x)
        for i, decoder_block in enumerate(self.blocks):
            x = decoder_block(x, skip=None)
        return x


class ViTSeg(nn.Module):
    def __init__(self,
                 transformer,
                 img_size=224,
                 num_classes=3,
                 hidden_size=192,
                 decoder_channels=(256, 128, 64, 16)):
        super(ViTSeg, self).__init__()
        self.img_size = img_size
        self.num_classes = num_classes
        self.transformer = transformer
        self.decoder = DecoderCup(hidden_size, decoder_channels)
        self.segmentation_head = SegmentationHead(
            in_channels=decoder_channels[-1],
            out_channels=num_classes,
            kernel_size=3,
        )

    def forward(self, x):
        assert x.shape[-1] == self.img_size, 'Input image is of wrong size'
        if x.size()[1] == 1:
            x = x.repeat(1, 3, 1, 1)
        # (B, n_patch, hidden)
        x = self.transformer(x, return_all_tokens=True)
        # remove the CLS token
        x = x[:, 1:, :]
        x = self.decoder(x)
        logits = self.segmentation_head(x)
        return logits
