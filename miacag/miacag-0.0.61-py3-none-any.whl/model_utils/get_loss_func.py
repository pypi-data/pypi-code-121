import torch.nn as nn
from monai.losses import DiceLoss
from monai.losses import DiceCELoss
from miacag.model_utils.siam_loss import SimSiamLoss
import torch


def get_loss_func(config):
    criterions = []
    for loss in config['loss']['name']:
        if loss == 'CE':
            criterion = nn.CrossEntropyLoss(reduction='mean')
            criterions.append(criterion)
        elif loss == 'dice_loss':
            criterion = DiceLoss(
                include_background=False,
                to_onehot_y=False, sigmoid=False,
                softmax=True, squared_pred=True)
            criterions.append(criterion)
        elif loss == 'diceCE_loss':
            criterion = DiceCELoss(
                include_background=True,
                to_onehot_y=False, sigmoid=False,
                softmax=True, squared_pred=True)
            criterions.append(criterion)
        elif loss == 'Siam':
            criterion = SimSiamLoss('original')
            criterions.append(criterion)
        elif loss == 'total':
            pass
        else:
            raise ValueError("Loss type is not implemented")
    return criterions
