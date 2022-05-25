import torch
import torch.nn as nn
import torch.nn.functional as F
import pytorch_lightning as pl 
from typing import Union, List, Dict, Any, Optional, cast

class DoubleConv(nn.Module):
    """[ Conv2d => BatchNorm (optional) => ReLU ] x 2."""

    def __init__(
        self, 
        in_ch: int, 
        out_ch: int,
        bn : bool = True,
        activation_type : str = "relu",
        negative_slope : Optional[float] = None 
    ):
        super().__init__()
        
        layers = []
        layers.append(nn.Conv2d(in_ch, out_ch, kernel_size=3, padding=1))
        if bn:
            layers.append(nn.BatchNorm2d(out_ch))
        if activation_type == "tanh":
            layers.append(nn.Tanh())
        elif activation_type == "relu":
            layers.append(nn.ReLU(inplace=True))
        elif activation_type == "leaky_relu":
            if not negative_slope:
                negative_slope = 1e-2
            layers.append(nn.LeakyReLU(negative_slope=negative_slope, inplace=True))
        else:
            raise ValueError("Wrong name {} for activation function.".format(activation_type))
        
        layers.append(nn.Conv2d(out_ch, out_ch, kernel_size=3, padding=1))
        if bn:
            layers.append(nn.BatchNorm2d(out_ch))
        if activation_type == "tanh":
            layers.append(nn.Tanh())
        elif activation_type == "relu":
            layers.append(nn.ReLU(inplace=True))
        elif activation_type == "leaky_relu":
            if not negative_slope:
                negative_slope = 1e-2
            layers.append(nn.LeakyReLU(negative_slope=negative_slope, inplace=True))
        else:
            raise ValueError("Wrong name {} for activation function.".format(activation_type))
        
        
        self.net = nn.Sequential(*layers)

    def forward(self, x):
        return self.net(x)


class Down(nn.Module):
    """Downscale with MaxPool => DoubleConvolution block."""

    def __init__(self, in_ch: int, out_ch: int):
        super().__init__()
        self.net = nn.Sequential(nn.MaxPool2d(kernel_size=2, stride=2), DoubleConv(in_ch, out_ch))

    def forward(self, x):
        return self.net(x)


class Up(nn.Module):
    """Upsampling (by either bilinear interpolation or transpose convolutions) followed by concatenation of feature
    map from contracting path, followed by DoubleConv."""

    def __init__(
        self, 
        in_ch: int, 
        out_ch: int, 
        bilinear: bool
    ):
        super().__init__()
        self.upsample = None
        if bilinear:
            self.upsample = nn.Sequential(
                nn.Upsample(scale_factor=2, mode="bilinear", align_corners=True),
                nn.Conv2d(in_ch, in_ch // 2, kernel_size=1),
            )
        else:
            self.upsample = nn.ConvTranspose2d(in_ch, in_ch // 2, kernel_size=2, stride=2)

        self.conv = DoubleConv(in_ch, out_ch)

    def forward(self, x1, x2):
        x1 = self.upsample(x1)

        # Pad x1 to the size of x2
        diff_h = x2.shape[2] - x1.shape[2]
        diff_w = x2.shape[3] - x1.shape[3]

        x1 = F.pad(x1, [diff_w // 2, diff_w - diff_w // 2, diff_h // 2, diff_h - diff_h // 2])

        # Concatenate along the channels axis
        x = torch.cat([x2, x1], dim=1)
        return self.conv(x)

