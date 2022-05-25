import os
import random
from typing import OrderedDict

import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import Dataset, DataLoader

from torchvision import datasets
from torchvision.transforms import transforms

from torchinfo import summary

from skimage import io, color
from skimage.transform import resize

import matplotlib.pyplot as plt

class _DenseLayer(nn.Module):
    def __init__(self, in_channels, growth_rate, bn_size):
        super(_DenseLayer, self).__init__()
        self.add_module('norm1', nn.BatchNorm2d(in_channels))
        self.add_module('relu1', nn.ReLU(inplace=True))
        self.add_module('conv1', nn.Conv2d(in_channels=in_channels, out_channels=bn_size * growth_rate, 
                                           kernel_size=1, stride=1, bias=False))
        self.add_module('norm2', nn.BatchNorm2d(bn_size * growth_rate))
        self.add_module('relu2', nn.ReLU(inplace=True))
        self.add_module('conv2', nn.Conv2d(in_channels=bn_size * growth_rate, out_channels=growth_rate, 
                                           kernel_size=3, stride=1, padding=1, bias=False))
    
    def bn_function(self, inputs):
        concated_layers = torch.cat(inputs, 1)
        bottleneck_output = self.conv1(self.relu1(self.norm1(concated_layers)))
        return bottleneck_output

    def forward(self, input):
        if isinstance(input, torch.Tensor):
            prev_layers = [input]
        else:
            prev_layers = input
        
        bottleneck_output = self.bn_function(prev_layers)
        new_features = self.conv2(self.relu2(self.norm2(bottleneck_output)))

        return new_features

class _DenseBlock(nn.ModuleDict):
    def __init__(self, num_layers, in_channels, growth_rate, bn_size):
        super(_DenseBlock, self).__init__()
        for i in range(num_layers):
            layer = _DenseLayer(
                in_channels=in_channels + i * growth_rate,
                growth_rate=growth_rate,
                bn_size=bn_size,
            )
            self.add_module('denselayer{}'.format(i), layer)

    def forward(self, init_features):
        features = [init_features]
        for name, layer in self.items():
            new_features = layer(features)
            features.append(new_features)
        return torch.cat(features, 1)

class _DownTransition(nn.Sequential):
    def __init__(self, in_channels, out_channels):
        super(_DownTransition, self).__init__()
        self.add_module('norm', nn.BatchNorm2d(in_channels))
        self.add_module('relu', nn.ReLU(inplace=True))
        self.add_module('conv', nn.Conv2d(in_channels=in_channels, out_channels=out_channels, 
                                          kernel_size=2, stride=2, bias=False))

class _UpTransition(nn.Sequential):
    def __init__(self, in_channels, out_channels):
        super(_UpTransition, self).__init__()
        self.add_module('norm', nn.BatchNorm2d(in_channels))
        self.add_module('relu', nn.ReLU(inplace=True))
        self.add_module('convT', nn.ConvTranspose2d(in_channels=in_channels, out_channels=out_channels, 
                                                    kernel_size=2, stride=2, bias=False))

