from typing import Tuple, Union

import torch
import torch.nn.functional as F
from einops import repeat  # type: ignore
from torch import Tensor
from torch.nn import BatchNorm1d, Conv1d, Dropout, Linear, Module


class TNet(Module):
    """Model class respresenting the T-Net as proposed in:

    Qi, Charles R., et al.
    "Pointnet: Deep learning on point sets for 3d classification and segmentation."
    Proceedings of the IEEE conference on computer vision and pattern recognition. 2017.

    """

    def __init__(self, channels_in: int = 3, dimension: int = 3) -> None:
        """Create a new instance of T-Net.

        Args:
            channels_in (optional): the size of first convolutional layer. Defaults to 3.
            dimension (optional): the dimension for the learned transformation. Defaults to 3.
        """
        super(TNet, self).__init__()
        self.dim = dimension
        self.conv_1 = Conv1d(channels_in, 64, 1)
        self.conv_2 = Conv1d(64, 128, 1)
        self.conv_3 = Conv1d(128, 1024, 1)
        self.fc_1 = Linear(1024, 512)
        self.fc_2 = Linear(512, 256)
        self.fc_3 = Linear(256, self.dim * self.dim)

        self.bn_1 = BatchNorm1d(64)  # type: ignore
        self.bn_2 = BatchNorm1d(128)  # type: ignore
        self.bn_3 = BatchNorm1d(1024)  # type: ignore
        self.bn_4 = BatchNorm1d(512)  # type: ignore
        self.bn_5 = BatchNorm1d(256)  # type: ignore

    def forward(self, x: Tensor) -> Tensor:
        """Process input point cloud and produce the transformation matrix.

        Args:
            x: The input clouds with shape (B, CH_IN, NUM_PTS). The method internally
            does NOT transposes the data tensor to correctly operate with PyTorch convetion (B CH N).

        Returns:
            The learned transformation with shape (B, DIMENSION, DIMENSION).
        """
        batch_size = x.shape[0]
        x = F.relu(self.bn_1(self.conv_1(x)))
        x = F.relu(self.bn_2(self.conv_2(x)))
        x = F.relu(self.bn_3(self.conv_3(x)))
        x = torch.max(x, 2, keepdim=True)[0]
        x = x.reshape(batch_size, -1)

        x = F.relu(self.bn_4(self.fc_1(x)))
        x = F.relu(self.bn_5(self.fc_2(x)))
        x = self.fc_3(x)

        iden = torch.eye(self.dim).reshape(1, self.dim * self.dim)
        iden = iden.to(x.device)
        iden = repeat(iden, "b d -> (r b)  d", r=x.size(0))
        x = x + iden
        x = x.reshape(-1, self.dim, self.dim)

        return x

    def transform(
        self,
        x: Tensor,
        transform: Tensor,
        rotate_normals: bool,
        apply_to_features: bool,
    ) -> Tensor:
        """Apply the transformation.

        Args:
            x: the input points to transform with shape (B, D, N).
            transform: the transformation to apply with shape (B, D, D).

        Returns:
            The transformed points with shape (B, D, N).
        """

        def multiply(x: Tensor, transform: Tensor) -> Tensor:
            x = x.transpose(2, 1)
            x = torch.bmm(x, transform)
            x = x.transpose(2, 1)
            return x

        if apply_to_features or x.shape[1] == 3:
            return multiply(x, transform)
        else:
            pts = x[:, :3, :]
            features = x[:, 3:, :]
            pts = multiply(pts, transform)

            if rotate_normals:
                features = multiply(features, transform)

            x = torch.cat([pts, features], dim=1)
            return x


