import torch


class LinearEncoder(torch.nn.Module):
    def __init__(self, input_dimension):
        super().__init__()
        self.input_dimension = input_dimension

    def forward(self, x):
        return x
