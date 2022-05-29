#coding:utf-8
from __future__ import print_function, division, absolute_import
import os
os.environ['CUDA_VISIBLE_DEVICES'] =  '0'
import sys
import torch
import cv2
from imgaug import augmenters as iaa
import numpy as np
import torch.nn.functional as F
from collections import OrderedDict
os.environ['KMP_DUPLICATE_LIB_OK']='True'
pwd = os.path.abspath('./')
RESIZE_SIZE=112


"""
ResNet code gently borrowed from
https://github.com/pytorch/vision/blob/master/torchvision/models/resnet.py
"""
from collections import OrderedDict
import math

import torch.nn as nn
from torch.utils import model_zoo

class SEModule(nn.Module):

    def __init__(self, channels, reduction):
        super(SEModule, self).__init__()
        self.avg_pool = nn.AdaptiveAvgPool2d(1)
        self.fc1 = nn.Conv2d(channels, channels // reduction, kernel_size=1,
                             padding=0)
        self.relu = nn.ReLU(inplace=True)
        self.fc2 = nn.Conv2d(channels // reduction, channels, kernel_size=1,
                             padding=0)
        self.sigmoid = nn.Sigmoid()

    def forward(self, x):
        module_input = x
        x = self.avg_pool(x)
        x = self.fc1(x)
        x = self.relu(x)
        x = self.fc2(x)
        x = self.sigmoid(x)
        return module_input * x


class Bottleneck(nn.Module):
    """
    Base class for bottlenecks that implements `forward()` method.
    """
    def forward(self, x):
        residual = x

        out = self.conv1(x)
        out = self.bn1(out)
        out = self.relu(out)

        out = self.conv2(out)
        out = self.bn2(out)
        out = self.relu(out)

        out = self.conv3(out)
        out = self.bn3(out)

        if self.downsample is not None:
            residual = self.downsample(x)

        out = self.se_module(out) + residual
        out = self.relu(out)
        return out


class SEBottleneck(Bottleneck):
    """
    Bottleneck for SENet154.
    """
    expansion = 4
    def __init__(self, inplanes, planes, groups, reduction, stride=1,
                 downsample=None):
        super(SEBottleneck, self).__init__()
        self.conv1 = nn.Conv2d(inplanes, planes * 2, kernel_size=1, bias=False)
        self.bn1 = nn.BatchNorm2d(planes * 2)
        self.conv2 = nn.Conv2d(planes * 2, planes * 4, kernel_size=3,
                               stride=stride, padding=1, groups=groups,
                               bias=False)
        self.bn2 = nn.BatchNorm2d(planes * 4)
        self.conv3 = nn.Conv2d(planes * 4, planes * 4, kernel_size=1,
                               bias=False)
        self.bn3 = nn.BatchNorm2d(planes * 4)
        self.relu = nn.ReLU(inplace=True)
        self.se_module = SEModule(planes * 4, reduction=reduction)
        self.downsample = downsample
        self.stride = stride


# class SEResNetBottleneck(Bottleneck):
#     """
#     ResNet bottleneck with a Squeeze-and-Excitation module. It follows Caffe
#     implementation and uses `stride=stride` in `conv1` and not in `conv2`
#     (the latter is used in the torchvision implementation of ResNet).
#     """
#     expansion = 4
#
#     def __init__(self, inplanes, planes, groups, reduction, stride=1,
#                  downsample=None):
#         super(SEResNetBottleneck, self).__init__()
#         self.conv1 = nn.Conv2d(inplanes, planes, kernel_size=1, bias=False,
#                                stride=stride)
#         self.bn1 = nn.BatchNorm2d(planes)
#         self.conv2 = nn.Conv2d(planes, planes, kernel_size=3, padding=1,
#                                groups=groups, bias=False)
#         self.bn2 = nn.BatchNorm2d(planes)
#         self.conv3 = nn.Conv2d(planes, planes * 4, kernel_size=1, bias=False)
#         self.bn3 = nn.BatchNorm2d(planes * 4)
#         self.relu = nn.ReLU(inplace=True)
#         self.se_module = SEModule(planes * 4, reduction=reduction)
#         self.downsample = downsample
#         self.stride = stride