class PointNetEncoder(Module):
    """Model class respresenting the PointNet Encoder as proposed in:

    Qi, Charles R., et al.
    "Pointnet: Deep learning on point sets for 3d classification and segmentation."
    Proceedings of the IEEE conference on computer vision and pattern recognition. 2017.
    """

    def __init__(
        self,
        channels_in: int = 3,
        size_global_feature: int = 1024,
        use_pts_tnet: bool = True,
        use_feats_tnet: bool = True,
        align_normals: bool = False,
    ) -> None:
        """Create a new instance of PointNet Encoder.

        Args:
            channels_in (optional): the size of first convolutional layer. Defaults to 3.
            size_global_feature (optional): the size for the global feature. Defaults to 1024.
            use_pts_tnet (optional): If True use the points T-Net. Defaults to True.
            use_feats_tnet (optional): If True use the features T-Net. Defaults to True.
            align_normals (optional): If True rotate normals using the T-Net. Defaults to True.
        """
        super(PointNetEncoder, self).__init__()
        self.size_feat_glob = size_global_feature
        self.use_pts_tnet = use_pts_tnet
        self.use_feat_tnet = use_feats_tnet
        self.align_normals = align_normals

        if self.use_pts_tnet:
            self.tnet_pts = TNet(channels_in=channels_in, dimension=3)

        self.conv_1 = Conv1d(channels_in, 64, 1)
        self.conv_2 = Conv1d(64, 128, 1)
        self.conv_3 = Conv1d(128, self.size_feat_glob, 1)
        self.bn_1 = BatchNorm1d(64)  # type: ignore
        self.bn_2 = BatchNorm1d(128)  # type: ignore
        self.bn_3 = BatchNorm1d(self.size_feat_glob)  # type: ignore

        if self.use_feat_tnet:
            self.tnet_feats = TNet(channels_in=64, dimension=64)

    def forward(self, x: Tensor) -> Tuple[Tensor, Union[Tensor, None], Union[Tensor, None]]:
        """Process input point cloud and produce point net features.

        Args:
            x: The input clouds with shape (B, NUM_PTS, DIM). The method internally
            transposes the data tensor to correctly operate with PyTorch convetion (B CH N).

        Returns:
            A tuple containing:
                - The computed global feature vector with shape (B, SIZE_GLOBAL_FEAT).
                - The learned transformation matrix for the input points.
                - The learned transformation matrix for the features.
        """
        x = x.transpose(2, 1)  # B DIM NUM_PTS
        if self.use_pts_tnet:
            trans_pts = self.tnet_pts(x)
            x = self.tnet_pts.transform(x, trans_pts, self.align_normals, False)
        else:
            trans_pts = None

        x = F.relu(self.bn_1(self.conv_1(x)))

        if self.use_feat_tnet:
            trans_feat = self.tnet_feats(x)
            x = self.tnet_feats.transform(x, trans_feat, False, True)
        else:
            trans_feat = None

        x = F.relu(self.bn_2(self.conv_2(x)))
        x = self.bn_3(self.conv_3(x))
        x = torch.max(x, 2, keepdim=True)[0]
        global_feature = x.reshape(-1, self.size_feat_glob)

        return global_feature, trans_pts, trans_feat


class PointNetClassification(Module):
    def __init__(
        self,
        channels_in: int = 3,
        size_global_feature: int = 1024,
        use_pts_tnet: bool = True,
        use_feats_tnet: bool = True,
        align_normals: bool = False,
        dropout_p: float = 0.3,
        num_classes: int = 10,
    ) -> None:
        """Create a new instance of PointNet Classification Network.

        Args:
            channels_in (optional): the size of first convolutional layer. Defaults to 3.
            size_global_feature (optional): the size for the global feature. Defaults to 1024.
            use_pts_tnet (optional): If True use the points T-Net. Defaults to True.
            use_feats_tnet (optional): If True use the features T-Net. Defaults to True.
            align_normals (optional): If True rotate normals using the T-Net. Defaults to False.
            dropout_p: the dropout probability. Defaults to 0.5.
            num_classes: the number of classes. Defaults to 10.
        """

        super(PointNetClassification, self).__init__()
        self.encoder = PointNetEncoder(
            channels_in=channels_in,
            size_global_feature=size_global_feature,
            align_normals=align_normals,
            use_pts_tnet=use_pts_tnet,
            use_feats_tnet=use_feats_tnet,
        )
        self.fc_1 = Linear(1024, 512)
        self.fc_2 = Linear(512, 256)
        self.fc_3 = Linear(256, num_classes)
        self.dropout = Dropout(dropout_p)
        self.bn_1 = BatchNorm1d(512)  # type: ignore
        self.bn_2 = BatchNorm1d(256)  # type: ignore

    def forward(self, x: Tensor) -> Tuple[Tensor, Union[Tensor, None], Union[Tensor, None]]:
        """Process input point clouds and produces claffication scores.

        Args:
            x: The input clouds with shape (B, NUM_PTS, DIM). The method internally
            transposes the data tensor to correctly operate with PyTorch convetion (B CH N).

        Returns:
            A tuple containing:
                - The computed classification scores with shape (B, NUM_CLASSES).
                - The learned transformation matrix for the input points.
                - The learned transformation matrix for the features.
        """
        x, trans_pts, trans_feat = self.encoder(x)
        x = F.relu(self.dropout(self.bn_1(self.fc_1(x))))
        x = F.relu(self.dropout(self.bn_2(self.fc_2(x))))
        x = self.fc_3(x)
        return x, trans_pts, trans_feat


