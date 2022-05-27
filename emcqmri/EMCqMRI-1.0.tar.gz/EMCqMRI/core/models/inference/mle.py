from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

from core.base import base_inference_model
from core.utilities.core_utilities import ProgressBarWrap
import torch


class Mle(base_inference_model.InferenceModel, object):
    """
    """
    def __init__(self, config_object):
        super(Mle, self).__init__()
        self.__name__ = 'MLE'
        self.__require_initial_guess__ = True
        self.args = config_object.args

    @ProgressBarWrap
    def update_bar(self, loss, args):
        return -1

    def forward(self, inputs):
        signal = inputs
        initial_kappa = self.args.engine.signal_model.initialize_parameters(signal)

        self.args.engine.optimizer = torch.optim.Adam(list(initial_kappa), lr=self.args.engine.learningRate, betas=(0.8, 0.899))
        for _ in range(self.args.inference.inferenceSteps):
            self.args.engine.optimizer.zero_grad()

            weighted_images = self.args.engine.signal_model.forward(initial_kappa, self.args.task.tau)
            loss = self.args.engine.likelihood_model.likelihood(signal, weighted_images)
            self.update_bar(loss.item(), self.args)

            loss.backward()

            self.args.engine.optimizer.step()
            estimates = initial_kappa

        return torch.stack(estimates)
