from .imageFile import *
from .channel import Channel
from .DCCExceptions import *
import numpy as np
import PIL.Image
import matplotlib.pyplot as plt
import os
import re
from typing import List, Union


class Image:
    supportedClasses = [CZIFile_, TIFFFile, PILFile, MATLABFile]
    supportedFormats = []

    def __init__(self, imageData: np.ndarray = None, path: str = None):
        self._getSupportedFormats()  # FIXME

        if path is not None:
            if not os.path.exists(str(path)):
                raise ValueError("Cannot load '{0}': file does not exist".format(path))

            self.path = path
            self.channels = []
            self.__fileObject = None
            for supportedClass in Image.supportedClasses:
                try:
                    fileObject = supportedClass(path)
                    imageData = fileObject.imageDataFromPath()
                    if imageData.nbytes != 0:
                        self.channels = self.channelsFromArray(imageData)
                        self.__fileObject = fileObject
                    break
                except NotImplementedError as e:
                    raise e
                except:
                    continue
            if self.__fileObject is None:
                message = "Cannot read '{0}': not a recognized image format ({1})".format(self.path,
                                                                                          Image.supportedFormats)
                raise InvalidFileFormatException(message)
        else:
            self.path = None
            self.__fileObject = None
            self.channels = self.channelsFromArray(imageData)

    def __str__(self) -> str:
        return str(np.array(self.channels))

    def __eq__(self, other) -> bool:
        if not isinstance(other, Image):
            return False
        return np.array_equal(self.asArray(), other.asArray())

    def __getitem__(self, index):
        return self.channels[index]

    @property
    def shape(self):
        if len(self.channels) != 0:
            x, y = self.channels[0].shape
            return x, y, len(self.channels)

    @property
    def sizeInBytes(self) -> int:
        totalSize = 0
        for channel in self.channels:
            totalSize += channel.sizeInBytes
        return totalSize

    def removeChannels(self, channels: list):
        for index in channels:
            del self.channels[index]

    def keepChannel(self, channel: int):
        allIndexes = list(range(0, len(self.channels)))
        for index in allIndexes:
            if index != channel:
                del self.channels[index]

    def asChannelsArray(self):
        channelsPixels = list(map(lambda c: c.pixels, self.channels))
        return channelsPixels

    def asArray(self):
        channelArrays = self.asChannelsArray()
        imageData = np.dstack(channelArrays)
        return imageData

    def asOriginalArray(self):
        # or call asArray on an original Image Object (currently Channel.original is only np.ndarray)
        originalChannelArrays = list(map(lambda c: c.originalPixels, self.channels))
        return np.dstack(originalChannelArrays)

    def replaceFromArray(self, imageArray):
        assert len(self.channels) == imageArray.shape[2], "Array has to contain the same number of channels."

        for i, channel in enumerate(self.channels):
            channel.replaceFromArray(imageArray[:, :, i])

    def save(self, filePath):
        imageAsArray = self.asArray()

        if len(self.channels) == 1:
            mode = 'L'
        elif len(self.channels) == 3:
            mode = 'RGB'
        pilImage = PIL.Image.fromarray(imageAsArray, mode=mode)
        pilImage.save(filePath)
        pilImage.close()

    def display(self, colorMap=None):
        if self.shape[-1] not in [1, 3]:
            Channel.multiChannelDisplay(self.channels)
        else:
            plt.imshow(self.asArray().squeeze().swapaxes(0, 1), cmap=colorMap)
            plt.show()

    def channelsFromArray(self, array):
        # This (static) method creates new Channel Objects
        if array.ndim == 2:
            return [Channel(array.T)]
        elif array.ndim == 3:
            channelsData = np.squeeze(np.dsplit(array.transpose(1, 0, 2), array.shape[2]))
            # (temp fix) : channelsData is only 2D if input array has only one channel (shape (x, y, 1))
            if channelsData.ndim == 2:
                channelsData = np.expand_dims(channelsData, axis=0)
            channels = list(map(lambda pix: Channel(pix), channelsData))
            return channels
        else:
            raise DimensionException(array.ndim)

    def _getSupportedFormats(self):
        fmts = list(map(lambda cls: cls.supportedFormats, Image.supportedClasses))
        Image.supportedFormats = [item for sublist in fmts for item in sublist]

    @property
    def hasLabelledComponents(self) -> bool:
        for channel in self.channels:
            if not channel.hasLabelledComponents:
                return False
        return True

    @property
    def hasMask(self) -> bool:
        for channel in self.channels:
            if channel.mask is None:
                return False
        return True

    @property
    def hasOriginal(self) -> bool:
        for channel in self.channels:
            if not channel.hasOriginal:
                return False
        return True

    def labelMaskComponents(self):
        for channel in self.channels:
            channel.labelMaskComponents()

    def setLabelledComponents(self, label: 'Channel'):
        for channel in self.channels:
            channel.setLabelledComponents(label.pixels)

    def analyzeComponents(self):
        for channel in self.channels:
            channel.analyzeComponents()

    def filterNoise(self):
        for channel in self.channels:
            channel.filterNoise()

    def threshold(self, value=None):
        for channel in self.channels:
            channel.threshold(value)

    def setMask(self, mask: 'Channel'):
        if mask.isBinary:
            for channel in self.channels:
                channel.setMask(mask)
        else:
            raise ValueError("Mask must be binary")

    def setMasks(self, masks: List['Channel']):
        if len(masks) == len(self.channels):
            for i, mask in enumerate(masks):
                if mask.isBinary:
                    self.channels[i].setMask(mask)
                else:
                    raise ValueError("Mask must be binary")
        else:
            raise ValueError("Must provide one mask per channel")

    def setMaskFromThreshold(self, value=None):
        for channel in self.channels:
            channel.setMaskFromThreshold(value)

    def applyConvolution(self, matrix: Union[np.ndarray, list]) -> None:
        for channel in self.channels:
            channel.applyConvolution(matrix)

    def applyXDerivative(self) -> None:
        for channel in self.channels:
            channel.applyXDerivative()

    def applyYDerivative(self) -> None:
        for channel in self.channels:
            channel.applyYDerivative()

    def applyGaussianFilter(self, sigma: float) -> None:
        for channel in self.channels:
            channel.applyGaussianFilter(sigma)

    def applyThresholding(self, value=None) -> None:
        if value is None:
            self.applyIsodataThresholding()
        else:
            self.applyGlobalThresholding(value)

    def applyGlobalThresholding(self, value) -> None:
        for channel in self.channels:
            channel.applyGlobalThresholding(value)

    def applyIsodataThresholding(self) -> None:
        for channel in self.channels:
            channel.applyIsodataThresholding()

    def applyOtsuThresholding(self) -> None:
        for channel in self.channels:
            channel.applyOtsuThresholding()

    def applyOpening(self, size: int) -> None:
        for channel in self.channels:
            channel.applyOpening(size)

    def applyClosing(self, size: int) -> None:
        for channel in self.channels:
            channel.applyClosing(size)

    def applyErosion(self, size: int = 2):
        for channel in self.channels:
            channel.applyErosion(size)

    def applyDilation(self, size: int = 2):
        for channel in self.channels:
            channel.applyDilation(size)

    def applyNoiseFilter(self, algorithm=None):
        for channel in self.channels:
            channel.applyNoiseFilter(algorithm)

    def applyNoiseFilterWithErosionDilation(self, erosion_size=2, dilation_size=2, closing_size=2):
        for channel in self.channels:
            channel.applyNoiseFilterWithErosionDilation(erosion_size, dilation_size, closing_size)

    def applyOpeningToMask(self, size: int = None, iterations: int = 1):
        for channel in self.channels:
            channel.mask.applyNdImageBinaryOpening(size, iterations)

    def applyClosingToMask(self, size: int = None, iterations: int = 1):
        for channel in self.channels:
            channel.mask.applyNdImageBinaryClosing(size, iterations)
