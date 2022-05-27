from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

from abc import ABC, abstractmethod

class SignalModel(ABC):
    """Base class for implementation of likelihood models
    """
    
    def __init__(self):
        super().__init__()

    @abstractmethod
    def forward(self, kappa, *fixed_params):
        """Abstract function that defines the forward pass of the signal model.
        Generates a synthetic signal based on a signal model. This function must
        implement any necessary loops for generation of sequence of signals

        Args:
            kappa ([torch.Tensor]): a torch.Tensor or a list of torch.Tensor containing 
                independent parameters of the signal model.

            *fixed_params ([tuple]): any necessary fixed parameter of the signal model. 
             
        Raises:
            NotImplementedError: When the subclass does not override this method.

        Returns:
            ([torch.Tensor]): Simulated (or synthetic) signal.
        """
        raise NotImplementedError("Forward_model not implemented")

    @abstractmethod
    def initialize_parameters(self):
        """
        Initializes the independent parameters of the signal model. In general, these are
        the parameters that will be estimated by the inference model.
             
        Raises:
            NotImplementedError: When the subclass does not override this method.

        Returns:
            ([torch.Tensor]) or ([list]): If list, each element contains a torch.Tensor of different
            types (e.g. images, scalars, etc.). Each torch.Tensor is defined as the parameter to
            be estimated by the inference model.
        """
        raise NotImplementedError("Parameter initialization method not implemented")