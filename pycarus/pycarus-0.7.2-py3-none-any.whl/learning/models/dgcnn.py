from typing import Tuple, Union

import torch
import torch.nn.functional as F
from einops import rearrange, repeat  # type: ignore
from pytorch3d.ops import knn_gather, knn_points  # type: ignore
from torch import Tensor
from torch.nn import BatchNorm1d, BatchNorm2d, Conv1d, Conv2d, Dropout, LeakyReLU, Linear, Module
from torch.nn import Sequential


class TNet(Module):
    """Model class respresenting the T-Net as proposed in:

    Wang, Yue, et al. "Dynamic graph cnn for learning on point clouds."
    Acm Transactions On Graphics (tog) 38.5 (2019): 1-12.
    """

    def __init__(self) -> None:
        super(TNet, self).__init__()

        self.conv_1 = Sequential(
            Conv2d(6, 64, kernel_size=1, bias=False),
            BatchNorm2d(64),  # type: ignore
            LeakyReLU(negative_slope=0.2),
        )
        self.conv_2 = Sequential(
            Conv2d(64, 128, kernel_size=1, bias=False),
            BatchNorm2d(128),  # type: ignore
            LeakyReLU(negative_slope=0.2),
        )
        self.conv_3 = Sequential(
            Conv1d(128, 1024, kernel_size=1, bias=False),
            BatchNorm1d(1024),  # type: ignore
            LeakyReLU(negative_slope=0.2),
        )

        self.fc_1 = Sequential(
            Linear(1024, 512, bias=False),
            BatchNorm1d(512),  # type: ignore
            LeakyReLU(negative_slope=0.2),
        )

        self.fc_2 = Sequential(
            Linear(512, 256, bias=False),
            BatchNorm1d(256),  # type: ignore
            LeakyReLU(negative_slope=0.2),
        )

        self.fc_3 = Linear(256, 9)

    def forward(self, x: Tensor) -> Tensor:
        """Process input point cloud and produce the transformation matrix.

        Args:
            x: The input clouds with shape (B, 6, NUM_PTS, K).

        Returns:
            The learned transformation with shape (B, 3, 3).
        """

        x = self.conv_1(x)
        x = self.conv_2(x)
        x = x.max(dim=-1, keepdim=False)[0]

        x = self.conv_3(x)
        x = x.max(dim=-1, keepdim=False)[0]

        x = self.fc_1(x)
        x = self.fc_2(x)
        x = self.fc_3(x)

        iden = torch.eye(3).reshape(1, 9)
        iden = iden.to(x.device)
        iden = repeat(iden, "b d -> (r b)  d", r=x.size(0))
        x = x + iden
        x = x.reshape(-1, 3, 3)

        return x


def get_graph_feature(x: Tensor, k: int = 20, indices: Union[Tensor, None] = None) -> Tensor:
    """Select features from neighbors.

    Args:
        x : the input features with shape (B, NUM_PTS, D).
        k: the number of neighbors. Defaults to 20.
        indices: the features indices with shape (B, NUM_PTS, K). Defaults to None.

    Returns:
        The selected features with shape (B, NUM_PTS, K, 2*D)
    """
    if indices is None:
        _, indices, _ = knn_points(x, x, K=k)

    features = knn_gather(x, indices)

    x = repeat(x, "b n d -> b n r d", r=k)
    features = torch.cat((features - x, x), dim=3)

    return features


