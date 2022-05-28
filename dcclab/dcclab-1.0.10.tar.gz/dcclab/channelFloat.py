from .channel import *
from scipy.signal import convolve2d
from skimage.filters import *
import scipy.ndimage.filters as filters
import warnings
from skimage.filters.rank import entropy


class ChannelFloat(Channel):

    def __init__(self, pixels: np.ndarray):
        if "float" not in str(pixels.dtype):
            raise TypeError("Pixel type must be float.")
        maxValue = np.nanmax(pixels)
        if maxValue <= 1.0:
            self.__originalFactor = 1.0
            normalizedPixels = np.copy(pixels).astype(np.float32)
        else:
            self.__originalFactor = maxValue
            normalizedPixels = (np.copy(pixels) / maxValue).astype(np.float32)
        Channel.__init__(self, normalizedPixels)

    def getHistogramValues(self, normed: bool = False) -> typing.Tuple[np.ndarray, np.ndarray]:
        pixels = self.convertTo8BitsUnsignedInteger().pixels
        array = pixels.ravel()
        nbBins = len(np.bincount(array))
        hist, bins = np.histogram(array, nbBins, [0, nbBins], density=normed)
        return hist, bins

    def getEntropyFilter(self, filterSize: int):
        pixels = self.convertTo8BitsUnsignedInteger().pixels
        entropyFiltered = entropy(pixels, morphology.selem.square(filterSize, dtype=np.float32))
        return Channel(entropyFiltered.astype(np.float32))

    def convolveWith(self, matrix: typing.Union[np.ndarray, list]):
        convolvedArray = convolve2d(self.pixels.T, matrix, mode="same", boundary="symm")
        return Channel(convolvedArray.T)

    def getGaussianFilter(self, sigma: float = 1):
        gaussianFiltered = gaussian(self.pixels, sigma, mode="nearest", multichannel=False,
                                    preserve_range=True)
        return Channel(gaussianFiltered)

    def getStandardDeviationFilter(self, filterSize: int):
        pixels = self.pixels
        stdDevFilter1 = filters.uniform_filter(pixels, filterSize, mode="nearest")
        stdDevFilter2 = filters.uniform_filter(pixels * pixels, filterSize, mode="nearest")
        stdFiltered = np.sqrt(stdDevFilter2 - stdDevFilter1 * stdDevFilter1)
        if np.any(np.isnan(stdFiltered)):
            warnings.warn("Nan values encountered! Replacing them with 0.", category=RuntimeWarning)
            stdFiltered = np.nan_to_num(stdFiltered)
        return Channel(stdFiltered)

    def getIsodataThresholding(self):
        integerChannel = self.convertTo8BitsUnsignedInteger()
        return integerChannel.getIsodataThresholding()

    def getOtsuThresholding(self):
        integerChannel = self.convertTo8BitsUnsignedInteger()
        return integerChannel.getOtsuThresholding()

    def getAdaptiveThresholdMean(self, oddRegionSize: int = 3):
        integerChannel = self.convertTo8BitsUnsignedInteger()
        return integerChannel.getAdaptiveThresholdMean(oddRegionSize)

    def getAdaptiveThresholdGaussian(self, oddRegionSize: int = 3):
        integerChannel = self.convertTo8BitsUnsignedInteger()
        return integerChannel.getAdaptiveThresholdGaussian(oddRegionSize)

    def getHorizontalSobelFilter(self):
        sobelH = sobel_h(self.pixels.T)
        return Channel(sobelH.T)

    def getVerticalSobelFilter(self):
        sobelV = sobel_v(self.pixels.T)
        return Channel(sobelV.T)

    def getSobelFilter(self) -> Channel:
        sobelHV = sobel(self.pixels.T)
        return Channel(sobelHV)

    def convertTo8BitsUnsignedInteger(self):
        return self._convertToUnsignedInt(np.uint8)

    def convertTo16BitsUnsignedInteger(self):
        return self._convertToUnsignedInt(np.uint16)

    def _convertToUnsignedInt(self, dtype):
        convertedArray = ((np.copy(self.pixels)) * np.iinfo(dtype).max)
        return Channel(convertedArray.astype(dtype))

    def convertToNormalizedFloatMinToZeroMaxToOne(self):
        minimum = self.getExtrema()[0]
        minTo0 = self.pixels - minimum
        maximum = np.max(minTo0)
        maxTo1 = minTo0 / maximum
        return Channel(maxTo1)

    def applyPoissonNoise(self, scale: float):
        noise = np.random.poisson(scale * self.pixels)
        return Channel(noise + self.pixels)

