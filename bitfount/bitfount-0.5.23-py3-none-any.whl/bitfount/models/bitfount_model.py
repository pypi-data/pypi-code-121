"""Contains the base classes for handling custom models."""

from abc import ABC
from typing import Any

from bitfount.models.base_models import _BaseModel


# This class must implement `DistributedModelProtocol` but cannot inherit from it for
# two reasons:
# 1. Pytorch lightning does not like this for some reason and throws an error in the
# `PyTorchBitfountModel` subclass:
#   "AttributeError: cannot assign module before Module.__init__() call"
# 2. If this inherits from `DistributedModelProtocol`, mypy does not ensure that an
# implementation actually implements the protocol. As a result, we have to do an
# `isinstance` check which will always return `True` if the protocol is part of the
# hierarchy regardless of whether the implementation actually implements the protocol.
class BitfountModel(_BaseModel, ABC):
    """Base class for custom models which must implement `DistributedModelProtocol`.

    A base tagging class to highlight custom models which are designed to be uploaded to
    Bitfount Hub.
    """

    def __init__(self, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self.class_name = type(self).__name__  # overrides _BaseModel attribute