class DGCNNEncoder(Module):
    """Model class respresenting the DGCNN Encoder network as proposed in:

    Wang, Yue, et al. "Dynamic graph cnn for learning on point clouds."
    Acm Transactions On Graphics (tog) 38.5 (2019): 1-12.
    """

    def __init__(
        self,
        k: int = 20,
        size_global_feature: int = 1024,
        use_geometry_nn: bool = False,
        use_tnet: bool = False,
    ) -> None:
        """Create a new instance of DGCNN Classification Encoder.

        Args:
            k (optional): the number of k-nearest neighbors for the Edge-Conv. Defaults to 20.
            size_global_feature (optional): the size for the global feature. Defaults to 1024.
            use_geometry_nn (optional): if True compute the nearest neighbors in coordinate space
            use_tnet (optional): if True use the points T-Net. Defaults to False.
        """
        super(DGCNNEncoder, self).__init__()

        self.k = k
        self.size_feat_glob = size_global_feature
        self.use_use_geometry_nn = use_geometry_nn
        self.use_pts_tnet = use_tnet
        if self.use_pts_tnet:
            self.tnet = TNet()

        self.bn_1 = BatchNorm1d(64)  # type: ignore
        self.bn_2 = BatchNorm1d(64)  # type: ignore
        self.bn_3 = BatchNorm1d(128)  # type: ignore
        self.bn_4 = BatchNorm1d(256)  # type: ignore
        self.bn_5 = BatchNorm1d(self.size_feat_glob)  # type: ignore

        self.slope = 0.2
        self.fc_1 = Linear(3 * 2, 64, bias=False)
        self.fc_2 = Linear(64 * 2, 64, bias=False)
        self.fc_3 = Linear(64 * 2, 128, bias=False)
        self.fc_4 = Linear(128 * 2, 256, bias=False)
        self.fc_5 = Linear(512, self.size_feat_glob, bias=False)

    def block_forward(
        self, x: Tensor, linear: Module, bn: Module, indices: Union[Tensor, None] = None
    ) -> Tensor:
        batch_size, num_points = x.shape[0], x.shape[1]

        x = get_graph_feature(x, k=self.k, indices=indices)
        x = linear(x)
        x = rearrange(x, "b n k d -> b d (n k)")
        x = bn(x)
        x = F.leaky_relu(x, negative_slope=self.slope)
        x = x.reshape(batch_size, -1, num_points, self.k)

        features_out = x.max(dim=-1, keepdim=False)[0]
        features_out = rearrange(features_out, "b ch n -> b n ch")
        return features_out

    def forward(self, x: Tensor) -> Tuple[Tensor, Union[Tensor, None]]:
        """Process input point cloud and produce dgcnn features.

        Args:
            x: The input clouds with shape (B, NUM_PTS, DIM).

        Returns:
            A tuple containing:
                - The computed global feature vector with shape (B, SIZE_GLOBAL_FEAT).
                - The learned transformation matrix for the input points.
        """
        if self.use_pts_tnet:
            x0 = get_graph_feature(x, k=self.k)
            x0 = torch.permute(x0, (0, 3, 1, 2))
            trans = self.tnet(x0)
            x = torch.bmm(x, trans)
        else:
            trans = None

        indices = None
        if self.use_use_geometry_nn:
            _, indices, _ = knn_points(x, x, K=self.k)

        x_1 = self.block_forward(x, self.fc_1, self.bn_1, indices)
        x_2 = self.block_forward(x_1, self.fc_2, self.bn_2, indices)
        x_3 = self.block_forward(x_2, self.fc_3, self.bn_3, indices)
        x_4 = self.block_forward(x_3, self.fc_4, self.bn_4, indices)
        x_5 = torch.cat((x_1, x_2, x_3, x_4), dim=-1)

        x_5 = self.fc_5(x_5)
        x_5 = rearrange(x_5, "b n d -> b d n")
        x_5 = self.bn_5(x_5)
        feat = F.leaky_relu(x_5, negative_slope=self.slope)

        global_feature = F.adaptive_max_pool1d(feat, 1)
        global_feature = global_feature.reshape(len(x), self.size_feat_glob)

        return global_feature, trans


