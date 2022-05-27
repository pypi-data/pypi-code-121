from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

from .rnn import Rnn
from core.base import base_inference_model
from core.utilities.core_utilities import ProgressBarWrap
import torch
from torch.autograd import Variable
import torch.nn as nn


class Rim(base_inference_model.InferenceModel, nn.Module):
    """
        Class Implementing the RIM model.
        Methods:
            - setOpts
                inputs: a Dict containing the key and value for a new configuration setting
            - forward
                inputs: signal (measured signal); args (options containing, at least args.batchSize and args.device)
                outputs: Estimated parameters
    """

    def __init__(self, config_object):
        super(Rim, self).__init__()
        self.__name__ = 'RIM'
        self.__require_initial_guess__ = True
        self.args = config_object.args
        self.__buildNetwork__()

    def __buildNetwork__(self):
        """
            Hidden method that instanciates a version of the RNN module based on the configuration file
        """
        self.rnn = Rnn(self.args.inference.inputChannels,
                       self.args.inference.outputChannelsLayer1,
                       self.args.inference.outputChannelsLayer2,
                       self.args.inference.outputChannelsLayer3,
                       self.args.inference.outputChannels,
                       self.args)

    def __initHidden__(self, signal):
        """
            Initialises all hidden states in the network
        """
        shape_input = torch.tensor((signal.shape)[2:])
        shape_hs1 = [1, self.args.engine.batchSize*int(torch.prod(shape_input)), self.args.inference.outputChannelsLayer1]
        shape_hs2 = [1, self.args.engine.batchSize*int(torch.prod(shape_input)), self.args.inference.outputChannelsLayer3]
        st_1 = Variable(torch.zeros(tuple(shape_hs1)).to(device=self.args.engine.device))
        st_2 = Variable(torch.zeros(tuple(shape_hs2)).to(device=self.args.engine.device))
        return [st_1, st_2]

    def __getGradients__(self, signal, kappa, tau):
        """
            Compute and return gradients of the Likelihood Function w.r.t. parameter maps
        """
        gradientParamBatch = []
        for batch in range(len(signal)):
            if isinstance(kappa,list): #For kappa with multiple types of map (e.g. relaxometry and motion)
                motion_map = kappa[1]
                clonedKappa = []   
                for num_kappa in range(len(kappa)):
                    cloned_k = [Variable(pmap.clone(), requires_grad=True) for pmap in kappa[num_kappa][batch]]
                    clonedKappa.append(cloned_k)
                gradients = self.args.engine.likelihood_model.gradients(signal[batch], clonedKappa, tau)
                gradientParamBatch.append(torch.cat(gradients,0))
            else:
                clonedMaps = [Variable(pmap.clone(), requires_grad=True) for pmap in kappa[batch]]
                gradientParamBatch.append(self.args.engine.likelihood_model.gradients(signal[batch], clonedMaps, tau))
        
        paramGrad = torch.stack(gradientParamBatch)
        paramGrad[torch.isnan(paramGrad)] = 0
        paramGrad[torch.isinf(paramGrad)] = 0
        return paramGrad

    def forward(self, inputs):
        signal = inputs
        kappa = self.args.engine.signal_model.initialize_parameters(signal)

        hidden = self.__initHidden__(signal)
        estimates = []

        for _ in range(self.args.inference.inferenceSteps):
            paramGrad = self.__getGradients__(signal, kappa, self.args.dataset.tau)

            if isinstance(kappa,list):
                tensor_kappa = torch.cat(kappa,1)
                input = torch.cat([tensor_kappa, paramGrad], 1)
            else:
                input = torch.cat([kappa, paramGrad], 1)

            dx, hidden = self.rnn.forward(input, hidden)

            if isinstance(kappa,list):
                shape_list_kappa = [k.shape for k in kappa]
                cutoff_index = [s[1] for s in shape_list_kappa]
                tensor_kappa = tensor_kappa + dx
                kappa = list(torch.split(tensor_kappa, [*cutoff_index], dim=1))
            else:
                kappa = torch.abs(kappa + dx)

            estimates.append(kappa)

        return torch.stack(estimates)
