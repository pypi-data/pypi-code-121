from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

from core.base import base_likelihood_model
import torch
import math
import numpy as np


class Gaussian(base_likelihood_model.Likelihood):
    """
        Class for the Gaussian PDF.
        Methods:
            - logLikelihood
                inputs: signal (measured signal), mu (simulated signal) and sigma (SD of the noise)
                outputs: data consistency loss
            - applyNoise
                inputs: a signal and sigma
                outputs: Noisy signal corrupted by additive gaussian noise
    """
    
    def __init__(self, config_object):
        super(Gaussian, self).__init__(config_object, self)
        self.__name__ = 'Gaussian'
        self.args = config_object.args

    def likelihood(self, signal, modeled_signal):
        return torch.sum((signal - modeled_signal)**2)

    def apply_noise(self, signal, sigma):
        signal += torch.from_numpy(np.random.normal(0.0, sigma, signal.size())).to(self.args.engine.device)
        return signal

    