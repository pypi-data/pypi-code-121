import numpy as np
import typing

from skimage import measure, morphology, feature, transform
from scipy.ndimage import label, sum
import scipy.ndimage as ndimage
from .DCCExceptions import *
import cv2 as cv

import matplotlib.pyplot as plt
import json

try:
    from deprecated import deprecated
except:
    exit("need 'deprecated' module: pip install deprecated")


class Channel:

    def __new__(cls, pixels: np.ndarray):
        if cls is Channel:
            if "float" in str(pixels.dtype):
                return super(Channel, cls).__new__(ChannelFloat)
            elif "int" in str(pixels.dtype) or "bool" in str(pixels.dtype):
                return super(Channel, cls).__new__(ChannelInt)
            else:
                raise PixelTypeException("Can't read images of type {}".format(pixels.dtype))

    def __init__(self, pixels: np.ndarray):
        """
        Creates a Channel object from an array of pixels.
        :param pixels: Numpy array of integers or floats. Must be in the shape (X, Y), width x height
        """
        pixels.squeeze()  # in case the array is nested in useless dimensions
        if pixels.ndim != 2:
            raise DimensionException(pixels.ndim)
        self._pixels = np.copy(pixels)
        self._originalDType = pixels.dtype
        self.__original = None

        # Segmentation @properties
        self.mask = None  # type: Channel
        self.labelledComponents = None
        self.numberOfComponents = 0
        self.componentsProperties = None

    def __str__(self) -> str:
        return str(self.pixels)

    def __repr__(self) -> str:
        return self.__str__()

    def __sub__(self, other):
        if isinstance(other, Channel):
            substraction = self.pixels - other.pixels
        else:
            substraction = self.pixels - other
        return Channel(pixels=substraction)

    def __add__(self, other):
        if isinstance(other, Channel):
            addition = self.pixels + other.pixels
        else:
            addition = self.pixels + other
        return Channel(pixels=addition)

    @property
    def pixels(self) -> np.ndarray:
        return self._pixels

    @property
    def dimension(self) -> int:
        return self.pixels.ndim

    @property
    def shape(self) -> typing.Tuple[int, int]:
        return self.pixels.shape

    @property
    def width(self) -> int:
        return int(self.shape[0])

    @property
    def height(self) -> int:
        return int(self.shape[1])

    @property
    def sizeInBytes(self) -> int:
        return self.pixels.nbytes

    @property
    def numberOfPixels(self) -> int:
        return self.width * self.height

    def __eq__(self, other) -> bool:
        if not isinstance(other, Channel):
            return False
        return np.array_equal(self.pixels, other.pixels)

    def copy(self):
        return Channel(np.copy(self.pixels))

    @property
    def isBinary(self) -> bool:
        return np.array_equal(self.pixels, self.pixels.astype(bool))

    @property
    def hasMask(self) -> bool:
        if self.mask is not None:
            return self.mask.isBinary
        return False

    """ Display-related functions """

    def display(self, colorMap=None):
        plt.imshow(self.pixels.copy().T, cmap=colorMap)
        plt.show()
        return self

    def getHistogramValues(self, normed: bool = False) -> typing.Tuple[np.ndarray, np.ndarray]:
        pass

    def displayHistogram(self, normed: bool = False) -> typing.Tuple[np.ndarray, np.ndarray]:
        histogram, bins = self.getHistogramValues(normed)
        plt.bar(bins[:-1], histogram, width=np.diff(bins), ec="k", align="edge", color="black", alpha=0.5)
        plt.show()
        return histogram, bins

    """ High-level Image segmentation functions """

    @property
    def hasLabelledComponents(self) -> bool:
        return self.labelledComponents is not None

    def labelMaskComponents(self):
        if self.hasMask:
            labels, nbObjects = ndimage.label(self.mask.pixels)
            self.labelledComponents = labels
            self.numberOfComponents = nbObjects
        else:
            # FIXME: Should use pixels if isBinary ?
            raise Exception("Channel has no mask")

    def setLabelledComponents(self, label: typing.Union[np.ndarray, str]):
        if type(label) is str:
            self.labelledComponents = label
        elif label.shape == self.shape:
            self.labelledComponents = label
        else:
            raise Exception("Label and Channel shapes are not equal")

    def analyzeComponents(self) -> dict:
        if self.hasLabelledComponents:
            maskSizes = ndimage.sum(self.mask.pixels, self.labelledComponents, range(1, self.numberOfComponents + 1))
            sumValues = ndimage.sum(self.pixels, self.labelledComponents, range(1, self.numberOfComponents + 1))
            centersOfMass = ndimage.center_of_mass(self.pixels, self.labelledComponents,
                                                   range(1, self.numberOfComponents + 1))
            # centerOfMass = np.average(self.params["objectsCM"], axis=0, weights=self.params["objectsMass"])
            properties = dict()
            properties["objectsSize"] = maskSizes
            # properties["totalSize"] = np.sum(self.params["objectsSize"])
            # properties["objectsMass"] = self.__getObjectsMass()
            # properties["totalMass"] = np.sum(self.params["objectsMass"])
            properties["objectsCM"] = centersOfMass
            # properties["totalCM"] = self.__getCenterOfMass()
            self.componentsProperties = properties
            return properties
        else:
            raise ValueError("Channel has not been labelled")

    def saveComponentsStatistics(self, filePath: str):
        properties = self.analyzeComponents()
        jsonParams = json.dumps(properties, indent=4)
        if filePath.split(".")[-1] != "json":
            filePath += ".json"

        with open(filePath, "w+") as file:
            file.write(jsonParams)

    """ Manipulation-related functions """

    def convertToNormalizedFloat(self):
        pass

    def convertToNormalizedFloatMinToZeroMaxToOne(self) -> "Channel":
        newChannelPixels = np.copy(self.pixels) - self.getExtrema()[0]  # We put the min to 0
        newChannelPixels = newChannelPixels / np.nanmax(newChannelPixels)  # We put the maximum to 1
        return Channel(newChannelPixels)

    def filterNoise(self):
        self.applyNoiseFilter()

    def threshold(self, value=None):
        if value is not None:
            self.applyGlobalThresholding(value)
        else:
            self.applyThresholding()

    def setMask(self, mask):
        if mask.isBinary:
            self.mask = mask
        else:
            raise NotImplementedError("Mask must be binary")

    def setMaskFromThreshold(self, value=None):
        if value is not None:
            binaryMask = self.pixels > value
            self.mask = Channel(pixels=binaryMask)
        else:
            raise NotImplementedError("Mask requires a value for thresholding")

    def saveOriginal(self) -> None:
        if self.__original is None:
            self.__original = np.copy(self.pixels)

    def restoreOriginal(self) -> None:
        if self.__original is not None:
            self._pixels = self.__original

    @property
    def originalPixels(self) -> np.ndarray:
        if self.__original is not None:
            return self.__original

    @property
    def hasOriginal(self) -> bool:
        if self.__original is not None:
            return True
        return False

    def replaceFromArray(self, channelArray):
        assert channelArray.ndim == 2
        self.saveOriginal()
        self._pixels = channelArray

    def applyConvolution(self, matrix: typing.Union[np.ndarray, list]) -> None:
        self.saveOriginal()
        result = self.convolveWith(matrix)
        self._pixels = result.pixels

    def applyXDerivative(self) -> None:
        self.saveOriginal()
        result = self.getXAxisDerivative()
        self._pixels = result.pixels

    def applyYDerivative(self) -> None:
        self.saveOriginal()
        result = self.getYAxisDerivative()
        self._pixels = result.pixels

    def applyGaussianFilter(self, sigma: float) -> None:
        self.saveOriginal()
        result = self.getGaussianFilter(sigma)
        self._pixels = result.pixels

    def applyThresholding(self, value=None) -> None:
        if value is None:
            self.applyIsodataThresholding()
        else:
            self.applyGlobalThresholding(value)

    def applyGlobalThresholding(self, value) -> None:
        self.saveOriginal()
        result = self.getGlobalThresholding(value)
        self._pixels = result.pixels

    def applyIsodataThresholding(self) -> None:
        self.saveOriginal()
        result = self.getIsodataThresholding()
        self._pixels = result.pixels

    def applyOtsuThresholding(self) -> None:
        self.saveOriginal()
        result = self.getOtsuThresholding()
        self._pixels = result.pixels

    def applyOpening(self, size: int) -> None:
        self.saveOriginal()
        if self.isBinary:
            result = self.getBinaryOpening(size)
        else:
            result = self.getOpening(size)
        self._pixels = result.pixels

    def applyClosing(self, size: int) -> None:
        self.saveOriginal()
        if self.isBinary:
            result = self.getBinaryClosing(size)
        else:
            result = self.getClosing(size)
        self._pixels = result.pixels

    def applyNdImageBinaryOpening(self, size: int = None, iterations: int = 1):
        # fixme: mask.applyOpening already exist: but ndimage method differs from morphology
        self.saveOriginal()
        if not self.isBinary:
            raise TypeError("Channel has to be binary")
        struct = None
        if size is not None:
            struct = np.ones((size, size))
        self._pixels = ndimage.binary_opening(self.pixels, struct, iterations=iterations)

    def applyNdImageBinaryClosing(self, size: int = None, iterations: int = 1):
        self.saveOriginal()
        if not self.isBinary:
            raise TypeError("Channel has to be binary")
        struct = None
        if size is not None:
            struct = np.ones((size, size))
        self._pixels = ndimage.binary_closing(self.pixels, struct, iterations=iterations)

    def applyErosion(self, size: int = 2):
        self.saveOriginal()
        result = self.getErosion(size)
        self._pixels = result.pixels

    def applyDilation(self, size: int = 2):
        self.saveOriginal()
        result = self.getDilation(size)
        self._pixels = result.pixels

    def applyNoiseFilter(self, algorithm=None):
        self.saveOriginal()
        result = self.getNoiseFiltering(algorithm)
        self._pixels = result.pixels

    def applyNoiseFilterWithErosionDilation(self, erosion_size=2, dilation_size=2, closing_size=2):
        self.saveOriginal()
        result = self.getNoiseFilteringWithErosionDilation(erosion_size, dilation_size, closing_size)
        self._pixels = result.pixels

    def convolveWith(self, matrix: typing.Union[np.ndarray, list]):
        pass

    def getXAxisDerivative(self):
        dxFilter = [[-1, 0, 1]]
        return self.convolveWith(dxFilter)

    def getYAxisDerivative(self):
        dyFilter = [[-1], [0], [1]]
        return self.convolveWith(dyFilter)

    def getAverageValueOfPixels(self) -> float:
        return np.average(self.pixels)

    def getStandardDeviation(self) -> float:
        return np.std(self.pixels)

    def getShannonEntropy(self, base=2) -> float:
        _, counts = np.unique(self.pixels, return_counts=True)
        probArray = counts / np.sum(counts)
        logArray = np.log(probArray) / np.log(base)
        entropy = -np.sum(probArray * logArray)
        return entropy

    def getExtrema(self) -> typing.Tuple[typing.Union[int, float], typing.Union[int, float]]:
        return np.min(self.pixels), np.max(self.pixels)

    def getMedian(self):
        median = np.median(self.pixels)
        return median

    def getPixelsOfIntensity(self, intensity: float) -> typing.List[tuple]:
        coordsList = []
        array = self.pixels
        coordsTemp = np.where(array[:, :] == intensity)
        coords = list(zip(coordsTemp[0], coordsTemp[1])) if len(coordsTemp[0]) != 0 else None
        coordsList.append(coords)
        coordsList = coordsList[0]
        return coordsList

    def getMinimum(self) -> typing.List[typing.Tuple[int, int]]:
        minimum = self.getExtrema()[0]
        return self.getPixelsOfIntensity(minimum)

    def getMaximum(self) -> typing.List[tuple]:
        maximum = self.getExtrema()[1]
        return self.getPixelsOfIntensity(maximum)

    def getEntropyFilter(self, filterSize: int):
        pass

    def getStandardDeviationFilter(self, filterSize: int):
        pass

    def getGaussianFilter(self, sigma: float = 1):
        pass

    def getHorizontalSobelFilter(self):
        pass

    def getVerticalSobelFilter(self):
        pass

    def getSobelFilter(self):
        pass

    def normalizeWithGaussianFilter(self, sigma: float):
        gaussFilter = self.getGaussianFilter(sigma)
        mean = self.getAverageValueOfPixels()
        norm = self.pixels / gaussFilter.pixels - mean
        return Channel(norm)

    def getCannyEdgeDetection(self, gaussianStdDev: float = 1, lowerThreshold: float = None,
                              higherThreshold: float = None):
        canny = feature.canny(self.pixels, gaussianStdDev, lowerThreshold, higherThreshold)
        return Channel(canny)

    def getGlobalThresholding(self, value):
        mask = self.pixels > value
        return Channel(mask)

    def getIsodataThresholding(self):
        pass

    def getOtsuThresholding(self):
        pass

    def getAdaptiveThresholdMean(self, oddRegionSize: int = 3):
        pass

    def getAdaptiveThresholdGaussian(self, oddRegionSize: int = 3):
        pass

    def getOpening(self, windowSize: int = 3):
        opened = morphology.opening(self.pixels, np.ones((windowSize, windowSize)))
        return Channel(opened)

    def getBinaryOpening(self, windowSize: int = 3):
        if not self.isBinary:
            raise NotBinaryImageException
        binaryOpened = morphology.binary_opening(self.pixels, np.ones((windowSize, windowSize))).astype(
            self._originalDType)
        return Channel(binaryOpened)

    def getClosing(self, windowSize: int = 3):
        closed = morphology.closing(self.pixels, np.ones((windowSize, windowSize)))
        return Channel(closed)

    def getBinaryClosing(self, windowSize: int = 3):
        if not self.isBinary:
            raise NotBinaryImageException
        binarClosed = morphology.binary_closing(self.pixels, np.ones((windowSize, windowSize))).astype(
            self._originalDType)
        return Channel(binarClosed)

    def getErosion(self, size: int = 2):
        return Channel(ndimage.grey_erosion(self.pixels, size=size))

    def getDilation(self, size: int = 2):
        return Channel(ndimage.grey_dilation(self.pixels, size=size))

    def getNoiseFiltering(self, algorithm=None):
        return self.getNoiseFilteringWithErosionDilation()

    def getNoiseFilteringWithErosionDilation(self, erosion_size=2, dilation_size=2, closing_size=2):
        workingChannel = self.getErosion(erosion_size)
        workingChannel.applyDilation(dilation_size)
        workingChannel.applyClosing(closing_size)
        return workingChannel

    def getConnectedComponents(self, connectionStructure: np.ndarray = None) -> tuple:
        if not self.isBinary:
            raise NotBinaryImageException
        labeled, nbObjects = label(self.pixels, structure=connectionStructure)
        sizes = sum(self.pixels, labeled, range(nbObjects + 1))
        return Channel(labeled), nbObjects, sizes

    def getDistanceTransform(self, returnIndices: bool = False) -> np.ndarray:
        if not self.isBinary:
            raise NotBinaryImageException
        distanceTransform = ndimage.distance_transform_edt(self.pixels, return_indices=returnIndices)
        return distanceTransform

    def watershedSegmentation(self, gaussianFilterStdDev: float = 1.2, localPeaksMinDistance: int = 5,
                              use4Connectivity: bool = True) -> typing.Tuple["Channel", int]:
        ccKernel = None
        if not use4Connectivity:
            ccKernel = np.ones((3, 3))
        # First, we apply a gaussian filter in order to remove some noise in the channel and smooth it.
        gaussianFilter = self.getGaussianFilter(gaussianFilterStdDev)
        # We can now threshold the filtered channel in order to have a binary channel.
        gaussianBin = gaussianFilter.getOtsuThresholding()
        # Compute the distances between each pixels and its nearest 0 value pixel.
        distanceTransform = gaussianBin.getDistanceTransform()
        # We then find the local max of the distance transform array
        localMax = feature.peak_local_max(distanceTransform, indices=False, min_distance=localPeaksMinDistance,
                                          labels=gaussianBin.pixels)
        # Let's get the markers of the connected components
        markers = Channel(localMax).getConnectedComponents(connectionStructure=ccKernel)[0].pixels
        # Find labels of the different object in the image
        labels = morphology.watershed(-distanceTransform, markers, mask=gaussianBin.pixels)
        uniqueLabels = np.unique(labels)
        allMask = np.zeros(self.shape, dtype=np.uint8)
        for label in uniqueLabels:
            if label == 0:
                # label = 0 means background
                continue

            mask = np.zeros(self.shape, dtype=np.uint16)
            mask[labels == label] = 255
            allMask[labels == label] = label

        masks = Channel(allMask)
        return masks, len(uniqueLabels) - 1

    def dotsLikeStructureSegmentation(self, spotFilterScales: list, spotFilterCutoffs: list,
                                      watershedMinDistanceOfPeaks: int = 5) -> typing.Tuple["Channel", int]:
        try:
            from aicssegmentation.core.seg_dot import dot_3d_wrapper
        except:
            raise NotImplementedError("dot_3d_wrapper not implemented. Must import aicssegmentation.")

        # To use when the image contains dot-like structures, like little round cells. Not too good with neurons tho
        if len(spotFilterScales) == 0 or len(spotFilterCutoffs) == 0:
            raise ValueError("The lists of parameters must have at least one element.")
        if len(spotFilterCutoffs) != len(spotFilterScales):
            raise ValueError("The lists of parameters must have the same number of elements.")
        normalizedChannel = self.intensityScaleNormalization()
        # FIXME Find a way to get a std deviation automatically (depending on noise)?
        smooth = normalizedChannel.getGaussianFilter(1)
        # FIXME Find a way to get params automatically?
        spotFilterParams = [[spotFilterScales[i], spotFilterCutoffs[i]] for i in range(len(spotFilterScales))]
        spotFiltered = Channel(dot_3d_wrapper(smooth.pixels, spotFilterParams).astype(np.uint8))
        watershed = spotFiltered.watershedSegmentation(0, watershedMinDistanceOfPeaks)
        return watershed

    def curviLinearLikeStructuresSegmentation(self, filamentFilterScales: list, filamentFilterCutoffs: list) -> [
        "Channel"]:
        try:
            from aicssegmentation.core.pre_processing_utils import edge_preserving_smoothing_3d
            from aicssegmentation.core.vessel import filament_2d_wrapper
        except:
            raise NotImplementedError("dot_3d_wrapper not implemented. Must import aicssegmentation.")

        if len(filamentFilterScales) == 0 or len(filamentFilterCutoffs) == 0:
            raise ValueError("The lists of parameters must have at least one element.")
        if len(filamentFilterCutoffs) != len(filamentFilterScales):
            raise ValueError("The lists of parameters must have the same number of elements.")
        normalizedChannel = self.intensityScaleNormalization()
        # For some reason, edge_preserving_smoothing_3d transposes the array. Can't access code deeper from itk
        smooth = edge_preserving_smoothing_3d(normalizedChannel.pixels)
        filamentFilterParameters = [[filamentFilterScales[i], filamentFilterCutoffs[i]] for i in
                                    range(len(filamentFilterScales))]
        filamentFiltered = filament_2d_wrapper(smooth, filamentFilterParameters)
        return Channel(filamentFiltered.astype(np.uint8))

    def intensityScaleNormalization(self, scaleParam: list = None) -> ["Channel"]:
        # Adapted from the Allen Institute segmentation module. This is from a method suggesting scale parameters
        # but it actually doesn't return them (just printing them on console).
        from aicssegmentation.core.pre_processing_utils import intensity_normalization
        normParam = scaleParam
        if scaleParam is not None and len(scaleParam) != 2:
            raise ValueError("The list of scale parameters must contain 2 values.")
        if normParam is None:
            percentile99 = np.percentile(self.pixels, 99.99)
            mean = self.getAverageValueOfPixels()
            stdDev = self.getStandardDeviation()
            maxRatio = 0
            for tempMaxRatio in np.arange(0.5, 1000, 0.5):
                if mean + stdDev * tempMaxRatio > percentile99:
                    if mean + stdDev * tempMaxRatio > self.getExtrema()[1]:
                        maxRatio = tempMaxRatio - 0.5
                    else:
                        maxRatio = tempMaxRatio
                    break
            minRatio = 0
            for tempMinRatio in np.arange(0.5, 1000, 0.5):
                if mean - stdDev * tempMinRatio < self.getExtrema()[0]:
                    minRatio = tempMinRatio - 0.5
                    break
            normParam = [minRatio, maxRatio]
            normalizedPixels = intensity_normalization(self.pixels, normParam)

            # This should not happen but just in case
            # FIXME find a better way (in Channel, ChannelFloat or ChannelInt init?) to have only positive values
            if np.min(normalizedPixels) < 0 or np.max(normalizedPixels):
                normalizedPixels = np.clip(normalizedPixels, 0, 1)
            return Channel(normalizedPixels)

    def blobDetection(self, minStdDev: float = 1, maxStdDev: float = 50, threshold: float = 0.2,
                      overlap: float = 0.5) -> typing.Tuple["Channel", int]:
        # Not good with low contrast images
        blobs = feature.blob_log(self.pixels, maxStdDev, minStdDev, threshold=threshold, overlap=overlap)
        blobsDetected = Channel(np.zeros((self.width, self.height)))
        # Compute radii
        blobs[:, 2] = blobs[:, 2] * 2 ** 0.5
        numberOfBlobs = 0
        for blob in blobs:
            y, x, r = blob
            cv.circle(blobsDetected.pixels, (int(x), int(y)), int(r), 1, 2)
            numberOfBlobs += 1
        self.multiChannelDisplay([self, blobsDetected])
        return blobsDetected, numberOfBlobs

    def houghTransform(self, thresholdValue: int = 10, minLineLength: int = 50, maxLineGap: int = 10) -> typing.Tuple[
        "Channel", int]:
        # Uses Probabilistic Hough Transform algorithm
        edges = self.getCannyEdgeDetection()
        lines = transform.probabilistic_hough_line(edges.pixels, thresholdValue, minLineLength, maxLineGap)
        houghLines = Channel(np.zeros((self.width, self.height)))
        for line in lines:
            cv.line(houghLines.pixels, line[0], line[1], 1, 2)
        self.multiChannelDisplay([self, houghLines])
        return houghLines, len(lines)

    def convertTo16BitsUnsignedInteger(self):
        pass

    def convertTo8BitsUnsignedInteger(self):
        pass

    def _convertToUnsignedInt(self, dtype):
        pass

    @staticmethod
    def multiChannelDisplay(channels: list, colorMaps: list = None) -> list:
        if colorMaps is not None and len(channels) != len(colorMaps) and len(colorMaps) != 1:
            raise ValueError(
                "'channels' and 'colorMaps' must have the same length or 'colorMaps' must have a single element.")

        nrows = int(np.ceil(len(channels) / 4))
        ncols = len(channels) if len(channels) < 4 else 4
        for i in range(len(channels)):
            plt.subplot(nrows, ncols, i + 1)
            colorMap = None
            if colorMaps is not None:
                colorMap = colorMaps[i % len(colorMaps)]
            plt.imshow(channels[i].pixels.T, cmap=colorMap)
        plt.show()
        return channels

    ### Spectral analysis methods ###
    def applyHighPassFilterFromRectangularMask(self, filterSize: int):
        fftShiftPixels = self.fourierTransform()
        XY = self.createXYGridsFromArray(fftShiftPixels)
        mask = 1 - self.createRectangularMask(XY, filterSize)
        fftShiftPixelsWithMask = fftShiftPixels * mask
        ifftShift = np.fft.ifftshift(fftShiftPixelsWithMask)
        filteredPixels = np.abs(np.fft.ifft2(ifftShift))
        return Channel(filteredPixels)

    def applyLowPassFilterFromRectangularMask(self, filterSize: int):
        fftShiftPixels = self.fourierTransform()
        XY = self.createXYGridsFromArray(fftShiftPixels)
        mask = self.createRectangularMask(XY, filterSize)
        fftShiftPixelsWithMask = fftShiftPixels * mask
        ifftShift = np.fft.ifftshift(fftShiftPixelsWithMask)
        filteredPixels = np.abs(np.fft.ifft2(ifftShift))
        return Channel(filteredPixels)

    def applyBandpassFilterFromRectangularMask(self, cutIn: int, cutOff: int):
        fftShiftPixels = self.fourierTransform()
        XY = self.createXYGridsFromArray(fftShiftPixels)
        lowPassMask = self.createRectangularMask(XY, cutIn)
        highPassMask = 1 - self.createRectangularMask(XY, cutOff)
        bandpass = 1 - (lowPassMask + highPassMask)
        fftFiltered = fftShiftPixels * bandpass
        ifftShift = np.fft.ifftshift(fftFiltered)
        filteredPixels = np.abs(np.fft.ifft2(ifftShift))
        return Channel(filteredPixels)

    def applyLowPassFilterFromGaussianMask(self, FWHM: float):
        fftPixels = self.fourierTransform(True)
        x, y = self.createXYGridsFromArray(fftPixels)
        sigma = FWHM / (2 * np.sqrt(2 * np.log(2)))
        gauss = self.createGaussianMask((x, y), sigma)
        fftFiltered = fftPixels * gauss
        ifftShift = np.fft.ifftshift(fftFiltered)
        filteredPixels = np.abs(np.fft.ifft2(ifftShift))
        return Channel(filteredPixels)

    def applyHighPassFilterFromGaussianMask(self, FWHM: float):
        fftPixels = self.fourierTransform()
        x, y = self.createXYGridsFromArray(fftPixels)
        sigma = FWHM / (2 * np.sqrt(2 * np.log(2)))
        gauss = 1 - self.createGaussianMask((x, y), sigma)
        fftFiltered = fftPixels * gauss
        ifftShift = np.fft.ifftshift(fftFiltered)
        filteredPixels = np.abs(np.fft.ifft2(ifftShift))
        return Channel(filteredPixels)

    def applyBandpassFilterFromGaussianMask(self, parameter):
        # todo
        pass

    def applyLowPassFilterFromSigmoidMask(self, topRadius: float, inflectionPointSlope: float = 1 / 4):
        fftPixels = self.fourierTransform()
        x, y = self.createXYGridsFromArray(fftPixels)
        sigmoid = self.createSigmoidMask((x, y), topRadius, inflectionPointSlope)
        fftFiltered = fftPixels * sigmoid
        ifftShift = np.fft.ifftshift(fftFiltered)
        filteredPixels = np.abs(np.fft.ifft2(ifftShift))
        return Channel(filteredPixels)

    def applyHighPassFilterFromSigmoidMask(self, bottomRadius: float, inflectionPointSlope: float = 1 / 4):
        fftPixels = self.fourierTransform()
        x, y = self.createXYGridsFromArray(fftPixels)
        sigmoid = 1 - self.createSigmoidMask((x, y), bottomRadius, inflectionPointSlope)
        fftFiltered = fftPixels * sigmoid
        ifftShift = np.fft.ifftshift(fftFiltered)
        filteredPixels = np.abs(np.fft.ifft2(ifftShift))
        return Channel(filteredPixels)

    def applyBandpassFilterFromSigmoidMask(self, cutIn: int, cutOff: int, inflectionPointSlope: float = 1 / 4):
        fftPixels = self.fourierTransform()
        XY = self.createXYGridsFromArray(fftPixels)
        lowPass = self.createSigmoidMask(XY, cutIn, inflectionPointSlope)
        highPass = 1 - self.createSigmoidMask(XY, cutOff, inflectionPointSlope)
        bandpass = 1 - (lowPass + highPass)
        fftFiltered = fftPixels * bandpass
        ifftShift = np.fft.ifftshift(fftFiltered)
        filteredPixels = np.abs(np.fft.ifft2(ifftShift))
        return Channel(filteredPixels)

    def applyLowPassFilterFromCircularMask(self, radius: float):
        fftPixels = self.fourierTransform()
        XY = self.createXYGridsFromArray(fftPixels)
        mask = self.createCircularMask(XY, radius)
        fftFiltered = fftPixels * mask
        ifftShift = np.fft.ifftshift(fftFiltered)
        filteredPixels = np.abs(np.fft.ifft2(ifftShift))
        return Channel(filteredPixels)

    def applyHighPassFilterFromCircularMask(self, radius: float):
        fftPixels = self.fourierTransform()
        XY = self.createXYGridsFromArray(fftPixels)
        mask = 1 - self.createCircularMask(XY, radius)
        fftFiltered = fftPixels * mask
        ifftShift = np.fft.ifftshift(fftFiltered)
        filteredPixels = np.abs(np.fft.ifft2(ifftShift))
        return Channel(filteredPixels)

    def applyBandpassFilterFromCircularMask(self, cutIn: float, cutOff: float):
        fftPixels = self.fourierTransform()
        x, y = self.createXYGridsFromArray(fftPixels)
        mask = ((x ** 2 + y ** 2) ** (1 / 2) - cutIn) ** 2 <= cutOff ** 2
        fftFiltered = fftPixels * mask.astype(np.uint8)
        ifftShift = np.fft.ifftshift(fftFiltered)
        filteredPixels = np.abs(np.fft.ifft2(ifftShift))
        return Channel(filteredPixels)

    def powerSpectrum(self) -> np.ndarray:
        fftShiftPixels = self.fourierTransform()
        powerSpectrum = (np.abs(fftShiftPixels)) ** 2
        powerSpectrum /= np.sum(powerSpectrum)
        return powerSpectrum

    def displayPowerSpectrum(self, logScale: bool = True) -> np.ndarray:
        powerSpectrum = self.powerSpectrum()
        cols, rows = powerSpectrum.shape
        if logScale:
            powerSpectrum = np.log(powerSpectrum)
        plt.imshow(powerSpectrum.T, extent=(-cols // 2, cols // 2, -rows // 2, rows // 2))
        plt.colorbar()
        plt.show()
        return powerSpectrum

    def powerSpectrumAzimuthalAverage(self) -> np.ndarray:
        powerSpectrumDensity = self.powerSpectrum()
        ps1D = self.azimuthalAverage(powerSpectrumDensity.T)
        return ps1D

    def displayPowerSpectrumAzimuthalAverage(self, logBase: float = None) -> np.ndarray:
        ps1D = self.powerSpectrumAzimuthalAverage()
        x = range(len(ps1D))
        plt.plot(x, ps1D)
        if logBase is not None:
            plt.yscale("log", basey=logBase)
        plt.show()
        return ps1D

    def powerSpectrumAngularAverage(self, returnIndex: bool = False) -> typing.Union[
        np.ndarray, typing.Tuple[np.ndarray, np.ndarray]]:
        powerSpectrumDensity = self.powerSpectrum()
        psAngAvg, index = self.angularAverage(powerSpectrumDensity.T)
        returnValues = psAngAvg if not returnIndex else (psAngAvg, index)
        return returnValues

    def displayPowerSpectrumAngularAverage(self, logBase: float = None, useRadians: bool = False) -> np.ndarray:
        psAngAvg, index = self.powerSpectrumAngularAverage(True)
        x = index
        label = "degrees"
        if useRadians:
            x = x / 180 * np.pi
            label = "radians"
        plt.plot(x, psAngAvg)
        if logBase is not None:
            plt.yscale("log", basey=logBase)
        plt.xlabel("Angle [{}]".format(label))
        plt.show()
        return psAngAvg

    def fourierTransform(self, shift: bool = True) -> np.ndarray:
        pixels = self.pixels
        fftPixels = np.fft.fft2(pixels)
        if shift:
            fftPixels = np.fft.fftshift(fftPixels)
        return fftPixels

    def applyGaussianNoise(self, sigma: float, mean: float = 0):
        cols, rows = self.shape
        gauss = np.random.normal(mean, sigma, (rows, cols))
        gauss = np.clip(gauss.reshape(rows, cols), 0, np.max(gauss))
        noise = self.pixels + gauss.astype(self._originalDType)
        return Channel(noise)

    def applyPoissonNoise(self, scale: float):
        pass

    def phaseSpectrum(self, radians: bool = True) -> np.ndarray:
        fftPixels = self.fourierTransform()
        angles = np.angle(fftPixels, not radians)
        return angles

    def displayPhaseSpectrum(self, radians: bool = True) -> np.ndarray:
        phaseSpectrum = self.phaseSpectrum(radians)
        rows, cols = phaseSpectrum.shape
        plt.imshow(phaseSpectrum, extent=(-cols // 2, cols // 2, -rows // 2, rows // 2))
        plt.show()
        return phaseSpectrum

    @staticmethod
    def createXYGridsFromArray(array: np.ndarray, gridOriginAtCenter: bool = True) -> typing.Tuple[
        np.ndarray, np.ndarray]:
        shape = array.shape
        y, x = np.indices(shape)
        if gridOriginAtCenter:
            y, x = np.flipud(y - np.max(y) // 2), x - np.max(x) // 2
            if x.shape[1] % 2 == 0:
                x -= 1
        return x, y

    @staticmethod
    def createGaussianMask(XYGrids: typing.Tuple[np.ndarray, np.ndarray], sigma: float) -> np.ndarray:
        x, y = XYGrids
        gauss = np.exp(-(x ** 2 + y ** 2) / (2 * sigma ** 2))
        return gauss

    @staticmethod
    def createSigmoidMask(XYGrids: typing.Tuple[np.ndarray, np.ndarray], radius: float,
                          inflectionPointSlope: float = 1 / 4) -> np.ndarray:
        """
        Create a sigmoid mask with the same shape as the image to mask.
        :param XYGrids: Tuple with an array containing the x indices and another containing the y indices. The origin
        must be at the center of the arrays.
        Example:
        x : [[-1 0 1]
             [-1 0 1]
             [-1 0 1]]
        y : [[1 1 1]
             [0 0 0]
             [-1 -1 -1]]
        :param radius: Radius of the top of the sigmoid function
        :param inflectionPointSlope: The slope at the inflection point. The general sigmoid function is:
        S(x) = 1/(1 + exp(-lambda x)
        where lambda is proportional to the inflection slope (slope = lambda / 4).
        :return: Array of values in the range [0, 1] following a 2D centered sigmoid function
        """
        x, y = XYGrids
        expArg = -4 * inflectionPointSlope * (radius - np.sqrt(x ** 2 + y ** 2))
        # Overflow occuring when the xp arg is  >ln(1.7976931348623157e+308) which is a little bigger than 709
        expArg[expArg > 709] = 709
        sigmoid = 1 / (1 + np.exp(expArg))
        return sigmoid

    @staticmethod
    def createRectangularMask(XYGrids: typing.Tuple[np.ndarray, np.ndarray], size: int) -> np.ndarray:
        x, y = XYGrids
        demiSize1 = size // 2
        demiSize2 = demiSize1 if size % 2 == 0 else demiSize1 + 1
        maskX = ((x < 0) & (np.abs(x) < demiSize2)) | (~(x < 0) & (np.abs(x) <= demiSize1))
        maskY = ((y < 0) & (np.abs(y) < demiSize2)) | (~(y < 0) & (np.abs(y) <= demiSize1))
        mask = maskX & maskY
        return mask.astype(np.uint8)

    @staticmethod
    def createCircularMask(XYGrids: typing.Tuple[np.ndarray, np.ndarray], radius: float) -> np.ndarray:
        x, y = XYGrids
        mask = (x ** 2 + y ** 2 - radius ** 2) <= 0
        return mask.astype(np.uint8)

    @staticmethod
    def azimuthalAverage(array: np.ndarray) -> np.ndarray:
        """
        Computes the average value of the array for element with the same radius label.
        Example:
        array = [0,1,2]
                [2,2,3]
                [1,4,2]
        radiiLabel = [1,1,1]
                     [1,0,1]
                     [1,1,1]
        The average (depending on the radius value) is then computed. For this example, the average would be:
        avg = [2, 1.875] (2 for the mean of radius 0, 1.875 for the mean of radius 1)
        :param array: Array to use for the computation of the mean
        :return: An array containing the mean of each radius present (the index of the array represent the radius value)
        """
        x, y = Channel.createXYGridsFromArray(array)
        radii = ((x ** 2 + y ** 2) ** (1 / 2)).astype(int)
        # carre = np.maximum(np.abs(x), np.abs(y))
        index = np.unique(radii)
        average = ndimage.mean(array, radii, index=index)
        # averageSquare = ndimage.mean(array, x, index = np.unique(x))
        # averageSquare = averageSquare
        # plt.plot(range(len(averageSquare)), averageSquare)
        # plt.yscale("log", basey=2)
        # plt.show()
        return np.array(average) / np.sum(average)

    @staticmethod
    def angularAverage(array: np.ndarray) -> typing.Tuple[np.ndarray, np.ndarray]:
        x, y = Channel.createXYGridsFromArray(array)
        centerY = y.shape[0] // 2
        # We only take the 1st and 2nd quadrant because the 3rd and 4th are just a reflection.
        x, y = x[:centerY + 1, :], y[:centerY + 1, :]
        # The angle of a line starting from origin and passing through a pixel is given by arctan(y/x) where (x, y) are
        # the coordinates of each pixel.
        angleMask = np.round(np.arctan2(y, x) * 180 / np.pi).astype(int)
        upperPartArray = array[:centerY + 1, :]
        index = np.unique(angleMask)
        average = ndimage.mean(upperPartArray, angleMask, index=index)
        return np.array(average) / np.sum(average), index


from .channelFloat import ChannelFloat
from .channelInteger import ChannelInt
