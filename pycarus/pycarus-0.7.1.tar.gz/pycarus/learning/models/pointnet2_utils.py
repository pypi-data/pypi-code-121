from typing import List, Tuple

import torch
import torch.nn as nn
import torch.nn.functional as F
from einops import repeat  # type: ignore
from pytorch3d.ops import ball_query, knn_gather, knn_points  # type: ignore
from torch import Tensor
from torch.nn import BatchNorm2d, Conv2d, Module, ModuleList

from pycarus.geometry.pcd import farthest_point_sampling


def replace_minus_one(x: Tensor) -> Tensor:
    """Replace -1 pad with the index of the first element of the tensor.

    Args:
        x: indices tensor returned from ball_query with shape (B, NUM_PTS, K).

    Returns:
        The padded indices with new values with shape (B, NUM_PTS, K).
    """
    pad_values = x[:, :, 0]
    pad_values = repeat(pad_values, "b n -> b n r", r=x.shape[-1])

    indices_pad = x == -1
    x[indices_pad] = pad_values[indices_pad]

    return x


class PointNetSetAbstraction(Module):
    def __init__(
        self,
        num_point: int,
        radius: float,
        num_samples: int,
        in_channel: int,
        mlp: List[int],
        group_all: bool,
    ) -> None:
        super(PointNetSetAbstraction, self).__init__()
        self.num_point = num_point
        self.radius = radius
        self.num_sample = num_samples
        self.mlp_convs = ModuleList()
        self.mlp_bns = ModuleList()
        last_channel = in_channel
        for out_channel in mlp:
            self.mlp_convs.append(Conv2d(last_channel, out_channel, 1))
            self.mlp_bns.append(BatchNorm2d(out_channel))  # type: ignore
            last_channel = out_channel
        self.group_all = group_all

    def forward(self, xyz: Tensor, features: Tensor) -> Tuple[Tensor, Tensor]:
        """Process input point cloud and produce point net++ features.

        Args:
            xyz: the input points coordinates with shape (B, NUM_PTS, 3).
            features: the input features data with shaoe (B, NUM_PTS, D).

        Returns:
            A tuple containing:
             - The sampled points coordinates with fps with shape (B, NUM_POINTS, 3).
             - The concatenated points feature data (B, NUM_POINTS, D').
        """
        if self.group_all:
            size_b, num_pts, ch = xyz.shape
            grouped_xyz = xyz.reshape(size_b, 1, num_pts, ch)

            if features is not None:
                features_grouped = torch.cat(
                    [grouped_xyz, features.reshape(size_b, 1, num_pts, -1)],
                    dim=-1,
                )
            else:
                features_grouped = grouped_xyz

            xyz_grouped = torch.zeros(size_b, 1, ch).to(xyz.device)
        else:
            raise NotImplementedError("Function not yet implemented.")

        # new_xyz: sampled points position data, [B, npoint, C]
        # new_points: sampled points data, [B, npoint, nsample, C+D]
        features_grouped = features_grouped.permute(0, 3, 2, 1)  # [B, C+D, nsample,npoint]
        for i, conv in enumerate(self.mlp_convs):
            bn = self.mlp_bns[i]
            features_grouped = F.relu(bn(conv(features_grouped)))

        features_out = torch.max(features_grouped, 2)[0]
        features_out = features_out.transpose(2, 1)

        return xyz_grouped, features_out


