import json
import subprocess
from os.path import isfile
import zipfile

import torch
from torch.utils.data import DataLoader
import numpy as np
import pandas as pd

from sequence_models.datasets import UniRefDataset, FFDataset
from sequence_models.collaters import LMCollater, StructureCollater, MLMCollater, StructureImageCollater
from sequence_models.constants import PROTEIN_ALPHABET, PAD
from sequence_models.convolutional import ByteNetLM
from sequence_models.losses import MaskedCrossEntropyLoss
from sequence_models.gnn import Struct2SeqDecoder
from sequence_models.structure import StructureConditionedBytenet
from sequence_models.utils import get_metrics


ds = UniRefDataset('data/uniclust/cath/', 'test', structure=False, pdb=True, p_drop=0.0)
mlmc = MLMCollater(PROTEIN_ALPHABET)
lmc = LMCollater(PROTEIN_ALPHABET)
mlmdl = DataLoader(ds, batch_size=3, shuffle=False, collate_fn=mlmc)
lmdl = DataLoader(ds, batch_size=3, shuffle=False, collate_fn=lmc)
for batch in mlmdl:
    break
mlmsrc, mlmtgt, mlmmask = batch
for batch in lmdl:
    break
lmsrc, lmtgt, lmmask = batch
mlmsrc.shape
lmsrc.shape
lmsrc[0]
mlmsrc[0]
lm = ByteNetLM(len(PROTEIN_ALPHABET), 2, 4, 16, 5, 128, PROTEIN_ALPHABET.index(PAD), causal=True)
mlm = ByteNetLM(len(PROTEIN_ALPHABET), 2, 4, 16, 5, 128, PROTEIN_ALPHABET.index(PAD), causal=False)

# test the lm
out1 = lm(lmsrc)
out1.shape
out2 = lm(lmsrc[:, :50])
torch.allclose(out1[:, :50], out2[:, :50])

# test the mlm
input_mask = (mlmsrc != PROTEIN_ALPHABET.index(PAD)).float()
out3 = mlm(mlmsrc, input_mask=input_mask.unsqueeze(-1))
mlmsrc2 = torch.cat([mlmsrc, torch.ones((3, 10)).long() * PROTEIN_ALPHABET.index(PAD)], dim=-1)
input_mask2 = (mlmsrc2 != PROTEIN_ALPHABET.index(PAD)).float()
out4 = mlm(mlmsrc2, input_mask=input_mask2.unsqueeze(-1))
torch.allclose(out3, out4[:, :-10])



ds1 = UniRefDataset('data/uniclust/cath/', 'test', structure=True, pdb=True, p_drop=0.0)
data = ds1[11]
data[4]

collater = StructureCollater(LMCollater(PROTEIN_ALPHABET))
lmdl = DataLoader(ds1, batch_size=3, shuffle=False, collate_fn=collater)
for batch in lmdl:
    break
src, tgt, mask, nodes, edges, connections, edge_mask = batch
data = {}
data['src'] = src.numpy()
data['tgt'] = tgt.numpy()
data['mask'] = mask.numpy()
data['nodes'] = nodes.numpy()
data['edges'] = edges.numpy()
data['connections'] = connections.numpy()
data['edge_mask'] = edge_mask.numpy()
np.savez_compressed('batch_longer.npz', **data)


se1, dist1, omega1, theta1, phi1 = ds1[10]
se2, dist2, omega2, theta2, phi2 = ds2[0]
len(se2)
se1
se2






collater = StructureCollater(LMCollater(PROTEIN_ALPHABET))
dl = DataLoader(ds, batch_size=3, shuffle=True, collate_fn=collater)

metadata = np.load('data/uniclust/cath/lengths_and_offsets.npz')

for batch in dl:
    break
model = StructureConditionedBytenet(len(PROTEIN_ALPHABET), 8, 8, 16, 4, 3, 2,
                                    4, 4, 3, 2).cuda()
src, tgt, mask, structure, str_mask = batch
src = src.cuda()
tgt = tgt.cuda()
mask = mask.cuda()
structure = structure.cuda()
str_mask = str_mask.cuda()
input_mask = (src != 27).float()
print(torch.any(torch.isnan(src)), torch.any(torch.isnan(structure)))
with torch.no_grad():
    c = model.conditioner.embedder(structure, input_mask=str_mask.unsqueeze(-1))
    attn = model.conditioner.attention.layer(c)
    n, ell, _, _ = c.shape
    attn = attn.view(n, -1)
    attn = attn.masked_fill_(str_mask.view(n, -1).bool(), float('-inf'))
    attn = torch.nn.functional.softmax(attn, dim=-1)
    outputs = model(src, structure, input_mask.unsqueeze(-1), str_mask.unsqueeze(-1))
nan = torch.isnan(outputs)
model = Struct2SeqDecoder(len(PROTEIN_ALPHABET), 10, 6,
                          16, num_decoder_layers=2,
                          dropout=0.0, use_mpnn=True).cuda()
src, tgt, mask, nodes, edges, connections, edge_mask = batch
nodes = nodes.cuda()
edges = edges.cuda()
connections = connections.cuda()
edge_mask = edge_mask.cuda()
src = src.cuda()
mask = mask.cuda()
output = model(nodes, edges, connections.long(), src, edge_mask)
output[1, 2, :].sum()
output[0, 2, :].sum()
src2 = src
src2[1, 3:] = 1
src2[0, 10:] = 1
output2 = model(nodes, edges, connections.long(), src2, edge_mask)
output2[1, 2, :].sum()
output2[0, 2, :].sum()


loss_func = MaskedCrossEntropyLoss()

input_mask = (src != 27).float()

with torch.no_grad():
    out1 = model(src)
    out2 = model(src, input_mask=input_mask.unsqueeze(-1))
    out3 = model(src[:, :-1500])
    out4 = model(src[:, :-1500], input_mask=input_mask[:, :-1500].unsqueeze(-1))

sampler1 = SortishSampler(np.arange(100), 10, num_replicas=1, rank=0)
sampler2 = SortishSampler(np.arange(1000), 10, num_replicas=8, rank=2)
first = list(sampler1.__iter__())
sampler1.set_epoch(1)
second = list(sampler1.__iter__())
first[0] in second


metrics = get_metrics('/home/kevyan/workspace/pt/pretrain1/pretrain_dataset_uniref50_task_mlm/stdout.txt')
metrics.tail()

data_stem = '/home/kevyan/workspace/data/uniclust/UniRef30_2020_03_a3m.'
dataset = FFDataset(data_stem, max_len=np.inf)
seqs = dataset[100001]
len(seqs)
seqs[0].allclose(seqs[1])
seqs.shape


