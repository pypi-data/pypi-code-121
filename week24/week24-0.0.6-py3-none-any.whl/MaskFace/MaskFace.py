#coding:utf-8
# 路径置顶
import sys
import os
os.environ["CUDA_VISIBLE_DEVICES"] = "0"
from torch.nn.modules.distance import PairwiseDistance
import torch.nn as nn
import numpy as np
import torch
import time
import torchvision.models as models
import torchvision.transforms as transforms
from PIL import Image

def transform_image(image_bytes):
    my_transforms = transforms.Compose([transforms.Resize([255,255]),
                                        transforms.ToTensor(),
                                        transforms.Normalize(
                                        mean=[0.5, 0.5, 0.5],
                                        std=[0.5, 0.5, 0.5])])
    #image = Image.open(io.BytesIO(image_bytes))
    image = image_bytes;
    return my_transforms(image).unsqueeze(0)

def transform_image_bytes(image_bytes):
    my_transforms = transforms.Compose([transforms.Resize([255,255]),
                                        transforms.ToTensor(),
                                        transforms.Normalize(
                                        mean=[0.5, 0.5, 0.5],
                                        std=[0.5, 0.5, 0.5])])
    image = Image.open(io.BytesIO(image_bytes))
    return my_transforms(image).unsqueeze(0)


class Resnet18Triplet(nn.Module):
    """Constructs a ResNet-18 model for FaceNet training using triplet loss.

    Args:
        embedding_dimension (int): Required dimension of the resulting embedding layer that is outputted by the model.
                                   using triplet loss. Defaults to 128.
        pretrained (bool): If True, returns a model pre-trained on the ImageNet dataset from a PyTorch repository.
                           Defaults to False.
    """

    def __init__(self, embedding_dimension=128, pretrained=False):
        super(Resnet18Triplet, self).__init__()
        self.model = models.resnet18(pretrained=pretrained)
        input_features_fc_layer = self.model.fc.in_features
        # Output embedding
        self.model.fc = nn.Linear(input_features_fc_layer, embedding_dimension)

    def l2_norm(self, input):
        """Perform l2 normalization operation on an input vector.
        code copied from liorshk's repository: https://github.com/liorshk/facenet_pytorch/blob/master/model.py
        """
        input_size = input.size()
        buffer = torch.pow(input, 2)
        normp = torch.sum(buffer, 1).add_(1e-10)
        norm = torch.sqrt(normp)
        _output = torch.div(input, norm.view(-1, 1).expand_as(input))
        output = _output.view(input_size)

        return output

    def forward(self, images):
        """Forward pass to output the embedding vector (feature vector) after l2-normalization and multiplication
        by scalar (alpha)."""
        embedding = self.model(images)
        embedding = self.l2_norm(embedding)
        # Multiply by alpha = 10 as suggested in https://arxiv.org/pdf/1703.09507.pdf
        #   Equation 9: number of classes in VGGFace2 dataset = 9131
        #   lower bound on alpha = 5, multiply alpha by 2; alpha = 10
        alpha = 10
        embedding = embedding * alpha

        return embedding

class MaskFace():
    def __init__(self,model_path):
        self.model = Resnet18Triplet(pretrained=False,embedding_dimension = 128)
        if torch.cuda.is_available():
            self.model.cuda()
            print('Using single-gpu evaluate.')
        #state=torch.load("model_resnet18_triplet_epoch_586.pt")
        state=torch.load(model_path)
        self.model.load_state_dict(state['model_state_dict'])
        self.model.eval()

    def get_faceid_from_byte(self,image_bytes):
        img = transform_image_bytes(image_bytes)
        embedding = self.model(img)
        return embedding

    def get_faceid_from_file(self,image_file):
        #img=Image.open('upload.jpg')
        img=Image.open(image_file)
        img = transform_image(img)
        embedding = self.model(img)
        return embedding
