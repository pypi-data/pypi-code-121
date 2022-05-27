import torch
from torch.utils.data import Dataset
from torchvision import transforms

from src.datasets.wrappers.base_wrapper import DatasetWrapper


class ColorMeDatasetWrapper(DatasetWrapper):
    def __init__(self,
                 ds: Dataset,
                 target_shape=(96, 96, 3),
                 debug=False):
        super().__init__(ds, debug=debug)
        self.target_shape = eval(target_shape)
        self.resize = transforms.Resize(size=(self.target_shape[0],
                                              self.target_shape[1]))

    def __getitem_internal__(self, idx, preprocess=True):
        # get the keys from the dict
        img_raw, lbl = self.ds[idx]

        # preprocess image
        if preprocess:
            img = self.preprocess(img_raw)
        else:
            img = transforms.ToTensor()(img_raw)

        # resize image
        img = self.resize(img)

        # extract green channel
        img_green = img[1, :, :][None, :, :]

        # color distribution
        h_red = torch.histogram(img[0, :, :], bins=5, range=(0, 1)).hist
        h_blue = torch.histogram(img[2, :, :], bins=5, range=(0, 1)).hist
        hist = torch.concat((h_red, h_blue))
        # normalize distribution
        hist = hist / torch.sum(hist)

        return img, img_green, hist, torch.tensor(lbl)
