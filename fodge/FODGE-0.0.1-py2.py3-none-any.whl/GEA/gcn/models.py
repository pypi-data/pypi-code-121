import torch.nn as nn
import torch.nn.functional as F
from GEA.gcn.layers import GraphConvolution


class GCN(nn.Module):
    def __init__(self, nfeat, nhid, nclass, dropout, multilabel):
        super(GCN, self).__init__()

        self.gc1 = GraphConvolution(nfeat, nhid)
        self.gc2 = GraphConvolution(nhid, nclass)
        self.dropout = dropout
        self.multi = multilabel

    def forward(self, x, adj):
        x = F.relu(self.gc1(x, adj))
        x = F.dropout(x, self.dropout, training=self.training)
        hid = x
        x = self.gc2(x, adj)
        if self.multi:
            return hid, x
        else:
            return hid, F.log_softmax(x, dim=1)
