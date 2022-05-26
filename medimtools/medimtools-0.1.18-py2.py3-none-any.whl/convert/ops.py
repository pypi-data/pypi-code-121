import SimpleITK as sitk
import torch


def sitk2torchtensor(image):
    np_image = sitk.GetArrayFromImage(image)
    return torch.tensor(np_image)


def torchtensor2sitk(tensor):
    np_image = tensor.detach().numpy()
    return sitk.GetImageFromArray(np_image)
