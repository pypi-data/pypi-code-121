from PIL import Image
from torchvision import transforms
from src.augmentations.augmentations import GaussianBlur, Solarization


class iBOTDataAugmentation(object):
    def __init__(self,
                 global_crops_scale,
                 local_crops_scale,
                 global_crops_number,
                 local_crops_number):

        # evaluate if strings (caused by yaml file)
        if type(global_crops_scale) is str:
            global_crops_scale = eval(global_crops_scale)
        if type(local_crops_scale) is str:
            local_crops_scale = eval(local_crops_scale)

        # augmentations
        flip_and_color_jitter = transforms.Compose([
            transforms.RandomHorizontalFlip(p=0.5),
            transforms.RandomApply([
                transforms.ColorJitter(
                    brightness=0.4, contrast=0.4, saturation=0.2, hue=0.1)
            ], p=0.8),
            transforms.RandomGrayscale(p=0.2),
        ])
        # normalization
        normalize = transforms.Compose([
            transforms.ToTensor(),
            transforms.Normalize((0.485, 0.456, 0.406), (0.229, 0.224, 0.225)),
        ])

        # global crops
        self.global_crops_number = global_crops_number
        # first global crop
        self.global_trans1 = transforms.Compose([
            transforms.RandomResizedCrop(224,
                                         scale=global_crops_scale,
                                         interpolation=Image.BICUBIC),
            flip_and_color_jitter,
            GaussianBlur(1.0),
            normalize,
        ])
        # second global crop
        self.global_trans2 = transforms.Compose([
            transforms.RandomResizedCrop(224,
                                         scale=global_crops_scale,
                                         interpolation=Image.BICUBIC),
            flip_and_color_jitter,
            GaussianBlur(0.1),
            Solarization(0.2),
            normalize,
        ])
        # transformation for the local small crops
        self.local_crops_number = local_crops_number
        self.local_trans = transforms.Compose([
            transforms.RandomResizedCrop(96,
                                         scale=local_crops_scale,
                                         interpolation=Image.BICUBIC),
            flip_and_color_jitter,
            GaussianBlur(p=0.5),
            normalize,
        ])

    def __call__(self, image):
        crops = []

        # global crops
        crops.append(self.global_trans1(image))
        for _ in range(self.global_crops_number - 1):
            crops.append(self.global_trans2(image))

        # local crops
        for _ in range(self.local_crops_number):
            crops.append(self.local_trans(image))

        return crops
