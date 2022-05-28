import torch
import torch.nn as nn


class MLP(nn.Module):
    def __init__(self, layer_sizes, last_actv=False):
        super(MLP, self).__init__()

        layers = []
        for i, (in_size, out_size) in enumerate(zip(layer_sizes[:-1], layer_sizes[1:])):
            layers.append(nn.Linear(in_size, out_size))
            if last_actv or i < len(layer_sizes) - 2:
                layers.append(nn.ReLU())

        self.net = nn.Sequential(*layers)

    def forward(self, x):
        x = self.net(x)
        return x


if __name__ == "__main__":
    model = MLP([256, 512, 256, 128])
    print(model)

    rand_x = torch.rand(4, 256)
    output = model(rand_x)

    assert output.shape == (4, 128)
