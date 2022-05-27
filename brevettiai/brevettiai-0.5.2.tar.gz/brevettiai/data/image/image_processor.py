import numpy as np

from pydantic import BaseModel
from abc import ABC, abstractmethod


class ImageProcessor(BaseModel, ABC):
    """
    Baseclass for implementing interface for image proccessors
    """
    type: str

    def output_size(self, input_height, input_width):
        """Calculated output size of output after postprocessing, given input image sizes"""
        return input_height, input_width

    def output_channels(self, input_channels):
        """Calculated output channel number"""
        return input_channels

    @abstractmethod
    def process(self, image):
        """Process image according to processor"""
        raise NotImplementedError("process(image)-> image should be implemented")
        # noinspection PyUnreachableCode
        return image

    @staticmethod
    def affine_transform(input_height, input_width):
        return np.eye(3)