class _ResImageNet(nn.Module):
    def __init__(self, growth_rate=4, block_config=(4, 4, 4, 4),
                 num_init_features=8, bn_size=4):
        super(_ResImageNet, self).__init__()

        if len(block_config) % 2:
            print("ERROR: len(block_config) is not a multiple of 2")
            return

        self.features = nn.Sequential(OrderedDict([
            ('conv0', nn.Conv2d(in_channels=3, out_channels=num_init_features, 
                                kernel_size=7, padding=3, bias=False)),
            ('norm0', nn.BatchNorm2d(num_init_features)),
            ('relu', nn.ReLU(inplace=True)),
        ]))

        num_features = num_init_features
        for i, num_layers in enumerate(block_config):
            block = _DenseBlock(
                num_layers=num_layers,
                in_channels=num_features,
                growth_rate=growth_rate,
                bn_size=bn_size,
            )
            self.features.add_module('denseblock{}'.format(i), block)
            num_features += num_layers * growth_rate
            if i <= len(block_config) // 2 - 1:
                trans = _DownTransition(in_channels=num_features,
                                        out_channels=num_features // 2)
            else:
                trans = _UpTransition(in_channels=num_features,
                                        out_channels=num_features // 2)
            self.features.add_module('transition{}'.format(i + 1), trans)
            num_features = num_features // 2
        
        self.features.add_module('norm', nn.BatchNorm2d(num_features))
        self.features.add_module('conv3x3', nn.Conv2d(in_channels=num_features, out_channels=3, 
                                                    kernel_size=3, stride=1, padding=1, bias=False))
        self.features.add_module('sigm', nn.Sigmoid())
        # Init weights before start learning
        for m in self.modules():
            if isinstance(m, nn.Conv2d):
                nn.init.kaiming_normal_(m.weight)
            elif isinstance(m, nn.BatchNorm2d):
                nn.init.constant_(m.weight, 1)
                nn.init.constant_(m.bias, 0)
            elif isinstance(m, nn.ConvTranspose2d):
                nn.init.kaiming_normal_(m.weight)
    
    def forward(self, x):
        out = self.features(x)
        return out

class ResImageDataset(Dataset):
    def __init__(self, dir_name, transform=None):
        self.dir_name = dir_name
        self.raw = sorted(os.listdir(os.path.join(dir_name, "raw")), key=lambda f: int("".join(filter(str.isdigit, f))))
        self.inpainted = sorted(os.listdir(os.path.join(dir_name, "inpainted")), key=lambda f: int("".join(filter(str.isdigit, f))))
        self.transform = transform
    
    def __len__(self):
        return len(self.raw)

    def imageTransform(self, raw_image, inpainted_image):
        # Gray to RGB conversion
        if len(raw_image.shape) < 3:
            raw_image = color.gray2rgb(raw_image)
        if len(inpainted_image.shape) < 3:
            inpainted_image = color.gray2rgb(inpainted_image)
        # RGBA to RGB conversion
        if raw_image.shape[2] > 3:
            raw_image = color.rgba2rgb(raw_image)
        if inpainted_image.shape[2] > 3:
            inpainted_image = color.rgba2rgb(inpainted_image)

        if raw_image.shape != inpainted_image.shape:
            print("Image size problem (raw shape {} and inpainted {}): resizing raw to inpainted".format(raw_image.shape, inpainted_image.shape))
            raw_image = resize(raw_image, (inpainted_image.shape[0], inpainted_image.shape[1]))
        
        # Resize to closest 4*N
        w = inpainted_image.shape[0]
        w = (w // 4) * 4
        h = inpainted_image.shape[1]
        h = (h // 4) * 4
        raw_image = resize(raw_image, (w, h))
        inpainted_image = resize(inpainted_image, (w, h))
        return raw_image, inpainted_image

    def __getitem__(self, index):
        if torch.is_tensor(index):
            index = index.tolist()
        
        raw_image = io.imread(os.path.join(self.dir_name, "raw", self.raw[index]))
        inpainted_image = io.imread(os.path.join(self.dir_name, "inpainted", self.inpainted[index]))

        raw_image, inpainted_image = self.imageTransform(raw_image, inpainted_image)

        sample = None
        if self.transform:
            sample = {"raw": self.transform(raw_image),
                      "inpainted": self.transform(inpainted_image)}
        else:
            sample = {"raw": raw_image,
                      "inpainted": inpainted_image}

        return sample

class ResImageNet():
    def __init__(self, device=None, try_to_train=False, image_dir=None,
                 epochs=100, lr=1e-3, batch_size=1,
                 growth_rate=4, block_config=(4, 4, 4, 4), num_init_features=8, bn_size=4):
        self.device = device
        self.image_dir = image_dir
        # Choose appropriate device
        if self.device == None:
            print("None device is given. Trying to use cuda...")
            if torch.cuda.is_available():
                print("Cuda is available. device = cuda.")
                self.device = torch.device('cuda')
            else:
                print("Cuda isn't available. device = cpu.")
                self.device = torch.device('cpu')
        # Create model of ResImageNet
        self.model = _ResImageNet(
            growth_rate = growth_rate,
            block_config = block_config,
            num_init_features = num_init_features,
            bn_size = bn_size,
        )
        if os.path.isfile("ResImageNet.pth"):
            print("File with model 'ResImageNet.pth' found...")
            try:
                self.model = torch.load('ResImageNet.pth', map_location=self.device)
                print("Model successfully loaded.")
            except Exception as ex:
                print(ex)
                return
        else:
            if try_to_train:
                if image_dir == None:
                    print("Error: image_dir isn't set")
                    return
                else:
                    try:
                        self.model.to(self.device)
                        self.__train(image_dir, epochs, lr, batch_size)
                    except Exception as ex:
                        print(ex)
                        return
            else:
                print("File with model 'ResImageNet.pth' not found and try_to_train is False. If you want to train model, set try_to_train to True.")
                return

    def __call__(self, img_input):
        shape = img_input.shape
        img_input = img_input.view(1, shape[0], shape[1], shape[2]).to(self.device, dtype = torch.float)
        img_output = self.model(img_input)
        img_output = img_output.cpu().detach()

        return img_output

    def __train(self, image_dir, epochs, lr, batch_size):
        # Loss function is BCE
        loss = nn.BCELoss()
        # Optimazer for model is Adam
        optimizer = optim.Adam(self.model.parameters(), lr=lr)
        # Create transform to torch.Tensor
        transform = transforms.Compose([transforms.ToTensor()])
        # Use ResImageDataset for auto image pack to samples
        train_set = ResImageDataset(image_dir, transform=transform)
        train_loader = DataLoader(train_set, batch_size=batch_size, shuffle=True)

        # Begin of train
        print("Start train net:")
        for epoch in range(1, epochs + 1):
            # Monitor training loss
            train_loss = 0.0

            for i, sample in enumerate(train_loader):
                print("Epoch {}. Processing image {}".format(epoch, i), end='.')
                raw = sample["raw"]
                shape = raw.shape
                raw = raw.view(1, shape[1], shape[2], shape[3]).to(self.device, dtype = torch.float)
                inpainted = sample["inpainted"]
                shape = inpainted.shape
                inpainted = inpainted.view(1, shape[1], shape[2], shape[3]).to(self.device, dtype = torch.float)
                optimizer.zero_grad()
                outputs = self.model(raw)
                cur_loss = loss(outputs, inpainted)
                cur_loss.backward()
                optimizer.step()
                train_loss += cur_loss.item()
                print(" Complete.")
                del raw, inpainted, cur_loss
                
            train_loss = train_loss/len(train_loader)
            print("Epoch: {} \tTraining Loss: {:.6f}".format(epoch, train_loss))
        torch.save(self.model, 'ResImageNet.pth')
        print("Model saved to 'ResImageNet.pth'")
    
    def testImage(self):
        # Create transform to torch.Tensor
        transform = transforms.Compose([transforms.ToTensor()])

        # Use ResImageDataset for auto image pack to samples
        train_set = ResImageDataset(self.image_dir, transform=transform)
        fig = plt.figure()

        img_index = random.randint(0, len(train_set) - 1)

        sample = train_set[img_index]

        img_input = sample["raw"]
        img_output = self.__call__(img_input) 
        transform_tmp = transforms.ToPILImage()
        img_output = img_output.view(3, img_output.shape[2], img_output.shape[3]).cpu().detach()
        img_output = transform_tmp(img_output)
        img_input = img_input.cpu().detach()
        img_input = transform_tmp(img_input)

        img_inpainted = sample["inpainted"]
        img_inpainted = img_inpainted.cpu().detach()
        img_inpainted = transform_tmp(img_inpainted)

        ax = plt.subplot(1, 3, 1)

        plt.tight_layout()
        ax.set_title("Input")
        ax.axis('off')
        plt.imshow(img_input)
        plt.pause(0.001)

        ax = plt.subplot(1, 3, 2)

        ax.set_title("Output")
        ax.axis('off')
        plt.imshow(img_output)
        plt.pause(0.001)

        ax = plt.subplot(1, 3, 3)

        ax.set_title("Inpainted")
        ax.axis('off')
        plt.imshow(img_inpainted)
        plt.pause(0.001)
        plt.show()
    
    def summary(self):
        summary(self.model, input_size=(1, 3, 1024, 1024))