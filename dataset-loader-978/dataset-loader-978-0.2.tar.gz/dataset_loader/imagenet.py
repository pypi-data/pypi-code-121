import os
import torch
from PIL import Image
import torchvision.transforms as transforms
import torchvision.transforms.functional as F
import warnings


class imagenet():

    def __init__(self,
                 _path='IMAGENET_path.txt',
                 _labs='labels.txt',
                 _classes='imagenet_classes.txt',
                 _gts='imagenet_val_gts.txt',
                 data_root='./annotations/data/',
                 p='./annotations/data/ILSVRC2012_devkit_t12/data/',
                 base=0,
                 window=1,
                 pattern='ILSVRC2012_val_********.JPEG'):

        self._path,self._labs,self._classes,self._gts,self.pattern,self.p = \
            _path, _labs, _classes, _gts, pattern, p
        self.means,self.stds=[0.485, 0.456, 0.406], [0.229, 0.224, 0.225]
        self.name='imagenet'

        self.base,self.window=base,window

        try:
            with open(data_root + self._path, 'r') as f:
                p = os.path.join(f.read().strip())
            # p += '/'
            labs_w = []
            with open(data_root + self._labs, 'r') as f:
                labs_w = [x[9:] for x in f.read().strip().split('\n')]

            labs = []
            with open(data_root + self._classes, 'r') as f:
                labs = [x for x in f.read().strip().split('\n')]

            labs1 = {}
            with open(data_root + self._labs, 'r') as f:
                labs1 = {str(self.get_name_images(x.split()[0])): x.split()[2] for x in f.read().split('\n')}
                # labs1=[x[2] for x in labs1.split()]

            GT = {}
            with open(data_root + self._gts, 'r') as f:
                GT = {self.get_name_images(x.split()[0]): self.get_name_images(x.split()[0]) + ' ' + x.split()[2] for x in
                      f.read().strip().split('\n')}

            self.img_list = {k: v for k, v in enumerate(sorted(os.listdir(p))[base:base + window])}

            if len(self.img_list) == 0:
                raise ValueError(f'Empty dataset')
            elif len(self.img_list) < self.window:
                warnings.warn(f'Dataset length lower than window ({len(self.img_list)} < {self.window})')

            self.p=p
            self.__dict__.update(locals())

        except Exception as e:
            print(e)
            self.img_list = {k: v for k, v in enumerate(sorted(os.listdir(p))[base:base + window])}
            GT = {self.get_name_images(x.split()[0]): self.get_name_images(x.split()[0]) + ' ' + x.split()[2] for x in
                  f.read().strip().split('\n')}
            self.p = p
            self.__dict__.update(locals())

    def get_name_images(self,s):
        return str(s)[-13:-5]

    def get_num_img(self,s):
        return int(s[-13:-5])

    def get_n_imgs(self,l, pattern):
        ret = []
        for i in range(len(l)):
            s = ''.join(map(str, ['0' for _ in range(13 - 5 - len(str(l[i])))])) + str(l[i])
            p = pattern.replace('********', s)
            ret.append(p)
        return {k: v for k, v in zip(range(len(l)), ret)}


    def get_infos(self):
        return self.__dict__

    def get_img_number(self,img):
        return str(img[-13:-5])

    def apply_transform(self,image,normalize=True,size=224):
        if not isinstance(image, Image.Image):
            image = F.to_pil_image(image)
        if normalize:
            transform = transforms.Compose([
                transforms.Resize(size),
                transforms.CenterCrop(size),
                transforms.ToTensor(),
                transforms.Normalize(self.means, self.stds)
            ])
        else:
            transform = transforms.Compose([
                transforms.Resize(size),
                transforms.CenterCrop(size),
                transforms.ToTensor(),
            ])

        tensor = transform(image).unsqueeze(0)

        tensor.requires_grad = True

        return tensor

    def detransform(self, tensor):
        means, stds = torch.tensor([0.485, 0.456, 0.406]), torch.tensor([0.229, 0.224, 0.225])
        denormalized = transforms.Normalize(-1 * means / stds, 1.0 / stds)(tensor)

        return denormalized
