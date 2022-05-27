from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

from core.base import base_inference_model
import torch
import torch.nn as nn


def custom_batch_norm(input, channels, with_mean):
    eps = 0.00001
    out = torch.zeros_like(input)
    for i in range(channels):
        if with_mean:
            mu = torch.mean(input, dim=1)
        else:
            mu = 0
        var = torch.sqrt(torch.var(input, dim=1)+eps)
        out[:,i,...] = (input[:, i, ...] - mu)/var
    return out


class BasicBlock(nn.Module):
    expansion = 1
    def __init__(self, in_layer, out_layer, stride=1, downsample=None, use_bias=True):
        super(BasicBlock, self).__init__()
        self.conv1 = nn.Conv2d(in_layer, out_layer, kernel_size=3, stride=stride, padding=1, bias=use_bias)
        self.bn1 = nn.BatchNorm2d(out_layer, track_running_stats=False)
        self.relu = nn.ReLU(inplace=True)
        self.conv2 = nn.Conv2d(out_layer, out_layer, kernel_size=3, stride=stride, padding=1, bias=use_bias)
        self.bn2 = nn.BatchNorm2d(out_layer, track_running_stats=False)
        self.downsample = downsample
        self.stride = stride

    def forward(self, x):
        residual = x
        out = self.conv1(x)
        out = self.bn1(out)
        out = self.relu(out)
        out = self.conv2(out)
        out = self.bn2(out)
        if self.downsample is not None:
            residual = self.downsample(x)
        out += residual
        out = self.relu(out)
        return out

    
class Resnet(base_inference_model.InferenceModel, nn.Module):
    """
        Class Implementing the ResNet model.
        Methods:
            - setOpts
                inputs: a Dict containing the key and value for a new configuration setting
            - forward
                inputs: signal (measured signal);
                outputs: Estimated parameters
    """

    def __init__(self, config_object):
        super(Resnet, self).__init__()
        self.__name__ = 'RESNET'
        self.__require_initial_guess__ = False
        self.use_bias = config_object.args.inference.useBias
        self.args = config_object.args
        self.__buildNetwork__()

    def __buildNetwork__(self):
        self.input_planes = self.args.inference.outputChannelsLayer1
        self.conv1 = nn.Conv2d(self.args.inference.inputChannels, self.args.inference.outputChannelsLayer1, kernel_size=1, stride=1, padding=0, bias=self.use_bias)
        self.bn1 = nn.BatchNorm2d(self.args.inference.outputChannelsLayer1, track_running_stats=False)
        self.relu = nn.ReLU(inplace=True)
        
        self.layer1 = self.__makeLayer__(BasicBlock, self.args.inference.outputChannelsLayer2, self.args.inference.convLayersInResidualBlock)
        self.layer2 = self.__makeLayer__(BasicBlock, self.args.inference.outputChannelsLayer3, self.args.inference.convLayersInResidualBlock)
        self.layer3 = self.__makeLayer__(BasicBlock, self.args.inference.outputChannelsLayer4, self.args.inference.convLayersInResidualBlock)
        self.layer4 = self.__makeLayer__(BasicBlock, self.args.inference.outputChannelsLayer5, self.args.inference.convLayersInResidualBlock)
        self.layer5 = self.__makeLayer__(BasicBlock, self.args.inference.outputChannelsLayer6, self.args.inference.convLayersInResidualBlock)
        self.layer6 = self.__makeLayer__(BasicBlock, self.args.inference.outputChannelsLayer7, self.args.inference.convLayersInResidualBlock)
        self.layer_out = nn.Conv2d(self.args.inference.outputChannelsLayer7, self.args.inference.outputChannels, kernel_size=1, stride=1, padding=0, bias=self.use_bias)
        self.use_mean = self.args.inference.useMeanBatchNorm

        for m in self.modules():
            if isinstance(m, nn.Conv2d):
                n = m.kernel_size[0] * m.kernel_size[1] * m.out_channels
                torch.nn.init.kaiming_normal_(m.weight)
            elif isinstance(m, nn.BatchNorm2d):
                m.weight.data.fill_(1)
                m.bias.data.zero_()

    def __makeLayer__(self, block, channels, blocks, stride=1):
        downsample = None
        if stride != 1 or self.input_planes != channels*block.expansion:
            downsample = nn.Sequential(nn.Conv2d(self.input_planes, channels*block.expansion,
                                                 kernel_size=1, stride=stride, bias=self.use_bias),
                                       nn.BatchNorm2d(channels*block.expansion, track_running_stats=False))
        layers = []
        layers.append(block(self.input_planes, channels, stride, downsample, self.use_bias))
        self.input_planes = channels*block.expansion
        for _ in range(1, blocks):
            layers.append(block(self.input_planes, channels))
        return nn.Sequential(*layers)

    def forward(self, inputs):
        signal = inputs
        x = self.conv1(signal)
        x = self.bn1(x)
        # x = custom_batch_norm(x, self.args.inference.inputChannels, self.use_mean)
        x = self.relu(x)
        x = self.layer1(x)
        x = self.layer2(x)
        x = self.layer3(x)
        x = self.layer4(x)
        x = self.layer5(x)
        x = self.layer6(x)
        out = self.layer_out(x)
        return out
