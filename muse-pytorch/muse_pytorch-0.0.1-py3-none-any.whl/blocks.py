import torch
from torch import nn
from torch.nn.init import kaiming_normal_, zeros_


def init_weights(m):

    for l in m.children():
        if isinstance(l, nn.Linear):
            kaiming_normal_(l.weight)

            if l.bias is not None:
                zeros_(l.bias)


class MultiViewEncoder(nn.Module):

    def __init__(self, in_features_x: int, in_features_y: int, sm_latent_dim: int = 128, joint_latent_dim: int = 100) -> None:
        super().__init__()

        self.in_features_x = in_features_x
        self.in_features_y = in_features_y
        self.sm_latent_dim = sm_latent_dim
        self.joint_latent_dim = joint_latent_dim

        self.x_encoder = Encoder(
            in_features=self.in_features_x, hidden_dim=self.sm_latent_dim)
        self.y_encoder = Encoder(
            in_features=self.in_features_y, hidden_dim=self.sm_latent_dim)
        self.joint_encoder = Encoder(
            in_features=self.sm_latent_dim*2, hidden_dim=self.joint_latent_dim)

        self.apply(init_weights)

    def forward(self, x, y):
        x_latent = self.x_encoder(x)
        y_latent = self.y_encoder(y)

        joint_latent = torch.concat((x_latent, y_latent), dim=1)
        joint_latent = self.joint_encoder(joint_latent)

        return joint_latent, x_latent, y_latent


class Encoder(nn.Module):
    def __init__(self, in_features: int, hidden_dim: int = 128) -> None:
        super().__init__()

        self.in_features = in_features
        self.hidden_dim = hidden_dim

        self.fc1 = nn.Linear(in_features=self.in_features,
                             out_features=self.hidden_dim)
        self.fc2 = nn.Linear(in_features=self.hidden_dim,
                             out_features=self.hidden_dim)

        self.apply(init_weights)

    def forward(self, x):
        x = self.fc1(x)
        x = self.fc2(x)

        return x


class Decoder(nn.Module):
    def __init__(self, in_features: int, out_features: int, hidden_dim: int = 128) -> None:
        super().__init__()

        self.in_features = in_features
        self.out_features = out_features
        self.hidden_dim = hidden_dim

        self.fc1 = nn.Linear(in_features=self.in_features,
                             out_features=hidden_dim)
        self.fc2 = nn.Linear(in_features=self.hidden_dim,
                             out_features=hidden_dim)
        self.fc3 = nn.Linear(in_features=self.hidden_dim,
                             out_features=out_features)

        self.apply(init_weights)

    def forward(self, x):
        x = self.fc1(x)
        x = self.fc2(x)
        x = self.fc3(x)

        return x


class WeightMatrix(torch.nn.Module):
    def __init__(self, joint_latent_dim: int = 100):
        super().__init__()
        self.joint_latent_dim = joint_latent_dim

        self.weight = torch.nn.Parameter(
            torch.zeros((joint_latent_dim, joint_latent_dim)))
        self.bias = None

        kaiming_normal_(self.weight)

    def fnorm(self):
        return torch.norm(self.weight, p='fro')

    def forward(self, x):
        return torch.matmul(x, self.weight)


class MUSELoss:
    def __init__(self, weight_penalty: float, triplet_lambda: float):
        self.weight_penality = weight_penalty
        self.triplet_lambda = triplet_lambda

    def __call__():
        return
