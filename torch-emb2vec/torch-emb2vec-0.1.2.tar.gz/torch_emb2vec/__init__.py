__version__ = '0.1.2'

import torch


class AverageToVec(torch.nn.Module):
    """ Convert W2V embedding to vector by averaging over the sequence

    Example:
    --------
    assert z.shape = (batch_sz, seq_len, emb_dim)
    avg = AverageToVec()
    vec = avg(z)
    assert vec.shape = (batch_sz, emb_dim)
    """
    def __init__(self):
        super(AverageToVec, self).__init__()

    def forward(self, x: torch.Tensor):
        return torch.mean(x, axis=2)


class ConcatToVec(torch.nn.Module):
    """ Convert W2V embedding to vector by concatenation

    Example:
    --------
    assert z.shape = (batch_sz, seq_len, emb_dim)
    con = ConcatToVec()
    vec = con(z)
    assert vec.shape = (batch_sz, seq_len * emb_dim)
    """
    def __init__(self):
        super(ConcatToVec, self).__init__()
        self.flat = torch.nn.Flatten()

    def forward(self, x: torch.Tensor):
        return self.flat(x)


class ConvToVec(torch.nn.Module):
    """ Convert W2V embedding to vector with 1D-Conv

    Parameter:
    ----------
    emb_dim : int
        The embedding dimension

    seq_len : int
        The sequence length of the embedding

    num_output : int
        The output dimension should

    Example:
    --------
    assert z.shape = (batch_sz, seq_len, emb_dim)
    con = ConvToVec()
    vec = con(z)
    assert vec.shape = (batch_sz, num_output)
    """
    def __init__(self,
                 seq_len: int,
                 emb_dim: int,
                 num_output: int,
                 seed: int = 42,
                 hashed: bool = False,
                 trainable: bool = False):
        super(ConvToVec, self).__init__()
        self.hashed = hashed
        # compute kernel size and output channel dim
        kernel_size = int(seq_len // 2 + 1)
        new_seq_len = int(seq_len - (kernel_size - 1))
        out_channel = int(num_output // new_seq_len)
        # the layers
        self.conv = torch.nn.Conv1d(
            in_channels=emb_dim,
            out_channels=out_channel,
            kernel_size=kernel_size,
            bias=False)
        self.conv.weight.requires_grad = trainable
        self.flat = torch.nn.Flatten()
        # random projection
        if seed:
            torch.manual_seed(seed)
        torch.nn.init.xavier_normal_(self.conv.weight)

    def forward(self, x: torch.Tensor):
        h = torch.transpose(x, 1, 2)
        h = self.conv(h)
        h = self.flat(h)
        if self.hashed:
            h = torch.heaviside(h, torch.tensor(0.0))
        return h
