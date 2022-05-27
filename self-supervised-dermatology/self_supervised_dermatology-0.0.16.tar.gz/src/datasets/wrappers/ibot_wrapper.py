import random
import math
import numpy as np
from typing import Union

from src.datasets.encrypted_image_folder import EncryptedImageFolder


class ImageFolderMask(EncryptedImageFolder):
    def __init__(self,
                 *args,
                 patch_size: float,
                 pred_ratio: Union[list, float],
                 pred_ratio_var: float,
                 pred_aspect_ratio: tuple,
                 pred_shape: str = 'block',
                 pred_start_epoch: int = 0,
                 **kwargs):
        super(ImageFolderMask, self).__init__(*args, **kwargs)
        pred_aspect_ratio = eval(pred_aspect_ratio)

        self.psz = patch_size
        if isinstance(pred_ratio, list) and len(pred_ratio) == 1:
            self.pred_ratio = pred_ratio[0]
        else:
            self.pred_ratio = pred_ratio

        if isinstance(pred_ratio_var, list) and len(pred_ratio_var) == 1:
            self.pred_ratio_var = pred_ratio_var[0]
        else:
            self.pred_ratio_var = pred_ratio_var

        if isinstance(self.pred_ratio, list) and \
                not isinstance(self.pred_ratio_var, list):
            self.pred_ratio_var = [self.pred_ratio_var] * len(self.pred_ratio)

        self.log_aspect_ratio = tuple(map(lambda x: math.log(x), pred_aspect_ratio))
        self.pred_shape = pred_shape
        self.pred_start_epoch = pred_start_epoch

    def get_pred_ratio(self):
        if hasattr(self, 'epoch') and self.epoch < self.pred_start_epoch:
            return 0

        if isinstance(self.pred_ratio, list):
            pred_ratio = []
            for prm, prv in zip(self.pred_ratio, self.pred_ratio_var):
                assert prm >= prv
                pr = random.uniform(prm - prv, prm + prv) if prv > 0 else prm
                pred_ratio.append(pr)
            pred_ratio = random.choice(pred_ratio)
        else:
            assert self.pred_ratio >= self.pred_ratio_var
            if self.pred_ratio_var > 0:
                pred_ratio = random.uniform(
                    self.pred_ratio - self.pred_ratio_var,
                    self.pred_ratio + self.pred_ratio_var)
            else:
                pred_ratio = self.pred_ratio

        return pred_ratio

    def set_epoch(self, epoch):
        self.epoch = epoch

    def __getitem__(self, index):
        output = super(ImageFolderMask, self).__getitem__(index)

        masks = []
        for img in output[0]:
            try:
                H, W = img.shape[1] // self.psz, img.shape[2] // self.psz
            except:
                # skip non-image
                continue

            # maximum number of masked patches
            high = self.get_pred_ratio() * H * W

            if self.pred_shape == 'block':
                # following BEiT (https://arxiv.org/abs/2106.08254)
                mask = np.zeros((H, W), dtype=bool)
                mask_count = 0
                while mask_count < high:
                    max_mask_patches = high - mask_count

                    delta = 0
                    for _ in range(10):
                        low = (min(H, W) // 3)**2
                        target_area = random.uniform(low, max_mask_patches)
                        aspect_ratio = math.exp(random.uniform(*self.log_aspect_ratio))
                        h = int(round(math.sqrt(target_area * aspect_ratio)))
                        w = int(round(math.sqrt(target_area / aspect_ratio)))
                        if w < W and h < H:
                            top = random.randint(0, H - h)
                            left = random.randint(0, W - w)

                            num_masked = mask[top:top + h, left:left + w].sum()
                            if 0 < h * w - num_masked <= max_mask_patches:
                                for i in range(top, top + h):
                                    for j in range(left, left + w):
                                        if mask[i, j] == 0:
                                            mask[i, j] = 1
                                            delta += 1

                        if delta > 0:
                            break

                    if delta == 0:
                        break
                    else:
                        mask_count += delta

            elif self.pred_shape == 'rand':
                mask = np.hstack([
                    np.zeros(H * W - int(high)),
                    np.ones(int(high)),
                ]).astype(bool)
                np.random.shuffle(mask)
                mask = mask.reshape(H, W)

            else:
                raise ValueError('Type of shape of partial prediction not implemented.')

            masks.append(mask)

        return output + (masks, )
