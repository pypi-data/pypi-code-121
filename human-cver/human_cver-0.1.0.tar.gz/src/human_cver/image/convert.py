import torch
import numpy as np
import torchvision.transforms as transforms

IMG_MEAN = [0.485, 0.456, 0.406]
IMG_STD = [0.229, 0.224, 0.225]


def tensor_to_bgr(img, normalized=True):
    img = img.permute(1, 2, 0).numpy()

    if normalized:
        mean = np.array(IMG_MEAN)
        std = np.array(IMG_STD)

        img = img * std + mean

    img = img[:, :, ::-1].copy() * 255.0
    img = img.astype(np.uint8)
    return img


def bgr_to_tensor(bgr_img, normalized=True):
    rgb_img = bgr_img[:, :, ::-1]
    img = np.transpose(rgb_img.astype(np.float32), (2, 0, 1)) / 255.0
    img = torch.from_numpy(img).float()
    if normalized:
        img = transforms.Normalize(mean=IMG_MEAN, std=IMG_STD)(img)
    return img