class DGCNNClassification(Module):
    """Model class respresenting the DGCNN Classification network as proposed in:

    Wang, Yue, et al. "Dynamic graph cnn for learning on point clouds."
    Acm Transactions On Graphics (tog) 38.5 (2019): 1-12.
    """

    def __init__(
        self,
        k: int = 20,
        size_global_feature: int = 1024,
        use_geometry_nn: bool = False,
        use_tnet: bool = False,
        dropout_p: float = 0.5,
        num_classes: int = 10,
    ) -> None:
        """Create a new instance of DGCNN Classification Network.

        Args:
            k (optional): the number of k-nearest neighbors for the Edge-Conv. Defaults to 20.
            size_global_feature (optional): the size for the global feature. Defaults to 1024.
            use_geometry_nn (optional): if True compute the nearest neighbors in coordinate space
            instead of feature space.
            use_tnet (optional): if True use the points T-Net. Defaults to False.
            dropout_p (optional): the dropout probability. Defaults to 0.5.
            num_classes (optional): the number of classes. Defaults to 10.
        """

        super(DGCNNClassification, self).__init__()
        self.encoder = DGCNNEncoder(
            use_tnet=use_tnet,
            k=k,
            size_global_feature=size_global_feature,
            use_geometry_nn=use_geometry_nn,
        )
        self.fc_1 = Linear(1024, 512)
        self.fc_2 = Linear(512, 256)
        self.fc_3 = Linear(256, num_classes)
        self.dropout = Dropout(dropout_p)
        self.bn_1 = BatchNorm1d(512)  # type: ignore
        self.bn_2 = BatchNorm1d(256)  # type: ignore

    def forward(self, x: Tensor) -> Tuple[Tensor, Union[Tensor, None]]:
        """Process input point clouds and produces claffication scores.

        Args:
            x: The input clouds with shape (B, NUM_PTS, DIM).

        Returns:
            A tuple containing:
                - The computed classification scores with shape (B, NUM_CLASSES).
                - The learned transformation matrix for the input points.
        """
        x, trans_pts = self.encoder(x)
        x = F.relu(self.dropout(self.bn_1(self.fc_1(x))))
        x = F.relu(self.dropout(self.bn_2(self.fc_2(x))))
        x = self.fc_3(x)
        return x, trans_pts


