import math
from typing import Tuple

import torch
import torch.nn as nn
import torch.nn.functional as F
import torch.nn.parallel
import torch.utils.data
from torch import Tensor


class PCN_encoder(nn.Module):
    """Model class respresenting the Point Completion Network Encoder as proposed in:

    Yuan, W., Khot, T., Held, D., Mertz, C., & Hebert, M. (2018).
    Pcn: Point completion network.
    In 2018 International Conference on 3D Vision (3DV) (pp. 728-737). IEEE.
    """

    def __init__(self, size_latent: int = 1024) -> None:
        """Create an instance of Point Completion Network Encoder.

        Args:
            size_latent: the dimension for the latent code.
        """
        super(PCN_encoder, self).__init__()
        self.conv1 = nn.Conv1d(3, 128, 1)
        self.conv2 = nn.Conv1d(128, 256, 1)
        self.conv3 = nn.Conv1d(512, 512, 1)
        self.conv4 = nn.Conv1d(512, size_latent, 1)

    def forward(self, x: Tensor) -> Tensor:
        """Process input point cloud and produce the latent codes.

        Args:
            x: The input point cloud with shape (BATCH, NUM_POINTS, 3). The method internally
            transposes the data tensor to correctly operate with PyTorch convetion (B CH N).

        Returns:
            The latent codes with shape (BATCH, SIZE_LATENT).
        """
        x = x.transpose(2, 1)
        batch_size, _, num_points = x.size()
        x = F.relu(self.conv1(x))
        x = self.conv2(x)
        global_feature, _ = torch.max(x, 2)
        x = torch.cat(
            (x, global_feature.reshape(batch_size, -1, 1).repeat(1, 1, num_points).contiguous()), 1
        )
        x = F.relu(self.conv3(x))
        x = self.conv4(x)
        global_feature, _ = torch.max(x, 2)
        return global_feature.reshape(batch_size, -1)


