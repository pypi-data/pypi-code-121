from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

from abc import ABC, abstractmethod
import torch

class Likelihood(ABC):
    """Base class for implementation of likelihood models
    """

    def __init__(self, config_object, ll_obj):
        """
        Args:
            config_object ([Configuration]): Configuration object where following attributes
                must be specified:

                - args.engine.signal_model ([SignalModel])

            ll_obj ([Likelihood]): Circular reference to child of Likelihood object
        """

        super().__init__()
        self.args = config_object.args
        self.ll_model = ll_obj

    @abstractmethod
    def likelihood(self, signal, modeled_signal):
        """
        Computes the loss, or error, based on the negative log likelihood function.

        Args:
            signal ([torch.Tensor]): Measured, input signal.

            modeled_signal ([torch.Tensor]): Tensor containing a simulated signal, generated
                with a signal model.
             
        Raises:
            NotImplementedError: When the subclass does not override this method.

        Returns:
            ([torch.Float]): A scalar loss (i.e. error)
        """
        raise NotImplementedError("Likelihood Function not implemented")

    def gradients(self, signal, kappa, *extra_args):
        """
        Computes the gradient of the signal model parameters with respect to the likelihood function.
        This function can be overriden if you want to define your own gradients (e.g. analytical, 
        different shapes, etc.)

        Args:
            signal ([torch.Tensor]): Measured, input signal.
            kappa ([list]): A list of torch.Tensor parameters.
            *extra_args ([tuple]): Any additional parameters required by the signal model or 
                likelihood model
             
        Raises:
            TypeError: When kappa is not a list of torch.Tensor.

        Returns:
            ([list]): list of torch.Tensor with same number of elements as Kappa. Each element of the list
            is the gradient of each parameter with respect to the likelihood function.
        """
        with torch.enable_grad():
            weighted_images = self.args.engine.signal_model.forward(kappa, *extra_args)
            loss = self.ll_model.likelihood(signal, weighted_images)
            loss.backward()
            if isinstance(kappa,list):
                if isinstance(kappa[0],list): # This is for when kappa contains more than 1 type of parameter
                    param_map_gradient = []
                    for kappa_map in kappa:
                        gradient = ([param_map.grad for param_map in kappa_map])
                        param_map_gradient.append(torch.stack(gradient))
                else:
                    param_map_gradient = torch.stack([param_map.grad for param_map in kappa])
            else:
                param_map_gradient = kappa.grad
        return param_map_gradient


        
