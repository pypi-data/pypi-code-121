from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

from abc import ABC, abstractmethod


class InferenceModel(ABC):
    """Base class for implementation of inference models
    """
    def __init__(self):
        super().__init__()

    @abstractmethod
    def forward(self, inputs):
        """Abstract function that defines the forward pass of the inference model.
        It supports conventional and Deep Learning methods. For iterative methods, the steps must
        be implemented within this function.

        Need subclass to implement different logics, like MLE, ResNet, RIM, etc.

        Args:
            inputs ([list]): list of torch.Tensors, containing one or more inputs. If one of the 
                inputs is an image, it must have shape [B, N, X, Y, ...], where B is the batch size, 
                N is the number of channels and X,Y,... are the image dimensions. If one of the inputs
                are scalar parameters, it must have shape [B, N, X], where B is the batch size,
                N is the number of channels and X the number of parameters.

        Raises:
            NotImplementedError: When the subclass does not override this method.

        Returns:
            ([torch.Tensor]): The subclass implementation should return the parameter estimates. If
            estimates are images, they should have shape [B, C, X, Y, ...], where B is the
            batch size, C is the number of parameters and X, Y,... are the image dimensions.
            If estimates are scalars, they should have shape [B, X], where B is the batch size and
            X are parameters.
        """
        raise NotImplementedError("Forward method not implemented")

    



    


