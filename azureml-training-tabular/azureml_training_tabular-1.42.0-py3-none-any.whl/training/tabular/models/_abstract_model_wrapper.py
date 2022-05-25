# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
from abc import ABC, abstractmethod


class _AbstractModelWrapper(ABC):
    """Abstract base class for the model wrappers."""

    def __init__(self):
        """Initialize AbstractModelWrapper class."""
        pass

    @abstractmethod
    def get_model(self):
        """
        Abstract method for getting the inner original model object.

        :return: An inner model object.
        """
        raise NotImplementedError
