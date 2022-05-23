#!/usr/bin/env python3
"""
A playground file about using Transformer type clf
However, it did not show better performace yet
Probably not a good idea

author: jy, nkmtmsys
"""

import math
import torch
import torch.nn as nn
import torch.nn.functional as func
from torch.nn import TransformerEncoder, TransformerEncoderLayer
import ageas.classifier as classifier


class Positional_Encoding(nn.Module):
    """
    Inject some information about the relative or absolute position
    of the tokens in the sequence.
    The positional encodings have the same dimension as the embeddings,
    so that the two can be summed.
    Here, we use sine and cosine functions of different frequencies.
    .. math:
        \text{PosEncoder}(pos, 2i) = sin(pos/10000^(2i/d_model))
        \text{PosEncoder}(pos, 2i+1) = cos(pos/10000^(2i/d_model))
        \text{where pos is the word position and i is the embed idx)
    Args:
        d_model: the embed dim (required).
        dropout: the dropout value (default=0.1).
    Examples:
        >>> pos_encoder = Positional_Encoding(d_model)
    """

    def __init__(self, d_model, dropout = 0.1):
        super(Positional_Encoding, self).__init__()
        self.dropout = nn.Dropout(p=dropout)
        pe = torch.zeros(d_model, d_model)
        position = torch.arange(0, d_model, dtype=torch.float).unsqueeze(1)
        div_term = torch.exp(torch.arange(0, d_model, 2).float() *
                                    (-math.log(10000.0) / d_model))
        pe[:, 0::2] = torch.sin(position * div_term)
        pe[:, 1::2] = torch.cos(position * div_term)
        pe = pe.unsqueeze(0).transpose(0, 1)
        self.register_buffer('pe', pe)

    def forward(self, x):
        """
        Args:
            x: the sequence fed to the positional encoder model (required).
        Shape:
            x: [sequence length, batch size, embed dim]
            output: [sequence length, batch size, embed dim]
        Examples:
            >>> output = pos_encoder(x)
        """
        x = x + self.pe[:x.size(0), :]
        return self.dropout(x)



class Transformer(nn.Module):
    """
    Container module with an encoder, a transformer module, and a decoder.
    """
    def __init__(self,
                id, # model id
                num_features, # the number of expected features
                has_mask = True, # whether using mask or not
                emsize = 512, # size after encoder
                nhead = 8, # number of heads in the multiheadattention models
                nhid = 200, # number of hidden units per layer
                nlayers = 2, # number of layers
                dropout = 0.5, # dropout ratio
                learning_rate = 0.1,
                n_class = 2, ): # number of class for classification
        super(Transformer, self).__init__()
        self.id = id
        self.has_mask = has_mask
        self.model_type = 'Transformer'
        self.num_features = num_features
        self.emsize = emsize
        self.mask = None
        self.encoder = nn.Linear(num_features, emsize)
        self.pos_encoder = Positional_Encoding(emsize, dropout)
        encoder_layers = TransformerEncoderLayer(emsize, nhead, nhid, dropout)
        self.transformer_encoder = TransformerEncoder(encoder_layers, nlayers)
        self.decoder = nn.Linear(emsize, n_class)
        #self.optimizer = torch.optim.AdamW(self.parameters(), lr=learning_rate)
        self.optimizer = None
        self.loss_func = nn.CrossEntropyLoss()
        # init_weights
        initrange = 0.1
        nn.init.zeros_(self.decoder.bias)
        nn.init.uniform_(self.decoder.weight, -initrange, initrange)

    def _make_square_subsequent_mask(self, size):
        mask = (torch.triu(torch.ones(size, size)) == 1).transpose(0, 1)
        return mask.float().masked_fill(mask == 0,
                                        float('-inf')).masked_fill(mask == 1,
                                                                    float(0.0))

    def forward(self, input):
        if self.has_mask:
            if self.mask is None or self.mask.size(0) != len(input):
                self.mask = self._make_square_subsequent_mask(len(input))
        else:
            self.mask = None
        input = self.encoder(input)
        input = self.pos_encoder(input)
        output = self.transformer_encoder(input, self.mask)
        output = torch.flatten(output, start_dim = 1)
        output = func.softmax(self.decoder(output), dim = -1)
        return output



class Make(classifier.Make_Template):
    """
    Analysis the performances of Transformer based approaches
    with different hyperparameters
    Find the top settings to build
    """
    # Perform classifier training process for given times
    def train(self, dataSets, test_split_set):
        testData = classifier.reshape_tensor(dataSets.dataTest)
        testLabel = dataSets.labelTest
        num_features = len(dataSets.dataTest[0])
        for id in self.configs:
            model = Transformer(id, num_features, **self.configs[id]['config'])
            epoch = self.configs[id]['epoch']
            batch_size = self.configs[id]['batch_size']
            self._train_torch(epoch, batch_size, model, dataSets)
            # local test
            accuracy = self._evaluate_torch(model,
                                            testData,
                                            testLabel,
                                            test_split_set)
            self.models.append([model, accuracy])


""" For testing """
# if __name__ == '__main__':
#     param = {
#                 'has_mask': True,
#                 'emsize': 512,
#                 'nhead': 8,
#                 'nhid': 200,
#                 'nlayers': 2,
#                 'dropout': 0.5,
#                 'learning_rate': 0.1
#             }
#     data = torch.rand((3,1,22090))
#     model = Transformer(id = 'a', num_features = 22090, **param)
#     model.train()
#     if model.optimizer is not None: model.optimizer.zero_grad()
#     out = model(data)
#     print(out)
#     loss = model.loss_func(out, torch.randint(0,1,(3,)))
#     loss.backward()
#     if model.optimizer is not None: model.optimizer.step()
