import env
from dcclab import *
import unittest
import numpy as np
from unittest.mock import Mock, patch
import warnings


class TestImageConstructor(unittest.TestCase):

    def testValidConstructor(self):
        array = np.ones((1250, 1500, 3), dtype=np.float32)
        image = Image(imageData=array)
        self.assertIsInstance(image, Image)

    def testInvalidDimensionsConstructor(self):
        with self.assertRaises(DimensionException):
            Image(np.zeros(12, dtype=np.float32))

    def testInvalidTypeConstructor(self):
        with self.assertRaises(PixelTypeException):
            Image(np.ones((1250, 1500, 3), dtype=np.complex))


class TestImageMethods(unittest.TestCase):

    def setUp(self) -> None:
        self.array = np.ones((1250, 1251), dtype=np.float32) * 25.56
        self.array[100][100] = 100.0
        self.array[0][0] = 0.0
        self.image = Image(imageData=self.array)

    def testEquals(self):
        testArray = np.copy(self.array)
        testImage = Image(imageData=testArray)
        testImage2 = Image(imageData=testArray)
        self.assertTrue(testImage == testImage2)

    def testNotEquals(self):
        testArray = np.copy(self.array)
        testArray[0][0] = 0.0001
        testImage = Image(imageData=testArray)
        self.assertFalse(testImage == self.image)

    def testInvalidEquality(self):
        testArray = np.copy(self.array)
        with self.assertRaises(InvalidEqualityTestException):
            self.image == testArray

    def testGetImageAsNumpyArray(self):
        testArray = np.copy(self.array)
        getArray = self.image.getArray()
        equality = np.array_equal(testArray, getArray)
        self.assertTrue(equality)

    def testImageIsImageGrayFalse(self):
        array = np.zeros((10, 10, 3), dtype=np.float32)
        image = Image(array)
        self.assertFalse(image.isImageInGray())

    def testImageIsImageInGrayTrue(self):
        self.assertTrue(self.image.isImageInGray())

    def testImageIsImageBinaryFalse(self):
        self.assertFalse(self.image.isImageInBinary())

    def testImageIsImageBinaryFalse3Channels(self):
        array = np.ones((10, 10, 3), dtype=np.float32)
        image = Image(array)
        self.assertFalse(image.isImageInBinary())

    def testImageIsImageBinaryFalseFloatValues(self):
        array = np.ones((1000, 1000), dtype=np.float32)
        array[10][674] = 0.001
        image = Image(array)
        self.assertFalse(image.isImageInBinary())

    def testImageIsImageInBinaryTrue(self):
        array = np.ones((1000, 1000), dtype=np.float32)
        image = Image(array)
        self.assertTrue(image.isImageInBinary())

    def testImageSeparatedChannelsGray(self):
        with self.assertRaises(DimensionException):
            self.image.splitChannels()

    def testImageSeparatedChannels(self):
        array = np.ones((1000, 1000, 3), dtype=np.float32)
        array[:, :, 0] = 100.25
        array[:, :, 1] = 205.78
        array[:, :, 2] = 137.96
        splitterList = [array[:, :, 0], array[:, :, 1], array[:, :, 2]]
        image = Image(array)
        self.assertTrue(np.array_equal(np.array(image.splitChannels()), np.array(splitterList)))

    def testImageStringRepresentation(self):
        self.assertTrue(np.array_equal(str(self.image), str(self.image.getArray())))

    def testGetImageWidth(self):
        width = 1250
        self.assertEqual(self.image.getWidth(), width)

    def testGetImageLength(self):
        length = 1251
        self.assertEqual(self.image.getLength(), length)

    def testGetImageChannels(self):
        nbChannel = 1
        self.assertEqual(self.image.getNumberOfChannel(), nbChannel)

    def testGetImageChannels3Channels(self):
        nbChannels = 3
        tempArray = np.zeros((1250, 1800, 3), dtype=np.float32)
        tempImage = Image(tempArray)
        self.assertEqual(tempImage.getNumberOfChannel(), nbChannels)

    def testGetNumberOFPixels(self):
        nbPixels = 1563750
        self.assertEqual(self.image.getNumberOfPixels(), nbPixels)

    def testToPILImage(self):
        import PIL.Image
        pilImage = PIL.Image.fromarray(np.copy(self.array))
        getPilImage = self.image.toPILImage()
        self.assertTrue(pilImage == getPilImage)

    def testCopyImage(self):
        imageCopy = self.image.copyImage()
        self.assertIsInstance(imageCopy, Image)

    def testCopyImageEquality(self):
        imageCopy = self.image.copyImage()
        self.assertTrue(self.image == imageCopy)

    def testModifiedCopy(self):
        imageCopy = self.image.copyImage()
        arrayCopy = imageCopy.getArray()
        arrayCopy[100][79] = 1.2
        imageNotCopy = Image(arrayCopy)
        self.assertFalse(self.image == imageNotCopy)

    @patch("matplotlib.pyplot.show", new=Mock)
    def testShowImage(self):
        imageReturn = self.image.showImage()
        self.assertIsInstance(imageReturn, Image)

    def testSaveToTIFFInvalidEmptyName(self):
        name = ""
        with self.assertRaises(InvalidImageNameException):
            self.image.saveToTIFF(name)

    def testSaveToTIFFInvalidCharacterName(self):
        name = "test?"
        with self.assertRaises(InvalidImageNameException):
            self.image.saveToTIFF(name)

    def testSaveToTIFF(self):
        import os
        name = "testSaveToTiff"
        self.image.saveToTIFF(name)
        isSaved = True
        try:
            os.remove("{}.tif".format(name))
        except FileNotFoundError:
            isSaved = False
        self.assertTrue(isSaved)

    # def testGrayScaleConversionImageAlreadyGray(self):
    #     grayScale = self.image.getGrayscaleConversion()
    #     self.assertTrue(grayScale == self.image)

    # def testGrayScaleConversion(self):
    #     image = np.ones((10, 10, 3), dtype=np.float32)
    #     image[..., -1] = 0.
    #     image[..., -2] = 0.
    #     Image = Image(image)
    #     grayScale = Image.getGrayscaleConversion()
    #     self.assertTrue(grayScale.getNumberOfChannel() == 1)

    # def testGrayScaleConversionCompute(self):
    #     # Y = 0.2125 R + 0.7154 G + 0.0721 B
    #     array = np.ones((10, 10, 3), dtype=np.float32)
    #     array[:, :, 0] = 100.25
    #     array[:, :, 1] = 205.78
    #     array[:, :, 2] = 137.96
    #     weights = [0.2125, 0.7154, 0.0721]
    #     arrayGray = np.zeros((10, 10), dtype=np.float32)
    #     for i in range(10):
    #         for j in range(10):
    #             for weight in range(len(weights)):
    #                 arrayGray[i][j] += array[i][j][weight] * weights[weight]
    #     self.assertTrue(np.allclose(arrayGray, Image(array).getGrayscaleConversion().getArray()))

    # def testImageGetGrayHistogramValuesWarning(self):
    #     with warnings.catch_warnings(record=True):
    #         warnings.simplefilter("error")
    #         with self.assertRaises(UserWarning):
    #             self.image.getGrayscaleHistogramValues()

    # def testImageGetGrayHistogramValuesNotNormalized(self):
    #     array = np.ones((5, 5), dtype=np.float32)
    #     image = Image(array)
    #     hist = [0, 25]
    #     bins = [0, 1, 2]
    #     self.assertTrue(np.alltrue(image.getGrayscaleHistogramValues()[0] == hist) and np.alltrue(
    #         image.getGrayscaleHistogramValues()[-1] == bins))

    # def testImageGetGrayHistogramValuesNormalized(self):
    #     with warnings.catch_warnings():
    #         warnings.simplefilter("ignore", category=UserWarning)
    #         hist, bins = self.image.getGrayscaleHistogramValues(True)
    #     self.assertAlmostEqual(sum(hist), 1, delta=1e-9)

    # def testImageGetColorHistogramVsluesNoColorImage(self):
    #     with self.assertRaises(DimensionException):
    #         self.image.getRGBHistogramValues()

    # def testImageGetColorHistogramValuesWarning(self):
    #     image = Image(np.ones((199, 201, 3), dtype=np.float32) * 1.23)
    #     with warnings.catch_warnings(record=True):
    #         warnings.simplefilter("error")
    #         with self.assertRaises(UserWarning):
    #             image.getGrayscaleHistogramValues()

    # def testImageGetColorHistogramValuesNotNormalized(self):
    #     image = Image(np.ones((5, 5, 3), dtype=np.float32))
    #     allHists = [[0, 25]] * 3
    #     allBins = [[0, 1, 2]] * 3
    #     self.assertTrue(np.alltrue(np.equal(image.getRGBHistogramValues()[0], allHists)) and np.alltrue(
    #         np.equal(image.getRGBHistogramValues()[1], allBins)))

    # def testImageGetColorHistogramValuesNormalized(self):
    #     image = Image(np.ones((1000, 1000, 3), dtype=np.float32))
    #     allHist, allBins = image.getRGBHistogramValues(True)
    #     allSums = [sum(allHist[x]) for x in range(3)]
    #     self.assertTrue(np.allclose(allSums, 1, atol=1e-9, rtol=1e-9))

    # def testDCCDisplayImageGrayHistogramWarning(self):
    #     with warnings.catch_warnings(record=True):
    #         warnings.simplefilter("error")
    #         with self.assertRaises(UserWarning):
    #             self.image.displayGrayscaleHistogram()

    # @patch("matplotlib.pyplot.show", new=Mock)
    # def testImageDisplayGrayHistogramNotNormalized(self):
    #     with warnings.catch_warnings():
    #         warnings.simplefilter("ignore", UserWarning)
    #         histogramFromGetValues, binsFromGetValues = self.image.getGrayscaleHistogramValues()
    #         histogramFromDisplay, binsFromDisplay = self.image.displayGrayscaleHistogram()
    #     self.assertTrue(
    #         np.alltrue(np.equal(histogramFromDisplay, histogramFromGetValues)) and np.alltrue(
    #             np.equal(binsFromDisplay, binsFromGetValues)))

    # @patch("matplotlib.pyplot.show", new=Mock)
    # def testImageDisplayGrayHistogramNormalized(self):
    #     with warnings.catch_warnings():
    #         warnings.simplefilter("ignore", UserWarning)
    #         hist, bins = self.image.displayGrayscaleHistogram(True)
    #     self.assertAlmostEqual(sum(hist), 1, delta=1e-9)

    # def testImageDisplayColorHistogramNoColorImage(self):
    #     with self.assertRaises(DimensionException):
    #         self.image.displayRGBHistogram()

    # def testImageDisplayColorHistogramWarning(self):
    #     image = Image(np.ones((1200, 1452, 3), dtype=np.float32) * 0.01)
    #     with warnings.catch_warnings(record=True):
    #         warnings.simplefilter("error")
    #         with self.assertRaises(UserWarning):
    #             image.displayRGBHistogram()

    # @patch("matplotlib.pyplot.show", new=Mock)
    # def testImageDisplayColorHistogramNotNormalized(self):
    #     image = Image(np.ones((1250, 1300, 3), dtype=np.float32))
    #     histogramFromGetValues, binsFromGetValues = image.getRGBHistogramValues()
    #     histogramFromDisplay, binsFromDisplay = image.displayRGBHistogram()
    #     self.assertTrue(
    #         np.alltrue(np.equal(histogramFromDisplay, histogramFromGetValues)) and np.alltrue(
    #             np.equal(binsFromDisplay, binsFromGetValues)))

    # @patch("matplotlib.pyplot.show", new=Mock)
    # def testImageDisplayColorHistogramNormalized(self):
    #     image = Image(np.ones((1010, 1500, 3), dtype=np.float32))
    #     allHists, allBins = image.displayRGBHistogram(True)
    #     allSums = [sum(allHists[x]) for x in range(3)]
    #     self.assertTrue(np.allclose(allSums, 1, atol=1e-9, rtol=1e-9))

    # def testImageXDerivativeZerosOutput(self):
    #     array = np.ones((5, 5), dtype=np.float32)
    #     image = Image(array)
    #     dxImage = image.getXAxisDerivative()
    #     supposedDerivative = Image(np.zeros_like(array))
    #     self.assertTrue(dxImage == supposedDerivative)

    # def testImageXDerivative(self):
    #     array = np.zeros((3, 3), dtype=np.float32)
    #     array[1][1] = 2
    #     image = Image(array)
    #     dxImage = image.getXAxisDerivative()
    #     supposedDerivativeArray = np.array([[0, 0, 0], [-2, 0, 2], [0, 0, 0]], dtype=np.float32)
    #     supposedDerivativeImage = Image(supposedDerivativeArray)
    #     self.assertTrue(supposedDerivativeImage == dxImage)

    # def testImageYDerivativeZerosOutput(self):
    #     array = np.zeros((5, 5), dtype=np.float32)
    #     image = Image(array)
    #     dyImage = image.getYAxisDerivative()
    #     supposedDerivative = Image(np.zeros_like(array))
    #     self.assertTrue(dyImage == supposedDerivative)

    # def testImageYDerivative(self):
    #     array = np.zeros((3, 3), dtype=np.float32)
    #     array[1][1] = 2
    #     image = Image(array)
    #     dyImage = image.getYAxisDerivative()
    #     supposedDerivativeArray = np.array([[0, 0, 0], [-2, 0, 2], [0, 0, 0]], dtype=np.float32).T
    #     supposedDerivativeImage = Image(supposedDerivativeArray)
    #     self.assertTrue(supposedDerivativeImage == dyImage)

    # def testImageAverage(self):
    #     sumPixelValues = np.sum(self.image.getArray())
    #     average = sumPixelValues / self.image.getNumberOfPixels()
    #     self.assertEqual(average, self.image.getAverageValueOfImage())

    # def testImageAverageColors(self):
    #     array = np.ones((10, 10, 3), dtype=np.float32)
    #     array[0][0][0] = 0
    #     array[0][0][1] = 0
    #     array[0][0][2] = 0
    #     image = Image(array)
    #     supposedAverage = [np.sum(array[..., 0]) / image.getNumberOfPixels(),
    #                        np.sum(array[..., 1]) / image.getNumberOfPixels(),
    #                        np.sum(array[..., 2]) / image.getNumberOfPixels()]
    #     self.assertTrue(image.getAverageValueOfImage() == supposedAverage)

    # def testImageStandardDev(self):
    #     average = self.image.getAverageValueOfImage()[0]
    #     stanDevP1 = np.float_power(np.add(self.image.getArray(), -average), 2)
    #     stanDev = np.sqrt(np.sum(stanDevP1) / self.image.getNumberOfPixels())
    #     self.assertTrue(np.allclose(stanDev, self.image.getStadardDeviationValueOfImage()))

    # def testImageStandardDevColors(self):
    #     array = np.ones((10, 10, 3), dtype=np.float32)
    #     image = Image(array)
    #     averageS = image.getAverageValueOfImage()
    #     stanDevS = []
    #     for i in range(image.getNumberOfChannel()):
    #         average = averageS[i]
    #         stanDevSP1 = np.float_power(np.add(image.getArray()[..., i], -average),
    #                                     2)
    #         stanDevS.append(np.sqrt(np.sum(stanDevSP1) / image.getNumberOfPixels()))
    #     self.assertTrue(np.allclose(stanDevS, image.getStadardDeviationValueOfImage()))

    # def testImageShannonEntropy(self):
    #     base = 2
    #     uniqueValues, counts = np.unique(self.image.getArray(), return_counts=True)
    #     entropy = -np.sum(
    #         counts / self.image.getNumberOfPixels() * np.log(counts / self.image.getNumberOfPixels()) / np.log(base))
    #     self.assertAlmostEqual(entropy, self.image.getShannonEntropyOfImage(base))

    # def testImageGetPixelsOfIntensityGray(self):
    #     intensity = 100
    #     position = [(100, 100)]
    #     self.assertTrue(self.image.getPixelsOfIntensityGrayImage(intensity) == position)

    # def testImageGetPixelsOfIntensityGrayNoPixels(self):
    #     intensity = 100.01
    #     self.assertIsNone(self.image.getPixelsOfIntensityGrayImage(intensity))

    # def testImageGetPixelsOfIntensityGrayMoreThanOne(self):
    #     array = np.ones((5, 5), dtype=np.float32)
    #     image = Image(array)
    #     coords = []
    #     for i in range(5):
    #         for j in range(5):
    #             coords.append((i, j))
    #     self.assertTrue(image.getPixelsOfIntensityGrayImage(1) == coords)

    # def testImageGetPixelsOfIntensityColorAllChannels(self):
    #     array = np.ones((5, 5, 3), dtype=np.float32)
    #     array[0][0][0] = 0
    #     coords = [[(0, 0)], None, None]
    #     image = Image(array)
    #     self.assertTrue(image.getPixelsOfIntensityColorImageAllChannels(0) == coords)

    # def testImageGetPixelsOfIntensityColorAllChannelsAllNone(self):
    #     nones = [None, None, None]
    #     image = Image(np.zeros((1000, 1000, 3), dtype=np.float32))
    #     supposed = image.getPixelsOfIntensityColorImageAllChannels(125)
    #     self.assertTrue(supposed == nones)

    # def testImageGetPixelsOfIntensityColorAllChannelsMultiplePixels(self):
    #     listCoordsChannel0 = []
    #     listCoordsChannel2 = []
    #     array = np.ones((1000, 1000, 3), dtype=np.float32)
    #     for i in range(235, 754):
    #         for j in range(296, 407):
    #             array[i][j][0] = 12.56
    #             listCoordsChannel0.append((i, j))
    #             if i / (j + 1) >= 1.05:
    #                 array[i][j][2] = 12.56
    #                 listCoordsChannel2.append((i, j))
    #     listCoords = [listCoordsChannel0, None, listCoordsChannel2]
    #     image = Image(array)
    #     self.assertTrue(image.getPixelsOfIntensityColorImageAllChannels(12.56) == listCoords)

    # def testImageGetPixelsOfIntensityColorOneChannel(self):
    #     listCoordsChannel0 = []
    #     array = np.ones((1000, 1000, 3), dtype=np.float32)
    #     for i in range(235, 754):
    #         for j in range(296, 407):
    #             array[i][j][0] = 12.56
    #             listCoordsChannel0.append((i, j))
    #     image = Image(array)
    #     self.assertTrue(listCoordsChannel0 == image.getPixelsOfIntensityColorImageOneChannel(12.56, 0))

    # def testImageGetPixelsOfIntensityColorOneChannelOutOfBound(self):
    #     with self.assertRaises(ValueError):
    #         array = np.ones((1000, 1000, 3), dtype=np.float32)
    #         image = Image(array)
    #         image.getPixelsOfIntensityColorImageOneChannel(1, 3)

    # def testImageMinimumIntensityPixels(self):
    #     minimumPosition = (0, 0)
    #     self.assertTrue(self.image.getMinimumIntensityPixels() == [minimumPosition])

    # def testImageMinimumIntensityPixels2Pixels(self):
    #     self.array[10][10] = 0
    #     image = Image(self.array)
    #     minimumsPosition = [(0, 0), (10, 10)]
    #     self.assertTrue(image.getMinimumIntensityPixels() == minimumsPosition)

    # def testImageMinimumIntensityPixelsColors(self):
    #     array = np.ones((10, 10, 3), dtype=np.float32)
    #     array[0][0][0] = 0
    #     array[2][2][0] = 0
    #     array[0][0][1] = -10
    #     array[0][0][2] = -0.1
    #     image = Image(array)
    #     minimumsPosition = [[(0, 0), (2, 2)], [(0, 0)], [(0, 0)]]
    #     self.assertTrue(image.getMinimumIntensityPixels() == minimumsPosition)

    # def testImageMaximumIntensityPixels(self):
    #     maximumPosition = [(100, 100)]
    #     self.assertTrue(self.image.getMaximumIntensityPixels() == maximumPosition)

    # def testImageMaximumIntensityPixels2Pixels(self):
    #     self.array[50][50] = 100.0
    #     image = Image(self.array)
    #     maximumsPosition = [(50, 50), (100, 100)]
    #     self.assertTrue(image.getMaximumIntensityPixels() == maximumsPosition)

    # def testImageMaximumIntensityPixelsColors(self):
    #     array = np.ones((10, 10, 3), dtype=np.float32)
    #     array[0][0][0] = 10
    #     array[2][2][0] = 10
    #     array[0][0][1] = 1.01
    #     array[0][0][2] = 100
    #     image = Image(array)
    #     maximumIntensityPositions = [[(0, 0), (2, 2)], [(0, 0)], [(0, 0)]]
    #     other = image.getMaximumIntensityPixels()
    #     self.assertTrue(other == maximumIntensityPositions)

    # def testEntropyFilter(self):
    #     filterSize = 3
    #     array = np.zeros((5, 5), dtype=np.float32)
    #     array[2][2] = 1
    #     resultEntropyArray = np.zeros_like(array)
    #     for i in range(1, 4):
    #         for j in range(1, 4):
    #             resultEntropyArray[i][j] = 503.2583348E-3
    #     resultEntropyImage = Image(resultEntropyArray)
    #     self.assertTrue(resultEntropyImage == Image(array).getEntropyFiltering(filterSize))

    # def testGaussianFilter(self):
    #     sigma = 0.4
    #     array = np.zeros((5, 5), dtype=np.float32)
    #     array[2][2] = 1
    #     image = Image(array)
    #     gaussianBlurredArray = np.zeros_like(array)
    #     for i in range(5):
    #         for j in range(5):
    #             gaussianBlurredArray[i][j] = np.exp(-((i - 2) ** 2 + (j - 2) ** 2) / (2 * sigma ** 2)) / (
    #                     2 * np.pi * sigma ** 2)
    #     normalizedGaussianBlurredArray = gaussianBlurredArray / np.sum(gaussianBlurredArray)
    #     ImageGaussianArray = image.getGrayGaussianFiltering(sigma).getArray()
    #     self.assertTrue(np.allclose(ImageGaussianArray, normalizedGaussianBlurredArray))

    # def testGaussianFilterColors(self):
    #     sigma = 0.4
    #     array = np.zeros((5, 5, 3), dtype=np.float32)
    #     array[2][2][0] = 1
    #     array[2][2][1] = 1.2
    #     array[2][2][2] = 2
    #     image = Image(array)
    #     gaussianBlurredArray = np.zeros_like(array)
    #     # Because of the nature of the discrete convolution used in the gaussian filter
    #     # and because of the nature of the input array (which contains only 0s except for the middle pixel):
    #     # We must multiply the resulting array by that non zero digit. In cases where there are more non zero values:
    #     # It would be more complicated. (In the case of filters, convolution of two matrix (a and b) is represented
    #     # by a (or b) "moving over" b (or a) and the elements of the resulting matrix would be the sum of the 1-1
    #     # product of each element of a and b (a11*b11+a12*b12+...). Since we only have one non zero element
    #     # and since size of gaussian filter = size of input, the output is the normalized gaussian filter multiplied
    #     # by the only non zero input element. Hope it helps!
    #     multiplicationFactors = [1, 1.2, 2]
    #     for channel in range(3):
    #         for i in range(5):
    #             for j in range(5):
    #                 gaussianBlurredArray[i][j][channel] = np.exp(-((i - 2) ** 2 + (j - 2) ** 2) / (2 * sigma ** 2)) / (
    #                         2 * np.pi * sigma ** 2)
    #         gaussianBlurredArray[..., channel] = gaussianBlurredArray[..., channel] / np.sum(
    #             gaussianBlurredArray[..., channel]) * multiplicationFactors[channel]
    #     ImageGaussianArray = image.getColorGaussianFiltering(sigma).getArray()
    #     self.assertTrue(np.allclose(ImageGaussianArray, gaussianBlurredArray))

    # def testImageWithStandardDeviationFilter_MK1(self):
    #     array = np.zeros((5, 5), dtype=np.float32)
    #     # Padded array (internally happens when computing convolution with another matrix)
    #     paddedArray = np.zeros((7, 7), dtype=np.float32)
    #     for i in range(1, 4):
    #         for j in range(1, 4):
    #             array[i][j] = 3
    #             paddedArray[i + 1][j + 1] = 3
    #     listOfImages = []
    #     # Smaller array of size 3x3 resulting of the convolution
    #     for i in range(5):
    #         for j in range(5):
    #             listOfImages.append(Image(
    #                 np.array([paddedArray[i][j:j + 3], paddedArray[i + 1][j:j + 3], paddedArray[i + 2][j:j + 3]],
    #                          dtype=np.float32)))
    #     # Compute the standard deviation of the smaller arrays
    #     resultArray = np.array([image.getStadardDeviationValueOfImage() for image in listOfImages],
    #                            dtype=np.float32).reshape((5, 5))

    #     with warnings.catch_warnings():
    #         warnings.simplefilter('ignore', category=UserWarning)
    #         stdDevImageAsArray = Image(array).getStandardDeviationFilteringSlow(
    #             filterSize=3).getArray()
    #     self.assertTrue(np.allclose(resultArray, stdDevImageAsArray))

    # def testImageWithStandardDeviationFilter_MK1Warning(self):
    #     with warnings.catch_warnings(record=True):
    #         warnings.simplefilter("error")
    #         with self.assertRaises(UserWarning):
    #             self.image.getStandardDeviationFilteringSlow(3)

    # def testImageWithStandardDeviationFilter_MK2(self):
    #     array = np.zeros((5, 5), dtype=np.float32)
    #     # Padded array (internally happens when computing convolution with another matrix)
    #     paddedArray = np.zeros((7, 7), dtype=np.float32)
    #     for i in range(1, 4):
    #         for j in range(1, 4):
    #             array[i][j] = 2
    #             paddedArray[i + 1][j + 1] = 2
    #     listOfImages = []
    #     # Smaller array of size 3x3 resulting of the convolution
    #     for i in range(5):
    #         for j in range(5):
    #             listOfImages.append(Image(
    #                 np.array([paddedArray[i][j:j + 3], paddedArray[i + 1][j:j + 3], paddedArray[i + 2][j:j + 3]],
    #                          dtype=np.float32)))
    #     # Compute the standard deviation of the smaller arrays
    #     resultArray = np.array([image.getStadardDeviationValueOfImage() for image in listOfImages],
    #                            dtype=np.float32).reshape((5, 5))

    #     stdDevImageAsArray = Image(array).getStandardDeviationFiltering(
    #         filterSize=3).getArray()
    #     self.assertTrue(np.allclose(resultArray, stdDevImageAsArray, rtol=1e-4, atol=1e-4))

    # def testImageSTDDevFilterMK1AndMK2Equality(self):
    #     array = np.arange(16).reshape((4, 4)).astype(np.float32)
    #     image = Image(array)
    #     with warnings.catch_warnings():
    #         warnings.simplefilter("ignore", category=UserWarning)
    #         mk1 = image.getStandardDeviationFilteringSlow(3).getArray()
    #     mk2 = image.getStandardDeviationFiltering(3).getArray()
    #     self.assertTrue(np.allclose(mk1, mk2))

    # def testImageSTDDevMk1SlowerThanMK2(self):
    #     import time
    #     array = np.arange(50000).reshape((500, 100)).astype(np.float32)
    #     image = Image(array)
    #     beforeMK1 = time.clock()
    #     with warnings.catch_warnings():
    #         warnings.simplefilter("ignore", category=UserWarning)
    #         image.getStandardDeviationFilteringSlow(3).getArray()
    #     afterMK1 = time.clock()
    #     beforeMK2 = time.clock()
    #     image.getStandardDeviationFiltering(3).getArray()
    #     afterMK2 = time.clock()
    #     self.assertTrue((afterMK1 - beforeMK1) >= (afterMK2 - beforeMK2))

    # def testImageSTDDevMk2NanWarning(self):
    #     array = np.ones((5, 5, 3), dtype=np.float32)
    #     array[0][0][0] = np.nan
    #     image = Image(array)
    #     with warnings.catch_warnings(record=True):
    #         warnings.simplefilter("error")
    #         with self.assertRaises(RuntimeWarning):
    #             image.getStandardDeviationFiltering(3)

    # def testImageGetHorizontalSobelFilter(self):
    #     array = np.zeros((5, 5), dtype=np.float32)
    #     for i in range(1, 4):
    #         for j in range(1, 4):
    #             array[i][j] = 1
    #     image = Image(array)
    #     sobelResult = np.array([[0.25, 0.75, 1, 0.75, 0.25], [0.25, 0.75, 1, 0.75, 0.25], [0, 0, 0, 0, 0],
    #                             [-0.25, -0.75, -1, -0.75, -0.25], [-0.25, -0.75, -1, -0.75, -0.25]])
    #     # Remove false edges:
    #     sobelResult[0, :] = 0
    #     sobelResult[-1, :] = 0
    #     sobelResult[:, 0] = 0
    #     sobelResult[:, -1] = 0
    #     self.assertTrue(np.array_equal(image.getHorizontalSobelFiltering().getArray(), sobelResult))

    # def testImageGetVerticalSobelFilter(self):
    #     array = np.zeros((5, 5), dtype=np.float32)
    #     for i in range(1, 4):
    #         for j in range(1, 4):
    #             array[i][j] = 1
    #     image = Image(array)
    #     sobelResult = np.array([[0.25, 0.75, 1, 0.75, 0.25], [0.25, 0.75, 1, 0.75, 0.25], [0, 0, 0, 0, 0],
    #                             [-0.25, -0.75, -1, -0.75, -0.25], [-0.25, -0.75, -1, -0.75, -0.25]]).T
    #     # Remove false edges:
    #     sobelResult[0, :] = 0
    #     sobelResult[-1, :] = 0
    #     sobelResult[:, 0] = 0
    #     sobelResult[:, -1] = 0
    #     self.assertTrue(np.array_equal(image.getVerticalSobelFiltering().getArray(), sobelResult))

    # def testImageGetHorizontalAndVerticalSobelFilter(self):
    #     array = np.zeros((5, 5), dtype=np.float32)
    #     for i in range(1, 4):
    #         for j in range(1, 4):
    #             array[i][j] = 1
    #     image = Image(array)
    #     sobelResultHorizontal = np.array([[0.25, 0.75, 1, 0.75, 0.25], [0.25, 0.75, 1, 0.75, 0.25], [0, 0, 0, 0, 0],
    #                                       [-0.25, -0.75, -1, -0.75, -0.25], [-0.25, -0.75, -1, -0.75, -0.25]])
    #     sobelResultHorizontal[0, :] = 0
    #     sobelResultHorizontal[-1, :] = 0
    #     sobelResultHorizontal[:, 0] = 0
    #     sobelResultHorizontal[:, -1] = 0
    #     sobelResultVertical = sobelResultHorizontal.T
    #     sobelResult = np.sqrt(sobelResultHorizontal ** 2 + sobelResultVertical ** 2) / np.sqrt(2)
    #     self.assertTrue(np.allclose(image.getBothDirectionsSobelFiltering().getArray(), sobelResult))

    # def testImageIsodataThresholding(self):
    #     # Calculation by hand
    #     thresholding = 0.5
    #     array = np.zeros((5, 5), dtype=np.float32)
    #     for i in range(1, 4):
    #         for j in range(1, 4):
    #             array[i][j] = 1
    #     image = Image(array)
    #     handCalculatedThresholdedImage = Image((array >= thresholding).astype(np.float32))
    #     self.assertTrue(image.getIsodataThresholding() == handCalculatedThresholdedImage)

    # def testImageOtsuThresholding(self):
    #     # Calcultation by hand
    #     thresholding = 0.5
    #     array = np.zeros((5, 5), dtype=np.float32)
    #     for i in range(1, 4):
    #         for j in range(1, 4):
    #             array[i][j] = 1
    #     image = Image(array)
    #     handCalculatedThresholdedImage = Image((array >= thresholding).astype(np.float32))
    #     self.assertTrue(image.getOtsuThresholding() == handCalculatedThresholdedImage)

    # def testImageAdaptiveThreshGaussian(self):
    #     # The threshold array to compare to is just the result of applying a gaussian filter to the input image.
    #     threshArray = self.image.getGrayGaussianFiltering(1).getArray()
    #     array = self.image.getArray()
    #     resultOfThresholding = array >= threshArray
    #     resultOfThresholdingImage = Image(resultOfThresholding.astype(np.float32))
    #     self.assertTrue(self.image.getAdaptiveThresholdingGaussian(sigma=1) == resultOfThresholdingImage)

    # def testImageAdaptiveThreshMean(self):
    #     array = np.zeros((5, 5), dtype=np.float32)
    #     for i in range(1, 4):
    #         for j in range(1, 4):
    #             array[i][j] = 1
    #     image = Image(array)
    #     # Hand calculated
    #     threshArray = np.array([[1, 2, 3, 2, 1], [2, 4, 6, 4, 2], [3, 6, 9, 6, 3], [2, 4, 6, 4, 2], [1, 2, 3, 2, 1]],
    #                            dtype=np.float32) / 9
    #     threshImage = Image((array >= threshArray).astype(np.float32))
    #     self.assertTrue(image.getAdaptiveThresholdingMean(3) == threshImage)

    # def testImageAdaptiveThreshMedian(self):
    #     array = np.zeros((5, 5), dtype=np.float32)
    #     for i in range(1, 4):
    #         for j in range(1, 4):
    #             array[i][j] = 1
    #     image = Image(array)
    #     # Hand calculated
    #     threshArray = np.array([[0, 0, 0, 0, 0], [0, 0, 1, 0, 0], [0, 1, 1, 1, 0], [0, 0, 1, 0, 0], [0, 0, 0, 0, 0]],
    #                            dtype=np.float32)
    #     threshImage = Image((array >= threshArray).astype(np.float32))
    #     with warnings.catch_warnings():
    #         warnings.simplefilter("ignore", category=UserWarning)
    #         self.assertTrue(image.getAdaptiveThresholdingMedian(3) == threshImage)

    # # todo faire test watershed

    # def testImageBinaryOpening(self):
    #     array = np.zeros((20, 20), dtype=np.float32)
    #     arrayOpened = np.zeros_like(array)
    #     for i in range(6, 6 + 2):
    #         for j in range(6, 6 + 2):
    #             array[i][j] = 1
    #     for i in range(12, 20):
    #         for j in range(12, 20):
    #             array[i][j] = 1
    #             arrayOpened[i][j] = 1
    #     image = Image(array)
    #     imageOpened = Image(arrayOpened)
    #     self.assertTrue(image.getBinaryOpening(3) == imageOpened)

    # def testImageBinaryOpeningColorException(self):
    #     array = np.ones((1000, 1000, 3), dtype=np.float32)
    #     image = Image(array)
    #     with self.assertRaises(NotBinaryImageException):
    #         image.getBinaryOpening()

    # def testImageOpening(self):
    #     array = np.zeros((20, 20, 3), dtype=np.float32)
    #     arrayOpened = np.zeros_like(array)
    #     for i in range(6, 6 + 2):
    #         for j in range(6, 6 + 2):
    #             array[i][j][:] = 1
    #     for i in range(12, 20):
    #         for j in range(12, 20):
    #             array[i][j][:] = 1
    #             arrayOpened[i][j][:] = 1
    #     image = Image(array)
    #     imageOpened = Image(arrayOpened).getGrayscaleConversion()
    #     self.assertTrue(image.getOpening(3) == imageOpened)

    # def testImageBinaryClosing(self):
    #     array = np.ones((20, 20), dtype=np.float32)
    #     array[1][1] = 0
    #     windowSize = 3
    #     array[10: 10 + windowSize, 1:1 + windowSize] = 0
    #     array[3:3 + windowSize - 1, 6:6 + windowSize - 1] = 0
    #     array[15:15 + windowSize, 17:17 + windowSize - 1] = 0
    #     array[2:2 + windowSize, 15:15 + windowSize + 1] = 0
    #     arrayClosed = np.ones_like(array)
    #     # Regions of the original array where the "hole" is too big to close
    #     arrayClosed[2:2 + windowSize, 15:15 + windowSize + 1] = 0
    #     arrayClosed[10: 10 + windowSize, 1:1 + windowSize] = 0
    #     image = Image(array)
    #     imageClosed = Image(arrayClosed)
    #     self.assertTrue(image.getBinaryClosing(windowSize) == imageClosed)

    # def testImageBinaryClosingException(self):
    #     array = np.ones((1000, 1000, 3), dtype=np.float32)
    #     image = Image(array)
    #     with self.assertRaises(NotBinaryImageException):
    #         image.getBinaryClosing(10)

    # def testImageClosing(self):
    #     array = np.ones((20, 20, 3), dtype=np.float32)
    #     arrayClosed = np.ones_like(array)
    #     windowSize = 4
    #     array[0:5, 0:5, 1] = 0
    #     array[3:5, 2:5, 0] = 0
    #     array[15:16, 13:14, :] = 0
    #     array[10:15, 8:11, 2] = 0
    #     array[1:5, 7:12, 0] = 0
    #     image = Image(array)
    #     # R channel closing:
    #     # Hole too big to close
    #     arrayClosed[1:5, 7:12, 0] = 0
    #     # G channel closing:
    #     # Hole too big to close
    #     arrayClosed[0:5, 0:5, 1] = 0
    #     # B channel closing: all holes are closed
    #     closedImage = Image(arrayClosed).getGrayscaleConversion()
    #     self.assertTrue(closedImage == image.getClosing(windowSize))


if __name__ == '__main__':
    unittest.main()
