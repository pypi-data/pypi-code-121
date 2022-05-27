from typing import List

import torch
from torch import nn as nn


class PointSetGenerator(nn.Module):
    """Generate a set of 3D points starting from a latent code."""

    def __init__(self, size_latent: int = 2500, convolutions: List[int] = [2500, 1250, 625, 3]):
        """Create a new instance of PointSet Generator.

        Args:
            size_latent ([type], optional): [description]. Defaults to 2500.
            convolutions ([type], optional): [description]. Defaults to [2500, 1250, 625, 3].

        Raises:
            ValueError: if the final output channel of the final layer differs from 3.
        """
        self.size_latent = size_latent
        super(PointSetGenerator, self).__init__()

        if convolutions[-1] != 3:
            raise ValueError("The output channels for the last layer must be 3.")

        self.convolutions = convolutions

        list_convolutions = nn.ModuleList()
        for idx in range(len(self.convolutions[:-1])):
            in_ch_conv = self.size_latent if idx == 0 else self.convolutions[idx - 1]
            out_ch_conv = self.convolutions[idx]
            list_convolutions.append(nn.Conv1d(in_ch_conv, out_ch_conv, 1))
            list_convolutions.append(nn.BatchNorm1d(out_ch_conv))  # type: ignore
            list_convolutions.append(nn.ReLU())

        list_convolutions.append(nn.Conv1d(self.convolutions[-2], self.convolutions[-1], 1))
        self.point_generator = nn.Sequential(*list_convolutions)
        self.th = nn.Tanh()

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """Generate a set of points.

        Args:
            x: The input embeddings with shape (BATCH, NUM_POINTS, SIZE_LATENT). The method internally
            transposes the data tensor to correctly operate with PyTorch convetion (B CH N).

        Returns:
            The generate points with shape (BATCH, NUM_POINTS, 3).
        """
        x_channel_first = torch.transpose(x, 2, 1)
        points = self.th(self.point_generator(x_channel_first))
        points_channel_last = torch.transpose(points, 2, 1)
        return points_channel_last

    def __repr__(self) -> str:
        layer_str = ""
        for name, param in self.named_parameters():
            if "kernel" in name:
                layer_str += "Name: {} - Shape {}".format(name, param.transpose(2, 1).shape) + "\n"

        return super(PointSetGenerator, self).__repr__() + layer_str  # type: ignore
