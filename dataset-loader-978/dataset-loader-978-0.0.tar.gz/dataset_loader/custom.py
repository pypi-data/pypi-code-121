import os
from dataset_loader import imagenet as IMNET
import torch
from PIL import Image
import torchvision.transforms as transforms
import torchvision.transforms.functional as F


class Custom(IMNET):

    def __init__(self,p='imgs/',base=0,window=1):
        # super().__init__()
        self.p,self.base,self.window=p,base,window

        self.name='imagenet'
        self.means, self.stds = [0.485, 0.456, 0.406], [0.229, 0.224, 0.225]
        self.img_list = {k: v for k, v in enumerate(sorted(os.listdir(p))[base:base + window])}

        self.GT,self.labs=[0],[0]

        self.p = p
        self.__dict__.update(locals())