class PCN_decoder(nn.Module):
    """Model class respresenting the Point Completion Network Decoder as proposed in:

    Yuan, W., Khot, T., Held, D., Mertz, C., & Hebert, M. (2018).
    Pcn: Point completion network.
    In 2018 International Conference on 3D Vision (3DV) (pp. 728-737). IEEE.
    """

    def __init__(
        self,
        num_pcd_coarse: int,
        num_pcd_fine: int,
        scale: float,
        num_cat_feature: int,
        device: torch.device,
    ) -> None:
        """Create an instance of Point Completion Network Decoder.

        Args:
            num_pcd_coarse: the number of points for the coarse point cloud.
            num_pcd_fine: the number of points for the fine point cloud.
            scale: the scale for the folded grid.
            num_cat_feature: the size of the input embedding.
            device: the device to use for the grid.
        """
        super(PCN_decoder, self).__init__()

        self.num_coarse = num_pcd_coarse
        self.num_fine = num_pcd_fine
        self.fc1 = nn.Linear(1024, 1024)
        self.fc2 = nn.Linear(1024, 1024)
        self.fc3 = nn.Linear(1024, self.num_coarse * 3)

        self.scale = scale
        grid = self.__gen_grid_up(2 ** (int(math.log2(scale))), 0.05)
        self.device = device
        self.grid = grid.to(self.device).contiguous()
        self.conv1 = nn.Conv1d(num_cat_feature, 512, 1)
        self.conv2 = nn.Conv1d(512, 512, 1)
        self.conv3 = nn.Conv1d(512, 3, 1)

    @staticmethod
    def __gen_grid_up(up_ratio: int, grid_size: float) -> Tensor:
        """Generate coordinates grid.

        Args:
            up_ratio: The scale of the grid.
            grid_size: The coordinate reference frame [-grid_size, grid_size].

        Returns:
            The generated grid.
        """
        sqrted = int(math.sqrt(up_ratio)) + 1
        num_x = 1
        num_y = 1
        for i in range(1, sqrted + 1).__reversed__():
            if (up_ratio % i) == 0:
                num_x = i
                num_y = int(up_ratio // i)
                break

        grid_x = torch.linspace(-grid_size, grid_size, steps=num_x)
        grid_y = torch.linspace(-grid_size, grid_size, steps=num_y)

        x, y = torch.meshgrid(grid_x, grid_y, indexing="ij")  # x, y shape: (2, 1)
        grid = torch.stack([x, y], dim=-1).reshape(-1, 2).transpose(0, 1).contiguous()
        return grid

    def forward(self, x: Tensor) -> Tuple[Tensor, Tensor]:
        """Generate the coarse and fine point clouds from the embedding.

        Args:
            x: The input latent codes with shape (BATCH, SIZE_LATENT).

        Returns:
            A Tuple containing:
            - The generated coarse point cloud with shape (BATCH, 3, NUM_PCD_COARSE).
            - The generated fine point cloud with shape (BATCH, 3, NUM_PCD_FINE).
        """
        batch_size = x.size()[0]
        coarse = F.relu(self.fc1(x))
        coarse = F.relu(self.fc2(coarse))
        coarse = self.fc3(coarse).reshape(-1, 3, self.num_coarse)

        grid = self.grid.clone().detach()
        grid_feat = grid.unsqueeze(0).repeat(batch_size, 1, self.num_coarse).contiguous()
        grid_feat = grid_feat.to(self.device)

        point_feat = (
            (
                (coarse.transpose(1, 2).contiguous())  # type: ignore
                .unsqueeze(2)
                .repeat(1, 1, self.scale, 1)
                .reshape(-1, self.num_fine, 3)
            )
            .transpose(1, 2)
            .contiguous()
        )

        global_feat = x.unsqueeze(2).repeat(1, 1, self.num_fine)

        feat = torch.cat((grid_feat, point_feat, global_feat), 1)

        center = (
            (
                (coarse.transpose(1, 2).contiguous())  # type: ignore
                .unsqueeze(2)
                .repeat(1, 1, self.scale, 1)
                .reshape(-1, self.num_fine, 3)
            )
            .transpose(1, 2)
            .contiguous()
        )

        fine = self.conv3(F.relu(self.conv2(F.relu(self.conv1(feat))))) + center
        return coarse, fine


class PCNNetwork(nn.Module):
    """Model class respresenting the Point Completion Network as proposed in:

    Yuan, W., Khot, T., Held, D., Mertz, C., & Hebert, M. (2018).
    Pcn: Point completion network.
    In 2018 International Conference on 3D Vision (3DV) (pp. 728-737). IEEE.
    """

    def __init__(
        self, device: torch.device, num_points: int = 2048, num_points_coarse: int = 1024
    ) -> None:
        """Create an instance of Point Completion Network.

        Args:
            device: the device to use for the grid to fold.
            num_points: The number of points for the fine point cloud. Defaults to 2048.
            num_points_coarse: The number of points for the coarse point cloud. Defaults to 1024.
        """
        super(PCNNetwork, self).__init__()
        self.num_coarse = num_points_coarse
        self.num_points = num_points
        self.scale = self.num_points // num_points_coarse
        self.cat_feature_num = 2 + 3 + 1024
        self.device = device

        self.encoder = PCN_encoder()
        self.decoder = PCN_decoder(
            self.num_coarse, self.num_points, self.scale, self.cat_feature_num, self.device
        )

    def forward(self, x: Tensor) -> Tuple[Tensor, Tensor]:
        """Perform point cloud completion on the input point cloud.

        Args:
            x: The input point cloud with shape (BATCH, NUM_POINTS, 3). The method internally
            transposes the data tensor to correctly operate with PyTorch convetion (B CH N).

        Returns:
            A Tuple containing:
            - The generated coarse point cloud with shape (BATCH, NUM_PCD_COARSE, 3).
            - The generated fine point cloud with shape (BATCH, NUM_PCD_FINE, 3).

            The method internally transposes the output data tensors.
        """
        feat = self.encoder(x)
        coarse, fine = self.decoder(feat)
        coarse = coarse.transpose(1, 2).contiguous()
        fine = fine.transpose(1, 2).contiguous()

        return coarse, fine

    def __repr__(self) -> str:
        layer_str = ""
        for name, param in self.named_parameters():
            if "kernel" in name:
                layer_str += "Name: {} - Shape {}".format(name, param.transpose(2, 1).shape) + "\n"

        return super(PCNNetwork, self).__repr__() + layer_str  # type: ignore
