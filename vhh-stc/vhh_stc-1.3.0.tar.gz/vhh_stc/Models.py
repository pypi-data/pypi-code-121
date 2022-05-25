import torch
import torchvision.transforms as transforms
import matplotlib.pyplot as plt
import numpy as np
import torch.nn.functional as F
import torch.optim as optim
from torch.utils import data
import h5py as hf
from PIL import Image
from torchvision import datasets
from torch.utils.data import DataLoader
from torchvision import models


def loadModel(model_arch="", classes=None, pre_trained_path=None):
    """
    This module is used to load specified deep learning model.

    :param model_arch: string value [required] - is used to select between various deep learning architectures
     (Resnet, Vgg, Densenet, Alexnet)
    :param classes: list of strings [required] - is used to hold the class names (e.g. ['ELS', 'LS', 'MS', 'CU'])
    :param pre_trained_path: string [optional] - is used to specify the path to a pre-trained model
    :return: the specified instance of the model
    """

    print("Load model architecture ... ")
    if (model_arch == "resnet50"):
        print("Resnet architecture selected ...")

        model = models.resnet50(pretrained=True)

        for params in model.parameters():
            params.requires_grad = True

        num_ftrs = model.fc.in_features
        model.fc = torch.nn.Linear(num_ftrs, len(classes))

        # Find total parameters and trainable parameters
        total_params = sum(p.numel() for p in model.parameters())
        print("total_params:" + str(total_params))
        total_trainable_params = sum(
            p.numel() for p in model.parameters() if p.requires_grad)
        print("total_trainable_params: " + str(total_trainable_params))

        if (pre_trained_path != None):
            print("load pre_trained weights ... ")
            model_dict_state = torch.load(pre_trained_path)
            model.load_state_dict(model_dict_state['net']) #, strict=False

    elif (model_arch == "resnet18"):
        print("Resnet architecture selected ...")

        model = models.resnet18(pretrained=True)

        for params in model.parameters():
            params.requires_grad = True

        num_ftrs = model.fc.in_features
        model.fc = torch.nn.Linear(num_ftrs, len(classes))

        # Find total parameters and trainable parameters
        total_params = sum(p.numel() for p in model.parameters())
        print("total_params:" + str(total_params))
        total_trainable_params = sum(
            p.numel() for p in model.parameters() if p.requires_grad)
        print("total_trainable_params: " + str(total_trainable_params))

        if (pre_trained_path != None):
            print("load pre_trained weights ... ")
            model_dict_state = torch.load(pre_trained_path)
            model.load_state_dict(model_dict_state['net']) #, strict=False

    elif (model_arch == "resnet152"):
        print("Resnet architecture selected ...")

        model = models.resnet152(pretrained=True)

        for params in model.parameters():
            params.requires_grad = True

        num_ftrs = model.fc.in_features
        model.fc = torch.nn.Linear(num_ftrs, len(classes))

        # Find total parameters and trainable parameters
        total_params = sum(p.numel() for p in model.parameters())
        print("total_params:" + str(total_params))
        total_trainable_params = sum(
            p.numel() for p in model.parameters() if p.requires_grad)
        print("total_trainable_params: " + str(total_trainable_params))

        if (pre_trained_path != None):
            print("load pre_trained weights ... ")
            model_dict_state = torch.load(pre_trained_path)
            model.load_state_dict(model_dict_state['net']) #, strict=False

    elif (model_arch == "vgg16"):
        print("Vgg architecture selected ...")

        model = models.vgg16(pretrained=True)
        # print(model)

        for params in model.parameters():
            params.requires_grad = True

        layers = model.children()
        print("number of layers: " + str(type(layers)))

        for params in model.parameters():
            params.requires_grad = True

        model.classifier[-1] = torch.nn.Linear(4096, len(classes))
        # print(model)
        # exit()
        # Find total parameters and trainable parameters
        total_params = sum(p.numel() for p in model.parameters())
        print("total_params:" + str(total_params))
        total_trainable_params = sum(
            p.numel() for p in model.parameters() if p.requires_grad)
        print("total_trainable_params: " + str(total_trainable_params))

        if (pre_trained_path != None):
            print("load pre_trained weights ... ")
            model_dict_state = torch.load(pre_trained_path)
            model.load_state_dict(model_dict_state['net']) #, strict=False

    elif (model_arch == "densenet121"):
        print("Densenet architecture selected ...")

        model = models.densenet121(pretrained=True)
        # print(model)

        for params in model.parameters():
            params.requires_grad = True

        num_ftrs = model.classifier.in_features
        model.classifier = torch.nn.Linear(num_ftrs, len(classes))
        # print(model)

        # Find total parameters and trainable parameters
        total_params = sum(p.numel() for p in model.parameters())
        print("total_params:" + str(total_params))
        total_trainable_params = sum(
            p.numel() for p in model.parameters() if p.requires_grad)
        print("total_trainable_params: " + str(total_trainable_params))

        if (pre_trained_path != None):
            print("load pre_trained weights ... ")
            model_dict_state = torch.load(pre_trained_path)
            model.load_state_dict(model_dict_state['net']) #, strict=False
    else:
        model = None
        print("ERROR: select valid model architecture!")
        exit()

    return model
