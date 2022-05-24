import torch as T
import abc


class LambdaLayer(T.nn.Module):
    def __init__(self, func):
        super(LambdaLayer, self).__init__()
        self.func = func

    def forward(self, x):
        return self.func(x)


class TimeDistributed(T.nn.Module):
    def __init__(self, module):
        super(TimeDistributed, self).__init__()
        self.module = module

    def forward(self, x):
        # B T ...
        if len(x.size()) <= 2:
            return self.module(x)
        x_reshape = x.contiguous().view(-1, *x.shape[2:])
        y = self.module(x_reshape)  # B*T ...
        return y.view(-1, x.shape[1], *y.shape[1:])


class WeightDecay(T.nn.Module):
    """
    Base wrapper class for any torch module for supporting regularization.

    Reference
    ----------
    [1] https://github.com/szymonmaszke/torchlayers/blob/master/torchlayers/regularization.py#L150

    """ 
    def __init__(self, module, weight_decay, name: str = None):
        if weight_decay <= 0.0:
            raise ValueError(
                "Regularization's weight_decay should be greater than 0.0, got {}".format(
                    weight_decay
                )
            )

        super().__init__()
        self.module = module
        self.weight_decay = weight_decay
        self.name = name

        self.hook = self.module.register_full_backward_hook(self._weight_decay_hook)

    def remove(self):
        self.hook.remove()

    def _weight_decay_hook(self, *_):
        if self.name is None:
            for param in self.module.parameters():
                if param.grad is None or T.all(param.grad == 0.0):
                    param.grad = self.regularize(param)
        else:
            for name, param in self.module.named_parameters():
                if self.name in name and (
                    param.grad is None or T.all(param.grad == 0.0)
                ):
                    param.grad = self.regularize(param)

    def forward(self, *args, **kwargs):
        return self.module(*args, **kwargs)

    def extra_repr(self) -> str:
        representation = "weight_decay={}".format(self.weight_decay)
        if self.name is not None:
            representation += ", name={}".format(self.name)
        return representation

    @abc.abstractmethod
    def regularize(self, parameter):
        pass


class L2Regularization(WeightDecay):
    """Regularize module's parameters using L2 weight decay.
    Example::
        import torchlayers as tl
        # Regularize only weights of Linear module
        regularized_layer = tl.L2(tl.Linear(30), weight_decay=1e-5, name="weight")
    .. note::
            Backward hook will be registered on `module`. If you wish
            to remove `L2` regularization use `remove()` method.
    Parameters
    ----------
    module : torch.nn.Module
        Module whose parameters will be regularized.
    weight_decay : float
        Strength of regularization (has to be greater than `0.0`).
    name : str, optional
        Name of parameter to be regularized (if any).
        Default: all parameters will be regularized (including "bias").
    """

    def regularize(self, parameter):
        return self.weight_decay * parameter.data


class L1Regularization(WeightDecay):
    """Regularize module's parameters using L1 weight decay.
    Example::
        import torchlayers as tl
        # Regularize all parameters of Linear module
        regularized_layer = tl.L1(tl.Linear(30), weight_decay=1e-5)
    .. note::
            Backward hook will be registered on `module`. If you wish
            to remove `L1` regularization use `remove()` method.
    Parameters
    ----------
    module : torch.nn.Module
        Module whose parameters will be regularized.
    weight_decay : float
        Strength of regularization (has to be greater than `0.0`).
    name : str, optional
        Name of parameter to be regularized (if any).
        Default: all parameters will be regularized (including "bias").
    """

    def regularize(self, parameter):
        return self.weight_decay * T.sign(parameter.data)