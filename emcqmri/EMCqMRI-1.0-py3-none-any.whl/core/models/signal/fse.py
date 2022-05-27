from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

from core.base import base_signal_model
import torch


class Fse(base_signal_model.SignalModel):
    """
        Class implementing the forward model of a Fast Spin Echo (FSE) based acquisition.
        Contains methods:
            - setTau: set inversion times of acquisition
            - forwardModel: Defines the signal model
            - generateWeightedImages: wrapper to generate N weighted images from A and T2 maps
            - gradients: Uses autograd to automatically compute gradients w.r.t. the likelihood function
            - initializeParameters: Initialises all tissue parameters 
    """
    def __init__(self, config_object):
        super(Fse, self).__init__()
        self.__name__ = 'Fast Spin Echo'
        self.__nParameters__ = 2
        self.args = config_object.args

    def __forwardModel__(self, kappa, tau):
        return torch.abs(torch.abs(kappa[0]) * torch.exp(torch.div(tau*(-1), torch.abs(kappa[1]))))

    def forward(self, kappa, tau):
        weightedImages = []
        for tau_ in tau:
            w_image = self.__forwardModel__(kappa, tau_).view(kappa[0].shape)
            weightedImages.append(w_image)
        return torch.stack(weightedImages)

    def initialize_parameters(self, signal):
        mipSignal, _ = torch.max(signal[:], 1)
        if not self.args.engine.inferenceModel == 'mle':
            ro_map = torch.autograd.Variable(mipSignal.to(device=self.args.engine.device), requires_grad=True)
            t2_map = torch.autograd.Variable(torch.ones_like(ro_map).to(device=self.args.engine.device), requires_grad=True)
            permute_list = [1, 0] + [i+2 for i in range(ro_map.dim()-1)]
            initialized_variables = torch.stack([ro_map, t2_map]).permute(permute_list)
        else:
            ro_map = torch.autograd.Variable(mipSignal[0].to(device=self.args.engine.device), requires_grad=True)
            t2_map = torch.autograd.Variable(torch.ones_like(ro_map).to(device=self.args.engine.device), requires_grad=True)
            initialized_variables = [ro_map, t2_map]
        
        return initialized_variables