class SEResNeXtBottleneck(Bottleneck):
    """
    ResNeXt bottleneck type C with a Squeeze-and-Excitation module.
    """
    expansion = 4

    def __init__(self, inplanes, planes, groups, reduction, stride=1,
                 downsample=None, base_width=4):
        super(SEResNeXtBottleneck, self).__init__()
        width = int(math.floor(planes * (base_width / 64)) * groups)


        self.conv1 = nn.Conv2d(inplanes, width, kernel_size=1, stride=1, bias=False)
        self.bn1 = nn.BatchNorm2d(width)
        self.conv2 = nn.Conv2d(width, width, kernel_size=3, stride=stride,
                               padding=1, groups=groups, bias=False)
        self.bn2 = nn.BatchNorm2d(width)
        self.conv3 = nn.Conv2d(width, planes * 4, kernel_size=1, bias=False)
        self.bn3 = nn.BatchNorm2d(planes * 4)
        self.relu = nn.ReLU(inplace=True)
        self.se_module = SEModule(planes * 4, reduction=reduction)
        self.downsample = downsample
        self.stride = stride


class SENet(nn.Module):

    def __init__(self, block, layers, groups, reduction, dropout_p=0.2,
                 inplanes=128, input_3x3=True, downsample_kernel_size=3,
                 downsample_padding=1, num_classes=1000):
        """
        Parameters
        ----------
        block (nn.Module): Bottleneck class.
            - For SENet154: SEBottleneck
            - For SE-ResNet models: SEResNetBottleneck
            - For SE-ResNeXt models:  SEResNeXtBottleneck
        layers (list of ints): Number of residual blocks for 4 layers of the
            network (layer1...layer4).
        groups (int): Number of groups for the 3x3 convolution in each
            bottleneck block.
            - For SENet154: 64
            - For SE-ResNet models: 1
            - For SE-ResNeXt models:  32
        reduction (int): Reduction ratio for Squeeze-and-Excitation modules.
            - For all models: 16
        dropout_p (float or None): Drop probability for the Dropout layer.
            If `None` the Dropout layer is not used.
            - For SENet154: 0.2
            - For SE-ResNet models: None
            - For SE-ResNeXt models: None
        inplanes (int):  Number of input channels for layer1.
            - For SENet154: 128
            - For SE-ResNet models: 64
            - For SE-ResNeXt models: 64
        input_3x3 (bool): If `True`, use three 3x3 convolutions instead of
            a single 7x7 convolution in layer0.
            - For SENet154: True
            - For SE-ResNet models: False
            - For SE-ResNeXt models: False
        downsample_kernel_size (int): Kernel size for downsampling convolutions
            in layer2, layer3 and layer4.
            - For SENet154: 3
            - For SE-ResNet models: 1
            - For SE-ResNeXt models: 1
        downsample_padding (int): Padding for downsampling convolutions in
            layer2, layer3 and layer4.
            - For SENet154: 1
            - For SE-ResNet models: 0
            - For SE-ResNeXt models: 0
        num_classes (int): Number of outputs in `last_linear` layer.
            - For all models: 1000
        """
        super(SENet, self).__init__()
        self.inplanes = inplanes
        if input_3x3:
            layer0_modules = [
                ('conv1', nn.Conv2d(3, 64, 3, stride=2, padding=1,
                                    bias=False)),
                ('bn1', nn.BatchNorm2d(64)),
                ('relu1', nn.ReLU(inplace=True)),
                ('conv2', nn.Conv2d(64, 64, 3, stride=1, padding=1,
                                    bias=False)),
                ('bn2', nn.BatchNorm2d(64)),
                ('relu2', nn.ReLU(inplace=True)),
                ('conv3', nn.Conv2d(64, inplanes, 3, stride=1, padding=1,
                                    bias=False)),
                ('bn3', nn.BatchNorm2d(inplanes)),
                ('relu3', nn.ReLU(inplace=True)),
            ]
        else:
            layer0_modules = [
                ('conv1', nn.Conv2d(3, inplanes, kernel_size=7, stride=2,
                                    padding=3, bias=False)),
                ('bn1', nn.BatchNorm2d(inplanes)),
                ('relu1', nn.ReLU(inplace=True)),
            ]

        layer0_modules.append(('pool', nn.MaxPool2d(3, stride=2,ceil_mode=True)))

        self.layer0 = nn.Sequential(OrderedDict(layer0_modules))
        self.layer1 = self._make_layer(
            block,
            planes=64,
            blocks=layers[0],
            groups=groups,
            reduction=reduction,
            downsample_kernel_size=1,
            downsample_padding=0
        )
        self.layer2 = self._make_layer(
            block,
            planes=128,
            blocks=layers[1],
            stride=2,
            groups=groups,
            reduction=reduction,
            downsample_kernel_size=downsample_kernel_size,
            downsample_padding=downsample_padding
        )
        self.layer3 = self._make_layer(
            block,
            planes=256,
            blocks=layers[2],
            stride=2,
            groups=groups,
            reduction=reduction,
            downsample_kernel_size=downsample_kernel_size,
            downsample_padding=downsample_padding
        )
        self.layer4 = self._make_layer(
            block,
            planes=512,
            blocks=layers[3],
            stride=2,
            groups=groups,
            reduction=reduction,
            downsample_kernel_size=downsample_kernel_size,
            downsample_padding=downsample_padding
        )
        self.avg_pool = nn.AvgPool2d(7, stride=1)
        self.dropout = nn.Dropout(dropout_p) if dropout_p is not None else None
        self.last_linear = nn.Linear(512 * block.expansion, num_classes)

    def _make_layer(self, block, planes, blocks, groups, reduction, stride=1,
                    downsample_kernel_size=1, downsample_padding=0):
        downsample = None
        if stride != 1 or self.inplanes != planes * block.expansion:
            downsample = nn.Sequential(
                nn.Conv2d(self.inplanes, planes * block.expansion,
                          kernel_size=downsample_kernel_size, stride=stride,
                          padding=downsample_padding, bias=False),
                nn.BatchNorm2d(planes * block.expansion),
            )

        layers = []
        layers.append(block(self.inplanes, planes, groups, reduction, stride,
                            downsample))
        self.inplanes = planes * block.expansion
        for i in range(1, blocks):
            layers.append(block(self.inplanes, planes, groups, reduction))

        return nn.Sequential(*layers)

    def features(self, x):
        x = self.layer0(x)
        x = self.layer1(x)
        x = self.layer2(x)
        x = self.layer3(x)
        x = self.layer4(x)
        return x

    def logits(self, x):
        x = self.avg_pool(x)
        if self.dropout is not None:
            x = self.dropout(x)
        x = x.view(x.size(0), -1)
        x = self.last_linear(x)
        return x

    def forward(self, x):
        x = self.features(x)
        x = self.logits(x)
        return x


