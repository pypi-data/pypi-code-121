import numpy as np

import torch
import torch.nn as nn
import pytorch_lightning as pl

# Add xaitk-saliency required imports
from smqtk_classifier import ClassifyImage
from xaitk_saliency.impls.gen_image_classifier_blackbox_sal.rise import RISEStack
from xaitk_saliency.impls.gen_image_classifier_blackbox_sal.slidingwindow import (
    SlidingWindowStack,
)

METHODS = {
    "RISEStack": RISEStack(100, 8, 0.5, seed=0, threads=6, debiased=False),
    "SlidingWindow": SlidingWindowStack((10, 10), (4, 4), threads=6),
}

from ..ai.run import get_model


class ClfModel(ClassifyImage):
    def __init__(self, model=None, xy=None):
        self.model = model
        self.xy = xy

    def set_xy(self, xy):
        self.xy = xy

    def set_model(self, model):
        self.model = model

    def get_labels(self):
        return ["output"]

    def classify_images(self, image_iter):
        for img in image_iter:
            inp = torch.Tensor(img).permute(2, 0, 1).unsqueeze(0)
            out = self.model(inp)[0, self.xy[1], self.xy[0]].detach().numpy()
            yield dict(zip(self.get_labels(), [out]))

    def get_config(self):
        return {}


CLF_MODEL = ClfModel()


async def xai_run(xy=(50, 25)):
    model = get_model()
    xai = METHODS.get("SlidingWindow")
    CLF_MODEL.set_model(model.model)
    CLF_MODEL.set_xy(xy)
    output = torch.Tensor(xai(model.inputs[0].permute(1, 2, 0).numpy(), CLF_MODEL))

    return {"values": np.flipud(output).flatten().tolist(), "size": (102, 50)}
