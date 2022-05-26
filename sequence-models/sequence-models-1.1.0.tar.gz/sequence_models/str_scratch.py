import numpy as np
import h5py
import torch
from sequence_models.metrics import LPrecision


sizes = [1029007, 293875]
edges = np.cumsum(sizes)
with open('catted') as f:
    data = f.read(sizes[0])


structures = [np.load(fname) for fname in ['000000.npz', '000001.npz']]
with h5py.File('str01.h5', 'w') as f:
    for i, s in enumerate(structures):
        data = np.stack([s[k] for k in ['dist', 'omega', 'theta', 'phi']])
        f.create_dataset(str(i), data=data)

# %timeit with h5py.File('str01.h5', 'r') as f: data = f['1'][:]

pre = LPrecision()
prediction = torch.randn(3, 100, 100)
tgt = torch.randn(3, 100, 100)
mask = torch.ones_like(tgt, dtype=torch.bool)
ells = torch.ones(3) * 100
pre(prediction, tgt, mask, ells)
