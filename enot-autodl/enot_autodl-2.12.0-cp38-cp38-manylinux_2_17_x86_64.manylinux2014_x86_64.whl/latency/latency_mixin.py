import inspect
from numbers import Real
from typing import Tuple

import torch

__all__ = [
    'LatencyMixin',
]


LATENCY_METHOD_NAME_PREFIX = 'latency_'


def _check_signature(latency_method):
    signature = inspect.signature(latency_method)
    param_names = list(signature.parameters)
    param_descriptions = list(signature.parameters.values())

    if param_names[:2] != ['self', 'inputs']:
        raise TypeError(f'Incorrect first arguments of latency calculator {latency_method.__qualname__}: '
                        f'must be (self, inputs)')
    for other_param in param_descriptions[2:]:
        if other_param.default is other_param.empty:
            raise TypeError('Params except inputs must have a default value')


class LatencyMixin:
    r"""Base class for operations with latency.

    Implement latency calculators like `def latency_<name>(self, inputs) -> float: ...`
    Then you can use it like `op.forward_latency(inputs, '<name>')`

    """

    def __init_subclass__(cls, **kwargs):
        dct = cls.__dict__
        # Find latency calculators and check their signatures
        for name, field in dct.items():
            if name.startswith(LATENCY_METHOD_NAME_PREFIX) and callable(field):
                _check_signature(field)

        super().__init_subclass__(**kwargs)

    def forward_latency(
            self,
            inputs: Tuple[torch.Tensor, ...],
            latency_type: str,
    ) -> Real:
        r"""

        Parameters
        ----------
        inputs : Tuple[Tensor, ...]
            Inputs.
        latency_type : str
            Type of latency which you want to run. user should implement it by
            yourself after inhering of this class.
        Returns
        -------
        float:
            Latency of user defined op.

        Raises
        ------
        ValueError
            If user don't implement latency_<latency_type> methid of inherited class.
        """
        try:
            calculator = getattr(self, LATENCY_METHOD_NAME_PREFIX + latency_type)
        except AttributeError:
            raise ValueError(
                f'Latency calculator for latency type {latency_type!r} is not defined in '
                f'{self.__class__.__qualname__}'
            )

        return calculator(inputs)