def FaceBagNet_model_A(num_classes=2):
    model = SENet(SEResNeXtBottleneck, [2, 2, 2, 2], groups=32, reduction=16,
                  dropout_p=None, inplanes=64, input_3x3=False,
                  downsample_kernel_size=1, downsample_padding=0,
                  num_classes=num_classes)
    return model

def FaceBagNet_model_B(num_classes=2):
    model = SENet(SEResNeXtBottleneck, [2, 4, 4, 2], groups=32, reduction=16,
                  dropout_p=None, inplanes=64, input_3x3=False,
                  downsample_kernel_size=1, downsample_padding=0,
                  num_classes=num_classes)
    return model

def FaceBagNet_model_C(num_classes=2):
    model = SENet(SEResNeXtBottleneck, [3, 4, 4, 3], groups=16, reduction=16,
                  dropout_p=None, inplanes=64, input_3x3=False,
                  downsample_kernel_size=1, downsample_padding=0,
                  num_classes=num_classes)
    return model
#from utils import *
import torchvision.models as tvm
import torch.nn as nn
import torch
import torch.nn.functional as F
import numpy as np
#from FaceBagNet import FaceBagNet_model_A
BatchNorm2d = nn.BatchNorm2d

###########################################################################################3
class Net(nn.Module):
    def load_pretrain(self, pretrain_file):
        pretrain_state_dict = torch.load(pretrain_file)
        state_dict = self.state_dict()

        keys = list(state_dict.keys())
        for key in keys:
            state_dict[key] = pretrain_state_dict['module.'+key]

        self.load_state_dict(state_dict)
        print('load: '+pretrain_file)

    def __init__(self, num_class=2, id_class = 300, is_first_bn = False):
        super(Net,self).__init__()

        self.is_first_bn = is_first_bn
        if self.is_first_bn:
            self.first_bn = nn.BatchNorm2d(3)

        self.encoder  = FaceBagNet_model_A(num_classes=1000)
        self.conv1 = self.encoder.layer0
        self.conv2 = self.encoder.layer1
        self.conv3 = self.encoder.layer2
        self.conv4 = self.encoder.layer3
        self.conv5 = self.encoder.layer4

        self.fc = nn.Sequential(nn.Linear(2048, num_class))
        self.id_fc = nn.Sequential(nn.Linear(2048, id_class))

    def forward(self, x):
        batch_size,C,H,W = x.shape

        if self.is_first_bn:
            x = self.first_bn(x)
        else:
            mean=[0.485, 0.456, 0.406] #rgb
            std =[0.229, 0.224, 0.225]

            x = torch.cat([
                (x[:,[0]]-mean[0])/std[0],
                (x[:,[1]]-mean[1])/std[1],
                (x[:,[2]]-mean[2])/std[2],
            ],1)

        x = self.conv1(x) #; print('e1',x.size())
        x = self.conv2(x) #; print('e2',x.size())
        x = self.conv3(x) #; print('e3',x.size())
        x = self.conv4(x) #; print('e4',x.size())
        x = self.conv5(x) #; print('e5',x.size())

        fea = F.adaptive_avg_pool2d(x, output_size=1).view(batch_size,-1)
        fea = F.dropout(fea, p=0.50, training=self.training)
        logit = self.fc(fea)
        logit_id = self.id_fc(fea)

        return logit, logit_id, fea

    def forward_res3(self, x):
        batch_size,C,H,W = x.shape

        if self.is_first_bn:
            x = self.first_bn(x)
        else:
            mean=[0.485, 0.456, 0.406] #rgb
            std =[0.229, 0.224, 0.225]

            x = torch.cat([
                (x[:,[0]]-mean[0])/std[0],
                (x[:,[1]]-mean[1])/std[1],
                (x[:,[2]]-mean[2])/std[2],
            ],1)

        x = self.conv1(x) #; print('e1',x.size())
        x = self.conv2(x) #; print('e2',x.size())
        x = self.conv3(x) #; print('e3',x.size())

        return x

    def set_mode(self, mode, is_freeze_bn=False ):
        self.mode = mode
        if mode in ['eval', 'valid', 'test']:
            self.eval()
        elif mode in ['backup']:
            self.train()
            if is_freeze_bn==True: ##freeze
                for m in self.modules():
                    if isinstance(m, BatchNorm2d):
                        m.eval()
                        m.weight.requires_grad = False
                        m.bias.requires_grad   = False


