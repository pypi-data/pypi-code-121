from torch import nn


class MLP(nn.Module):
    def __init__(self, in_channels, hidden_size=256, projection_size=4096):
        super(MLP, self).__init__()
        self.net = nn.Sequential(nn.Linear(in_channels, hidden_size),
                                 nn.BatchNorm1d(hidden_size),
                                 nn.ReLU(inplace=True),
                                 nn.Linear(hidden_size, projection_size))

    def forward(self, x):
        return self.net(x)
