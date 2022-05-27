from torch import nn


class LinearClassifier(nn.Module):
    """Linear layer to train on top of frozen features"""
    def __init__(self,
                 dim,
                 num_labels=1000,
                 dropout_rate=0.3,
                 use_bn=False,
                 log_softmax=False):
        super(LinearClassifier, self).__init__()
        self.num_labels = num_labels
        self.use_bn = use_bn
        self.log_softmax = log_softmax

        self.dropout = nn.Dropout(dropout_rate)
        self.bn = nn.BatchNorm1d(dim)

        self.linear = nn.Linear(dim, 128)
        self.linear.weight.data.normal_(mean=0.0, std=0.01)
        self.linear.bias.data.zero_()
        self.relu = nn.ReLU()

        self.dropout2 = nn.Dropout(dropout_rate)
        self.bn2 = nn.BatchNorm1d(128)

        self.linear2 = nn.Linear(128, num_labels)
        self.linear2.weight.data.normal_(mean=0.0, std=0.01)
        self.linear2.bias.data.zero_()

    def forward(self, x):
        # flatten
        x = x.view(x.size(0), -1)
        # Dropout
        x = self.dropout(x)
        if self.use_bn:
            x = self.bn(x)
        # 1. linear layer
        x = self.linear(x)
        x = self.relu(x)
        x = self.dropout2(x)
        if self.use_bn:
            x = self.bn2(x)
        # 2. linear layer
        x = self.linear2(x)
        if self.log_softmax:
            return nn.LogSoftmax(dim=1)(x)
        else:
            return x