class PointNetSetAbstractionMsg(Module):
    def __init__(
        self,
        num_point: int,
        list_radius: List[float],
        list_num_samples: List[int],
        in_channel: int,
        mlp_list: List[List[int]],
    ) -> None:
        """Create a new instance of PointNet++ Set Abstraction Layer MSG.

        Args:
            num_point: the numbe of points to sample with fps.
            list_radius: the list of radius to use for ball queries.
            list_num_samples: the list of max number of samples to keep for ball queries.
            in_channel: the number of input channels.
            mlp_list: the list of MLP modules channels.
        """
        super(PointNetSetAbstractionMsg, self).__init__()

        self.num_point = num_point
        self.radius_list = list_radius
        self.nsample_list = list_num_samples
        self.conv_blocks = ModuleList()
        self.bn_blocks = ModuleList()

        for i in range(len(mlp_list)):
            convs = ModuleList()
            bns = ModuleList()
            last_channel = in_channel + 3
            for out_channel in mlp_list[i]:
                convs.append(Conv2d(last_channel, out_channel, 1))
                bns.append(BatchNorm2d(out_channel))  # type: ignore
                last_channel = out_channel
            self.conv_blocks.append(convs)
            self.bn_blocks.append(bns)

    def forward(self, xyz: Tensor, features: Tensor) -> Tuple[Tensor, Tensor]:
        """Process input point cloud and produce point net++ features.

        Args:
            xyz: the input points coordinates with shape (B, NUM_PTS, 3).
            features: the input features data with shaoe (B, NUM_PTS, D).

        Returns:
            A tuple containing:
             - The sampled points coordinates with fps with shape (B, NUM_POINTS, 3).
             - The concatenated points feature data (B, NUM_POINTS, D').
        """
        _, _, C = xyz.shape

        xyz_ss = farthest_point_sampling(xyz, self.num_point)
        list_features_out = []

        for i, radius in enumerate(self.radius_list):
            _, indices_group, _ = ball_query(xyz_ss, xyz, K=self.nsample_list[i], radius=radius)
            indices_group = replace_minus_one(indices_group)
            xyz_grouped = knn_gather(xyz, indices_group)
            xyz_grouped -= xyz_ss.reshape(-1, self.num_point, 1, C)

            if features is not None:
                features_grouped = knn_gather(features, indices_group)
                features_grouped = torch.cat([features_grouped, xyz_grouped], dim=-1)
            else:
                features_grouped = xyz_grouped

            features_grouped = features_grouped.permute(0, 3, 2, 1)  # [B, D, K, S]
            for j in range(len(self.conv_blocks[i])):
                conv = self.conv_blocks[i][j]
                bn = self.bn_blocks[i][j]
                features_grouped = F.relu(bn(conv(features_grouped)))

            list_features_out.append(torch.max(features_grouped, 2)[0])  # [B, D', S]

        features_out = torch.cat(list_features_out, dim=1).transpose(2, 1)
        return xyz_ss, features_out


class PointNetFeaturePropagation(Module):
    def __init__(self, in_channel: int, mlp: List[int]) -> None:
        """Create a new instance of PointNetFeaturePropagation Layer.

        Args:
            in_channel: the size of first input channels.
            mlp: the size of output channels for each mlp.
        """
        super(PointNetFeaturePropagation, self).__init__()
        self.mlp_convs = ModuleList()
        self.mlp_bns = ModuleList()
        last_channel = in_channel

        for out_channel in mlp:
            self.mlp_convs.append(nn.Conv1d(last_channel, out_channel, 1))
            self.mlp_bns.append(nn.BatchNorm1d(out_channel))  # type: ignore
            last_channel = out_channel

    def forward(self, xyz_s: Tensor, xyz_t: Tensor, feats_s: Tensor, feats_t: Tensor) -> Tensor:
        """Process input point clouds and produces per interpolated features.

        Input:
            xyz_s: the input points coordinates with shape (B, NUM_PTS_S, 3).
            xyz_t: the sampled input points position with shape (B, NUM_PTS_T, 3).
            feats_s: xyz_s per point features with shape (B, NUM_PTS_S, D).
            feats_t: xyz_t per point features with shape (B, NUM_PTS_T, D).

        Return:
            The interpolead features with shape (B, NUM_PTS_S, D').
        """

        _, N, _ = xyz_s.shape
        _, S, _ = xyz_t.shape

        if S == 1:
            feats_inter = feats_t.repeat(1, N, 1)
        else:
            dists, indices, _ = knn_points(xyz_s, xyz_t, K=3)

            dist_recip = 1.0 / (dists + 1e-8)
            norm = torch.sum(dist_recip, dim=2, keepdim=True)
            weight = dist_recip / norm
            feats_inter = torch.sum(
                knn_gather(feats_t, indices) * weight.reshape(-1, N, 3, 1), dim=2
            )

        if feats_s is not None:
            features = torch.cat([feats_s, feats_inter], dim=-1)
        else:
            features = feats_inter

        features = features.transpose(2, 1)
        for i, conv in enumerate(self.mlp_convs):
            bn = self.mlp_bns[i]
            features = F.relu(bn(conv(features)))

        features_out = features.transpose(2, 1)
        return features_out