### 
def TTA_36_cropps(image, target_shape=(32, 32, 3)):
    image = cv2.resize(image, (RESIZE_SIZE, RESIZE_SIZE))

    width, height, d = image.shape
    target_w, target_h, d = target_shape

    start_x = ( width - target_w) // 2
    start_y = ( height - target_h) // 2

    starts = [[start_x, start_y],

              [start_x - target_w, start_y],
              [start_x, start_y - target_w],
              [start_x + target_w, start_y],
              [start_x, start_y + target_w],

              [start_x + target_w, start_y + target_w],
              [start_x - target_w, start_y - target_w],
              [start_x - target_w, start_y + target_w],
              [start_x + target_w, start_y - target_w],
              ]

    images = []

    for start_index in starts:
        image_ = image.copy()
        x, y = start_index

        if x < 0:
            x = 0
        if y < 0:
            y = 0

        if x + target_w >= RESIZE_SIZE:
            x = RESIZE_SIZE - target_w-1
        if y + target_h >= RESIZE_SIZE:
            y = RESIZE_SIZE - target_h-1

        zeros = image_[x:x + target_w, y: y+target_h, :]

        image_ = zeros.copy()

        zeros = np.fliplr(zeros)
        image_flip_lr = zeros.copy()

        zeros = np.flipud(zeros)
        image_flip_lr_up = zeros.copy()

        zeros = np.fliplr(zeros)
        image_flip_up = zeros.copy()

        images.append(image_.reshape([1,target_shape[0],target_shape[1],target_shape[2]]))
        images.append(image_flip_lr.reshape([1,target_shape[0],target_shape[1],target_shape[2]]))
        images.append(image_flip_up.reshape([1,target_shape[0],target_shape[1],target_shape[2]]))
        images.append(image_flip_lr_up.reshape([1,target_shape[0],target_shape[1],target_shape[2]]))

    return images