class PointNetPartSegmentation(Module):
    def __init__(
        self,
        channels_in: int = 3,
        size_global_feature: int = 2048,
        use_pts_tnet: bool = True,
        use_feats_tnet: bool = True,
        align_normals: bool = False,
        num_classes: int = 16,
        num_classes_part: int = 50,
    ) -> None:
        """Create a new instance of PointNet Part Segmentation Network.

        Args:
            channels_in (optional): the size of first convolutional layer. Defaults to 3.
            size_global_feature (optional): the size for the global feature. Defaults to 2048.
            use_pts_tnet (optional): if True use the points T-Net. Defaults to True.
            use_feats_tnet (optional): if True use the features T-Net. Defaults to True.
            align_normals (optional): if True rotate normals using the T-Net. Defaults to True.
            num_classes (optional): the number of classes for the categorical vector. Defaults to 16.
            num_classes_part: (optional): the number of overal part segmentation classes Defaults to 50.
        """

        super(PointNetPartSegmentation, self).__init__()

        self.num_classes = num_classes
        self.num_classes_part = num_classes_part
        self.use_pts_tnet = use_pts_tnet
        self.use_feat_tnet = use_feats_tnet
        self.size_global_feature = size_global_feature
        self.align_normals = align_normals

        if self.use_pts_tnet:
            self.tnet_pts = TNet(channels_in=channels_in, dimension=3)

        if self.use_feat_tnet:
            self.tnet_feats = TNet(channels_in=128, dimension=128)

        self.conv_1 = Conv1d(channels_in, 64, 1)
        self.conv_2 = Conv1d(64, 128, 1)
        self.conv_3 = Conv1d(128, 128, 1)
        self.conv_4 = Conv1d(128, 512, 1)
        self.conv_5 = Conv1d(512, self.size_global_feature, 1)
        self.bn_1 = BatchNorm1d(64)  # type: ignore
        self.bn_2 = BatchNorm1d(128)  # type: ignore
        self.bn_3 = BatchNorm1d(128)  # type: ignore
        self.bn_4 = BatchNorm1d(512)  # type: ignore
        self.bn_5 = BatchNorm1d(self.size_global_feature)  # type: ignore

        size_in_conv = self.size_global_feature * 2 + self.num_classes + 64 + 128 * 2 + 512
        self.conv_seg_1 = Conv1d(size_in_conv, 256, 1)
        self.conv_seg_2 = Conv1d(256, 256, 1)
        self.conv_seg_3 = Conv1d(256, 128, 1)
        self.conv_seg_4 = Conv1d(128, num_classes_part, 1)
        self.bn_seg_1 = BatchNorm1d(256)  # type: ignore
        self.bn_seg_2 = BatchNorm1d(256)  # type: ignore
        self.bn_seg_3 = BatchNorm1d(128)  # type: ignore

    def forward(
        self, x: Tensor, vector_cat: Tensor
    ) -> Tuple[Tensor, Union[Tensor, None], Union[Tensor, None]]:
        """Process input point clouds and produces per points claffication scores.

        Args:
            x: The input clouds with shape (B, NUM_PTS, DIM).
            vector_cat: the one hot encoding categorical vector (B, NUM_CLASSES).

        Returns:
            A tuple containing:
                - The computed classification scores with shape (B, NUM_PTS, NUM_CLASSES_PART).
                - The learned transformation matrix for the input points.
                - The learned transformation matrix for the features.
        """
        num_points = x.shape[1]
        x = torch.transpose(x, 2, 1)

        if self.use_pts_tnet:
            trans_pts = self.tnet_pts(x)
            x = self.tnet_pts.transform(x, trans_pts, self.align_normals, False)
        else:
            trans_pts = None

        feat_1 = F.relu(self.bn_1(self.conv_1(x)))
        feat_2 = F.relu(self.bn_2(self.conv_2(feat_1)))
        feat_3 = F.relu(self.bn_3(self.conv_3(feat_2)))

        if self.use_feat_tnet:
            trans_feat = self.tnet_feats(feat_3)
            feat_3 = self.tnet_feats.transform(feat_3, trans_feat, False, True)
        else:
            trans_feat = None

        feat_4 = F.relu(self.bn_4(self.conv_4(feat_3)))
        feat_5 = self.bn_5(self.conv_5(feat_4))
        global_feature = torch.max(feat_5, 2, keepdim=True)[0]
        global_feature = global_feature.reshape(-1, self.size_global_feature)

        global_feature = torch.cat([global_feature, vector_cat], 1)
        global_feature = global_feature.unsqueeze(-1)
        global_feature = repeat(global_feature, "b ch n -> b ch (n r)", r=num_points)

        feats_concat = torch.cat([global_feature, feat_1, feat_2, feat_3, feat_4, feat_5], 1)
        feats_seg = F.relu(self.bn_seg_1(self.conv_seg_1(feats_concat)))
        feats_seg = F.relu(self.bn_seg_2(self.conv_seg_2(feats_seg)))
        feats_seg = F.relu(self.bn_seg_3(self.conv_seg_3(feats_seg)))
        feats_pts = self.conv_seg_4(feats_seg)
        feats_pts = torch.transpose(feats_pts, 2, 1)

        feats_pts = feats_pts.reshape(-1, num_points, self.num_classes_part)
        return feats_pts, trans_pts, trans_feat
