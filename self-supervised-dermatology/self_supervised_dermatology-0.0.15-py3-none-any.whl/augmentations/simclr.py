from torchvision import transforms

from src.augmentations.augmentations import RandomApply, Solarization


class SimCLRDataAugmentation(object):
    def __init__(self,
                 target_size=96,
                 gaussian_kernel: int = 23,
                 scaling: float = 1.0,
                 two_augmentations=False):
        # configs
        self.target_shape = target_size
        self.scaling = scaling
        self.two_augmentations = two_augmentations

        # normalization
        normalize = transforms.Compose([
            transforms.ToTensor(),
            transforms.Normalize((0.485, 0.456, 0.406), (0.229, 0.224, 0.225)),
        ])

        # data augmentation
        color_jitter = transforms.ColorJitter(0.8 * self.scaling,
                                              0.8 * self.scaling,
                                              0.8 * self.scaling,
                                              0.2 * self.scaling)
        self.data_aug = transforms.Compose([
            transforms.RandomResizedCrop(size=self.target_shape),
            transforms.RandomHorizontalFlip(p=0.5),
            transforms.RandomApply([color_jitter], p=0.8),
            transforms.RandomGrayscale(p=0.2),
            transforms.GaussianBlur(kernel_size=gaussian_kernel,
                                    sigma=(0.1, 2)),
            normalize,
        ])

        if self.two_augmentations:
            # in BYOL they used two different augmentations
            # the second one had slightly other probabilities
            # and includes solarization
            gauss = transforms.GaussianBlur(kernel_size=gaussian_kernel,
                                            sigma=(0.1, 2))
            self.data_aug_2 = transforms.Compose([
                transforms.RandomResizedCrop(size=self.target_shape),
                transforms.RandomHorizontalFlip(p=0.5),
                transforms.RandomApply([color_jitter], p=0.8),
                transforms.RandomGrayscale(p=0.2),
                RandomApply(gauss, p=0.1),
                Solarization(p=0.2),
                normalize,
            ])

    def __call__(self, image):
        # create two augmentations of the same image
        img_aug_1 = self.data_aug(image)
        if self.two_augmentations:
            img_aug_2 = self.data_aug_2(image)
        else:
            img_aug_2 = self.data_aug(image)
        return img_aug_1, img_aug_2