class FaceAnti:
    def __init__(self,model_path):
        #from FaceBagNet_model_A import Net
        self.net = Net(num_class=2,is_first_bn=True)
        #model_path = os.path.join(pwd, 'models', 'model_A_color_64', 'checkpoint', 'global_min_acer_model.pth')
        #model_path = "./global_min_acer_model.pth"
        if torch.cuda.is_available():
            state_dict = torch.load(model_path, map_location='cuda')
        else:
            state_dict = torch.load(model_path, map_location='cpu')
        new_state_dict = OrderedDict()
        for k, v in state_dict.items():
            name = k[7:] # remove `module.`
            new_state_dict[name] = v
        self.net.load_state_dict(new_state_dict)
        #self.net.load_state_dict(state_dict)
        if torch.cuda.is_available():
            self.net = self.net.cuda()
        self.net.eval()

    def classify(self,color):
        return self.detect(color)
    def detect(self,color):
        #color = cv2.imread(imgpath,1)
        color = cv2.resize(color,(RESIZE_SIZE,RESIZE_SIZE))
        
        def color_augumentor(image, target_shape=(64, 64, 3), is_infer=False):
            if is_infer:
                augment_img = iaa.Sequential([
                    iaa.Fliplr(0),
                ])
            image =  augment_img.augment_image(image)
            image = TTA_36_cropps(image, target_shape)
            return image

        color = color_augumentor(color, target_shape=(64, 64, 3), is_infer=True)
        #import pdb
        #pdb.set_trace()
        n = len(color)
        color = np.concatenate(color, axis=0)

        image = color
        image = np.transpose(image, (0, 3, 1, 2))
        image = image.astype(np.float32)
        image = image / 255.0
        input_image = torch.FloatTensor(image)
        if (len(input_image.size())==4) and torch.cuda.is_available():
            input_image = input_image.unsqueeze(0).cuda()
        elif (len(input_image.size())==4) and not torch.cuda.is_available():
            input_image = input_image.unsqueeze(0)
        
        b, n, c, w, h = input_image.size()
        input_image = input_image.view(b*n, c, w, h)
        if torch.cuda.is_available():
            input_image = input_image.cuda()

    
        with torch.no_grad():
            logit,_,_   = self.net(input_image)
            logit = logit.view(b,n,2)
            logit = torch.mean(logit, dim = 1, keepdim = False)
            prob = F.softmax(logit, 1)

        print('probabilistic：', prob)
        print('predict: ', np.argmax(prob.detach().cpu().numpy()))
        return np.argmax(prob.detach().cpu().numpy())
     
#Val/0000/000037-color.jpg Val/0000/000037-depth.jpg Val/0000/000037-ir.jpg 1
#Val/0000/000038-color.jpg Val/0000/000038-depth.jpg Val/0000/000038-ir.jpg 0
#Val/0000/000039-color.jpg Val/0000/000039-depth.jpg Val/0000/000039-ir.jpg 0
#Val/0000/000040-color.jpg Val/0000/000040-depth.jpg Val/0000/000040-ir.jpg 0
#Val/0000/000041-color.jpg Val/0000/000041-depth.jpg Val/0000/000041-ir.jpg 0
#Val/0000/000042-color.jpg Val/0000/000042-depth.jpg Val/0000/000042-ir.jpg 1
#Val/0000/000043-color.jpg Val/0000/000043-depth.jpg Val/0000/000043-ir.jpg 1
#Val/0000/000044-color.jpg Val/0000/000044-depth.jpg Val/0000/000044-ir.jpg 0
if __name__=="__main__":        
        
    FA = FaceAnti("./global_min_acer_model.pth")
    img = cv2.imread('upload.jpg',1)
    FA.detect(img)
    #FA.detect('./CASIA-SURF/Val/0000/000037-color.jpg')
    #FA.detect('./CASIA-SURF/Val/0000/000038-color.jpg')
    #FA.detect('./CASIA-SURF/Val/0000/000039-color.jpg')
    #FA.detect('./CASIA-SURF/Val/0000/000040-color.jpg')
    #FA.detect('./CASIA-SURF/Val/0000/000041-color.jpg')
    #FA.detect('./CASIA-SURF/Val/0000/000042-color.jpg')
