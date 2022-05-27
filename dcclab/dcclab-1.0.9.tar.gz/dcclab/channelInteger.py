from skimage.filters.rank import entropy
from .channel import *
import cv2 as cv
import warnings



class ChannelInt(Channel):

    def __init__(self, pixels: np.ndarray):
        # FIXME: use bool directly?
        if "bool" in str(pixels.dtype):
            pixels = pixels.astype(int)

        if "int" not in str(pixels.dtype):
            raise TypeError("Pixel type must be integer.")
        if np.any(pixels < 0):
            # FIXME Better way to handle negative values (if we handle them at all)
            pixels = np.clip(pixels, 0, np.iinfo(self._originalDType).max)
        Channel.__init__(self, pixels)
        self._originalFactor = np.iinfo(self._originalDType).max

    def applyConvolution(self, matrix: typing.Union[np.ndarray, list]) -> None:
        self.saveOriginal()
        result = self.convolveWith(matrix)._convertToUnsignedInt(self._originalDType)
        self._pixels = result.pixels

    def applyGaussianFilter(self, sigma: float) -> None:
        self.saveOriginal()
        result = self.getGaussianFilter()._convertToUnsignedInt(self._originalDType)
        self._pixels = result.pixels

    def applyXDerivative(self) -> None:
        self.saveOriginal()
        result = self.getXAxisDerivative()._convertToUnsignedInt(self._originalDType)
        self._pixels = result.pixels

    def applyYDerivative(self) -> None:
        self.saveOriginal()
        result = self.getYAxisDerivative()._convertToUnsignedInt(self._originalDType)
        self._pixels = result.pixels

    def getHistogramValues(self, normed: bool = False) -> typing.Tuple[np.ndarray, np.ndarray]:
        array = self.pixels.ravel()
        nbBins = len(np.bincount(array))
        hist, bins = np.histogram(array, nbBins, [0, nbBins], density=normed)
        return hist, bins

    def convolveWith(self, matrix: typing.Union[np.ndarray, list]) -> Channel:
        floatChannel = self.convertToNormalizedFloat()
        return floatChannel.convolveWith(matrix)

    def getGaussianFilter(self, sigma: float = 1) -> Channel:
        floatChannel = self.convertToNormalizedFloat()
        return floatChannel.getGaussianFilter(sigma)

    def getEntropyFilter(self, filterSize: int) -> Channel:
        entropyFiltered = entropy(self.convertTo8BitsUnsignedInteger().pixels, morphology.selem.square(filterSize))
        return Channel(entropyFiltered)

    def getStandardDeviationFilter(self, filterSize: int) -> Channel:
        floatChannel = self.convertToNormalizedFloat()
        return floatChannel.getStandardDeviationFilter(filterSize)

    def getHorizontalSobelFilter(self) -> Channel:
        floatChannel = self.convertToNormalizedFloat()
        return floatChannel.getHorizontalSobelFilter()

    def getVerticalSobelFilter(self) -> Channel:
        floatChannel = self.convertToNormalizedFloat()
        return floatChannel.getVerticalSobelFilter()

    def getSobelFilter(self) -> Channel:
        floatChannel = self.convertToNormalizedFloat()
        return floatChannel.getSobelFilter()

    def getIsodataThresholding(self) -> Channel:
        """
        Adapted from skimage's isodata thresholding method.
        Their version was not behaving properly with data different than uint8.
        :return: The thresholded Channel instance according to isodata method.
        """
        warnings.catch_warnings()
        warnings.simplefilter("ignore", category=RuntimeWarning)
        hist, bins = self.getHistogramValues()

        hist = np.array(hist, dtype=np.float32)
        bins = np.array(bins)
        binsCenters = np.array([(i + i + 1) / 2 for i in range(len(bins) - 1)])
        pixelProbabilityThresholdOne = np.cumsum(hist)
        pixelProbabilityThresholdTwo = np.cumsum(hist[::-1])[::-1] - hist
        intensitySum = hist * binsCenters
        pixelProbabilityThresholdTwo[-1] = 1
        low = np.cumsum(intensitySum) / pixelProbabilityThresholdOne
        high = (np.cumsum(intensitySum[::-1])[::-1] - intensitySum) / pixelProbabilityThresholdTwo
        allMean = (low + high) / 2
        binWidth = binsCenters[1] - binsCenters[0]
        distances = allMean - binsCenters
        thresh = 0
        for i in range(len(distances)):
            if distances[i] is not None and 0 <= distances[i] < binWidth:
                thresh = binsCenters[i]
        threshArray = self.pixels >= thresh
        return Channel(threshArray)

    def getOtsuThresholding(self) -> Channel:
        """
        Adapted from skimage's Otsu thresholding method.
        Their version was not behaving properly with data different than uint8.
        :return: The thresholded DCCImage instance according to Otsu's method.
        """
        warnings.catch_warnings()
        warnings.simplefilter("ignore", category=RuntimeWarning)
        if self.getExtrema()[0] == self.getExtrema()[1]:
            raise ValueError(
                "This method only works for image with more than one \"color\" (i.e. more than one pixel value).")
        hist, bins = self.getHistogramValues()
        hist = np.array(hist, dtype=np.float32)
        bins = np.array(bins)
        binsCenters = np.array([(i + i + 1) / 2 for i in range(len(bins) - 1)])
        pixelProbabilityGroupOne = np.cumsum(hist)
        pixelProbabilityGroupTwo = np.cumsum(hist[::-1])[::-1]
        pixelIntensityGroupOneMean = np.cumsum(hist * binsCenters) / pixelProbabilityGroupOne
        pixelIntensityGroupTwoMean = (np.cumsum((hist * binsCenters)[::-1]) / pixelProbabilityGroupTwo[::-1])[::-1]
        varianceTwoGroups = pixelProbabilityGroupOne[:-1] * pixelProbabilityGroupTwo[1:] * (
                pixelIntensityGroupOneMean[:-1] - pixelIntensityGroupTwoMean[1:]) ** 2
        index = np.nanargmax(varianceTwoGroups)
        thresh = binsCenters[index]
        threshArray = self.pixels >= thresh
        return Channel(threshArray.astype(np.uint8))

    def getAdaptiveThresholdMean(self, oddRegionSize: int = 3) -> Channel:
        threshArray = cv.adaptiveThreshold(self.convertTo8BitsUnsignedInteger().pixels, 1, cv.ADAPTIVE_THRESH_MEAN_C,
                                           cv.THRESH_BINARY,
                                           oddRegionSize, 0)
        return Channel(threshArray.astype(np.uint8))

    def getAdaptiveThresholdGaussian(self, oddRegionSize: int = 3) -> Channel:
        threshArray = cv.adaptiveThreshold(self.convertTo8BitsUnsignedInteger().pixels, 1,
                                           cv.ADAPTIVE_THRESH_GAUSSIAN_C,
                                           cv.THRESH_BINARY, oddRegionSize, 0)
        return Channel(threshArray)

    def convertTo8BitsUnsignedInteger(self) -> Channel:
        return self._convertToUnsignedInt(np.uint8)

    def convertTo16BitsUnsignedInteger(self) -> Channel:
        return self._convertToUnsignedInt(np.uint16)

    def convertToNormalizedFloat(self) -> Channel:
        return Channel(np.copy(self.pixels) / self._originalFactor)


    def _convertToUnsignedInt(self, dtype) -> Channel:
        convertedArray = np.copy(self.pixels) / self._originalFactor * np.iinfo(dtype).max
        return Channel(convertedArray.astype(dtype))

    def applyPoissonNoise(self, scale: float):
        return self.convertToNormalizedFloat().applyPoissonNoise(scale)
