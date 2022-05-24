from typing import List

import torch
from torch import nn as nn
from torch.autograd import Variable

from pycarus.learning.models.pointset_generator import PointSetGenerator


class AtlasNetDecoder(nn.Module):
    """Model class respresenting a plane folding decoder as proposed in:

    Groueix, Thibault, et al. "A papier-mâché approach to learning 3d surface generation."
    Proceedings of the IEEE conference on computer vision and pattern recognition. 2018.
    """

    def __init__(
        self,
        size_latent: int = 512,
        size_points: int = 1225,
        convolutions: List[int] = [514, 257, 128, 3],
    ) -> None:
        """Create an instance of AtlasNetDecoder.

        Args:
            size_latent: the size for the latent space. Defaults to 512.
            size_points: the size of output points. Defaults to 1225.
            convolutions: the output channels for the 1D convolutions. Defaults to [514, 257, 128, 3].

        Raises:
            ValueError: if the final output channel of the final layer differs from 3.
        """
        super(AtlasNetDecoder, self).__init__()
        self.size_latent = size_latent
        self.size_points = size_points
        self.out_ch_conv = convolutions

        try:
            self.pts_gen = PointSetGenerator(self.size_latent + 2, self.out_ch_conv)
        except ValueError as exception:
            raise exception

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """Generate a set of points starting from the embeddings.

        Args:
            x: The input point cloud with shape (BATCH, SIZE_LATENT).

        Returns:
            The generate points with shape (BATCH, NUM_POINTS, 3).
        """
        rand_grid = Variable(torch.FloatTensor(x.size(0), 2, self.size_points).to(x.device))
        rand_grid.data.uniform_(0, 1)

        y = x.unsqueeze(2).expand(x.size(0), x.size(1), rand_grid.size(2))
        y = torch.cat((rand_grid, y), 1)
        # B N CH
        y = torch.transpose(y, 2, 1)
        pts_gen = self.pts_gen(y)
        return pts_gen

    def __repr__(self) -> str:
        layer_str = ""
        for name, param in self.named_parameters():
            if "kernel" in name:
                layer_str += "Name: {} - Shape {}".format(name, param.transpose(2, 1).shape) + "\n"

        return super(AtlasNetDecoder, self).__repr__() + layer_str  # type: ignore
