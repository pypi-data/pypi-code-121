from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import torch
import torch.nn as nn
import torch.nn.functional as f


class Rnn(nn.Module):
    def __init__(self, channels_input, out_channels_l1, out_channels_l2, out_channels_l3, channels_output, args_):
        super(Rnn, self).__init__()
        self.input_layer = nn.Conv2d(channels_input, out_channels_l1, kernel_size=3, stride=1, padding=1)
        self.conv_layer_2 = nn.Conv2d(out_channels_l1, out_channels_l2, kernel_size=3, stride=1, padding=1)
        self.conv_layer_3 = nn.Conv2d(out_channels_l2, out_channels_l3, kernel_size=3, stride=1, padding=1)
        self.output_layer = nn.Conv2d(out_channels_l3, channels_output, kernel_size=1, stride=1, padding=0)
        self.gru_layer_1 = nn.GRU(out_channels_l1, out_channels_l1)
        self.gru_layer_2 = nn.GRU(out_channels_l3, out_channels_l3)


        self.gru_1_channelSize = out_channels_l1
        self.gru_2_channelSize = out_channels_l3
        self.size_c1 = out_channels_l1
        self.size_c3 = out_channels_l3
        self.args = args_


    def __setGruShapes__(self, x):
        shape_input = x[0,0].size()
        shape_gru_1 = [len(x)] + list(shape_input) + [self.size_c1]
        shape_gru_2 = [len(x)] + list(shape_input) + [self.size_c3]
        permute_list_forw = [0] + [dim for dim in range(2, len(shape_input)+2)] + [1]
        permute_list_back = [0] + [-1] + [dim for dim in range(1, len(shape_input)+1)]
        self.shape_gru_1 = shape_gru_1
        self.shape_gru_2 = shape_gru_2
        self.permute_forward = permute_list_forw
        self.permute_backward =permute_list_back

    def __forwardGRU__(self, x, hs, gru_layer, sizeGRUforward, sizeGRUbackward):
        h1_gru = x.permute(self.permute_forward).contiguous().view(-1, sizeGRUforward).unsqueeze(0)
        h1_gru1, hs = gru_layer(h1_gru, hs)
        h1_gru = h1_gru1.squeeze(0).view(sizeGRUbackward).permute(self.permute_backward).contiguous()
        return h1_gru, hs

    def forward(self, input, hidden_states):
        self.__setGruShapes__(input)
        
        h1 = self.input_layer(input)
        h1 = f.relu(h1)
        h1_gru, hidden_states[0] = self.__forwardGRU__(h1, hidden_states[0], self.gru_layer_1, self.gru_1_channelSize, self.shape_gru_1)
        h2 = self.conv_layer_2(h1_gru)
        h2 = f.relu(h2)
        h3 = self.conv_layer_3(h2)
        h3 = f.relu(h3)
        h2_gru, hidden_states[1] = self.__forwardGRU__(h3, hidden_states[1], self.gru_layer_2, self.gru_2_channelSize, self.shape_gru_2)
        output = self.output_layer(h2_gru)
        return output, hidden_states