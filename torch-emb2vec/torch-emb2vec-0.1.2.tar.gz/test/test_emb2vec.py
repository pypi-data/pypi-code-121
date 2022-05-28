from torch_emb2vec import (AverageToVec, ConcatToVec, ConvToVec)
import torch


def test1():
    # toy data
    num_emb, emb_dim = 1000, 256
    emb = torch.nn.Embedding(num_emb, emb_dim)
    batch_sz, seq_len = 5, 128
    inputs = torch.randint(num_emb, (batch_sz, seq_len))
    z = emb(inputs)
    # Averaging
    avg = AverageToVec()
    vec = avg(z)
    assert list(vec.shape) == [5, 128]
    # Concat
    con = ConcatToVec()
    vec = con(z)
    assert list(vec.shape) == [5, 32768]
    # Conv1D
    conv1 = ConvToVec(
        seq_len=z.shape[1], emb_dim=z.shape[2], num_output=768)
    vec = conv1(z)
    assert list(vec.shape) == [5, 768]
    # Conv1D hashing
    conv2 = ConvToVec(
        seq_len=z.shape[1], emb_dim=z.shape[2], num_output=2048, hashed=True)
    vec = conv2(z)
    assert list(vec.shape) == [5, 2048]
    assert int(vec.max()) == 1
    assert int(vec.min()) == 0
