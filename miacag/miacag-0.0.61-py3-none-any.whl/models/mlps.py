from torch import nn


class projection_MLP(nn.Module):
    def __init__(self, in_dim, out_dim, num_layers=2, dimension='2D'):
        super().__init__()
        hidden_dim = out_dim
        self.dimension = dimension
        self.hidden_dim = hidden_dim
        self.in_dim = in_dim
        self.num_layers = num_layers

        self.layer1 = nn.Sequential(
            nn.Linear(in_dim, hidden_dim),
            nn.BatchNorm1d(hidden_dim),
            nn.ReLU(inplace=True)
        )

        # self.layer2 = nn.Sequential(
        #     nn.Linear(hidden_dim, hidden_dim),
        #     nn.BatchNorm1d(hidden_dim),
        #     nn.ReLU(inplace=True)
        # )
        self.layer3 = nn.Sequential(
            nn.Linear(hidden_dim, out_dim),
            nn.BatchNorm1d(out_dim, affine=False)  # Page:5, Paragraph:2
        )

    def forward(self, x):
        #x = x[-1]
        if self.dimension in ['3D', '2D+T']:
            x = x.mean(dim=(-3, -2, -1))
        #else:
        #    x = x.mean(dim=(-2, -1))
        x = x.view(-1, self.in_dim)
        if self.num_layers == 2:
            x = self.layer1(x)
            x = self.layer3(x)
        elif self.num_layers == 3:
            x = self.layer1(x)
            x = self.layer2(x)
            x = self.layer3(x)

        return x


class prediction_MLP(nn.Module):
    def __init__(self, in_dim=2048):
        super().__init__()
        out_dim = in_dim
        hidden_dim = int(out_dim / 4)

        self.layer1 = nn.Sequential(
            nn.Linear(in_dim, hidden_dim),
            nn.BatchNorm1d(hidden_dim),
            nn.ReLU(inplace=True)
        )
        self.layer2 = nn.Linear(hidden_dim, out_dim)

    def forward(self, x):
        x = self.layer1(x)
        x = self.layer2(x)

        return x