class DGCNNPartSegmentation(Module):
    """Model class respresenting the DGCNN Part Segmentation network as proposed in:

    Wang, Yue, et al. "Dynamic graph cnn for learning on point clouds."
    Acm Transactions On Graphics (tog) 38.5 (2019): 1-12.
    """

    def __init__(
        self,
        k: int = 20,
        size_global_feature: int = 1024,
        use_geometry_nn: bool = False,
        use_tnet: bool = True,
        dropout_p: float = 0.5,
        num_classes: int = 16,
        num_classes_part: int = 10,
    ) -> None:
        """Create a new instance of DGCNN Part Segmentation Network.

        Args:
            k (optional): the number of k-nearest neighbors for the Edge-Conv. Defaults to 20.
            size_global_feature (optional): the size for the global feature. Defaults to 1024.
            use_geometry_nn (optional): if True compute the nearest neighbors in coordinate space
            instead of feature space.
            use_tnet (optional): if True use the points T-Net. Defaults to False.
            dropout_p (optional): the dropout probability. Defaults to 0.5.
            num_classes (optional): the number of classes for the categorical vector. Defaults to 10.
            num_classes_part: (optional): the number of overal part segmentation classes Defaults to 10.
        """
        super(DGCNNPartSegmentation, self).__init__()

        self.num_classes_part = num_classes_part
        self.k = k
        self.use_pts_tnet = use_tnet
        self.use_geometry_nn = use_geometry_nn
        self.slope = 0.2

        if self.use_pts_tnet:
            self.tnet = TNet()

        self.conv_1 = Sequential(
            Conv2d(6, 64, kernel_size=1, bias=False),
            BatchNorm2d(64),  # type: ignore
            LeakyReLU(negative_slope=0.2),
        )
        self.conv_2 = Sequential(
            Conv2d(64, 64, kernel_size=1, bias=False),
            BatchNorm2d(64),  # type: ignore
            LeakyReLU(negative_slope=0.2),
        )
        self.conv_3 = Sequential(
            Conv2d(64 * 2, 64, kernel_size=1, bias=False),
            BatchNorm2d(64),  # type: ignore
            LeakyReLU(negative_slope=0.2),
        )
        self.conv_4 = Sequential(
            Conv2d(64, 64, kernel_size=1, bias=False),
            BatchNorm2d(64),  # type: ignore
            LeakyReLU(negative_slope=0.2),
        )
        self.conv_5 = Sequential(
            Conv2d(64 * 2, 64, kernel_size=1, bias=False),
            BatchNorm2d(64),  # type: ignore
            LeakyReLU(negative_slope=0.2),
        )
        self.conv_6 = Sequential(
            Conv1d(192, size_global_feature, kernel_size=1, bias=False),
            BatchNorm1d(size_global_feature),  # type: ignore
            LeakyReLU(negative_slope=0.2),
        )
        self.conv_7 = Sequential(
            Conv1d(num_classes, 64, kernel_size=1, bias=False),
            BatchNorm1d(64),  # type: ignore
            LeakyReLU(negative_slope=0.2),
        )

        size_in_conv_8 = 64 + size_global_feature + 64 + 64 + 64
        self.conv_8 = Sequential(
            Conv1d(size_in_conv_8, 256, kernel_size=1, bias=False),
            BatchNorm1d(256),  # type: ignore
            LeakyReLU(negative_slope=0.2),
        )

        self.dropout = Dropout(dropout_p)
        self.conv_9 = Sequential(
            Conv1d(256, 256, kernel_size=1, bias=False),
            BatchNorm1d(256),  # type: ignore
            LeakyReLU(negative_slope=0.2),
        )

        self.conv_10 = Sequential(
            Conv1d(256, 128, kernel_size=1, bias=False),
            BatchNorm1d(128),  # type: ignore
            LeakyReLU(negative_slope=0.2),
        )
        self.conv_11 = Conv1d(128, num_classes_part, kernel_size=1, bias=False)

    def forward(self, x: Tensor, vector_cat: Tensor) -> Tuple[Tensor, Union[Tensor, None]]:
        """Process input point clouds and produces per points claffication scores.

        Args:
            x: The input clouds with shape (B, NUM_PTS, DIM).
            vector_cat: the one hot encoding categorical vector (B, NUM_CLASSES).

        Returns:
            A tuple containing:
                - The computed classification scores with shape (B, NUM_PTS, NUM_CLASSES_PART).
                - The learned transformation matrix for the input points.
        """
        batch_size = x.size(0)
        num_points = x.size(1)

        if self.use_pts_tnet:
            x0 = get_graph_feature(x, k=self.k)
            x0 = torch.permute(x0, (0, 3, 1, 2))
            trans = self.tnet(x0)
            x = torch.bmm(x, trans)
        else:
            trans = None

        indices = None
        if self.use_geometry_nn:
            _, indices, _ = knn_points(x, x, K=self.k)

        x = get_graph_feature(x, k=self.k, indices=indices)
        x = torch.permute(x, (0, 3, 1, 2))

        x = self.conv_1(x)
        x = self.conv_2(x)
        x_1 = x.max(dim=-1, keepdim=False)[0]

        x = torch.transpose(x_1, 2, 1)
        x = get_graph_feature(x, k=self.k, indices=indices)
        x = torch.permute(x, (0, 3, 1, 2))
        x = self.conv_3(x)
        x = self.conv_4(x)
        x_2 = x.max(dim=-1, keepdim=False)[0]

        x = torch.transpose(x_2, 2, 1)
        x = get_graph_feature(x, k=self.k, indices=indices)
        x = torch.permute(x, (0, 3, 1, 2))
        x = self.conv_5(x)
        x_3 = x.max(dim=-1, keepdim=False)[0]

        x = torch.cat((x_1, x_2, x_3), dim=1)

        x = self.conv_6(x)
        x = x.max(dim=-1, keepdim=True)[0]

        vector_cat = vector_cat.reshape(batch_size, -1, 1)
        vector_cat = self.conv_7(vector_cat)

        x = torch.cat((x, vector_cat), dim=1)
        x = repeat(x, "b ch n -> b ch (n r)", r=num_points)

        x = torch.cat((x, x_1, x_2, x_3), dim=1)

        x = self.conv_8(x)
        x = self.dropout(x)
        x = self.conv_9(x)
        x = self.dropout(x)
        x = self.conv_10(x)
        x = self.conv_11(x)
        x = torch.transpose(x, 2, 1)

        return x, trans
