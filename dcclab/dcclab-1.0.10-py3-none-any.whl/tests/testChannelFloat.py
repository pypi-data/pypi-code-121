import env
from dcclab import *
import unittest
import numpy as np


class TestChannelFloat(env.DCCLabTestCase):

    def setUp(self) -> None:
        array = np.ones((10, 10), dtype=np.float32) * 2.35
        self.channelNotNormalized = Channel(array)
        arrayNormed = np.ones_like(array) * 0.87
        self.channelNormalized = Channel(arrayNormed)

    def testValidConstructor(self):
        self.assertTrue(
            isinstance(self.channelNormalized, ChannelFloat) and isinstance(self.channelNotNormalized, ChannelFloat))

    def testIsNormalizedAfterInit(self):
        self.assertTrue(np.max(self.channelNotNormalized.pixels) == 1)

    def testGetHistogramValues(self):
        bins = np.arange(0, 257)
        hist = np.zeros((256,))
        hist[-1] = 100
        computedHist, computedBins = self.channelNotNormalized.getHistogramValues()
        self.assertTrue(np.array_equal(computedBins, bins) and np.array_equal(computedHist, hist))

    def testGetHistogramValuesNormed(self):
        self.assertTrue(sum(self.channelNormalized.getHistogramValues(True)[0]) == 1)

    def testEntropyFiltering(self):
        filterSize = 3
        array = np.zeros((5, 5), dtype=np.float32)
        array[2][2] = 0.25
        resultEntropyArray = np.zeros_like(array)
        for i in range(1, 4):
            for j in range(1, 4):
                resultEntropyArray[i][j] = 503.2583348E-3
        resultEntropyImage = Channel(resultEntropyArray)
        computedByClass = Channel(array).getEntropyFilter(filterSize)
        self.assertTrue(resultEntropyImage == computedByClass)

    def testConvolveWith(self):
        array = [[0.5, 0, 0, 0, 0, 1], [0, 0, 1, 1, 0, 0], [0.25, 0, 1, 0.5, 0, 0], [0, 0, 0, 0, 0, 0.0025]]
        array = np.array(array)
        resultArray = [[0.5, 0.5, 0, 0, 1 / 3, 1 / 3], [0, 1 / 3, 1 / 3, 1, 1, 0], [0.25, 1.75 / 3, 0.5 / 3, 1, 0.5, 0],
                       [0, 0, 0, 0, 0.0025 / 3, 0.0025 / 3]]
        resultArray = np.array(resultArray).T
        self.assertTrue(np.allclose(Channel(array.T).convolveWith([[1, 0, 3]]).pixels, resultArray))

    def testGaussianFilter(self):
        sigma = 0.4
        array = np.zeros((5, 5), dtype=np.float32)
        array[2][2] = 100
        channel = Channel(array)
        gaussianBlurredArray = np.zeros_like(array, dtype=np.float32)
        gaussianBlurredArray[2][2] = 1
        for i in range(5):
            for j in range(5):
                gaussianBlurredArray[i][j] = np.exp(-((i - 2) ** 2 + (j - 2) ** 2) / (2 * sigma ** 2)) / (
                        2 * np.pi * sigma ** 2)
        normalizedGaussianBlurredArray = gaussianBlurredArray / np.sum(gaussianBlurredArray) * 1
        channelGaussian = channel.getGaussianFilter(sigma)
        channelGaussianPixels = channelGaussian.pixels
        self.assertTrue(np.allclose(channelGaussianPixels,
                                    normalizedGaussianBlurredArray) and isinstance(channelGaussian, ChannelFloat))

    def testStandardDevFilter(self):
        array = np.zeros((5, 5), dtype=np.float32)
        # Padded array (internally happens when computing convolution with another matrix)
        paddedArray = np.zeros((7, 7))
        for i in range(1, 4):
            for j in range(1, 4):
                array[i][j] = 0.75
                paddedArray[i + 1][j + 1] = 0.75
        listOfChannels = []
        # Smaller array of size 3x3 resulting of the convolution
        for i in range(5):
            for j in range(5):
                listOfChannels.append(
                    Channel(np.array([paddedArray[i][j:j + 3], paddedArray[i + 1][j:j + 3],
                                      paddedArray[i + 2][j:j + 3]], dtype=np.float32)))
                # Compute the standard deviation of the smaller arrays
        resultArray = np.array([channel.getStandardDeviation() for channel in listOfChannels],
                               dtype=np.float32).reshape((5, 5))
        stdDevChannel = Channel(array).getStandardDeviationFilter(filterSize=3)
        stdDevChannelPixels = stdDevChannel.pixels

        self.assertTrue(np.allclose(resultArray, stdDevChannelPixels) and isinstance(stdDevChannel, ChannelFloat))

    def testIsodataThresh(self):

        thresh = self.channelNotNormalized.getIsodataThresholding()
        self.assertIsInstance(thresh, ChannelInt)

    def testOtsuThresh(self):
        channel = Channel(np.arange(0, 100).reshape((10, 10)).astype(np.float32))
        thresh = channel.getOtsuThresholding()
        self.assertIsInstance(thresh, ChannelInt)

    def testAdaptiveThreshMean(self):
        thresh = self.channelNotNormalized.getAdaptiveThresholdMean()
        self.assertIsInstance(thresh, ChannelInt)

    def testAdaptiveThreshGaussian(self):

        thresh = self.channelNotNormalized.getAdaptiveThresholdGaussian()
        self.assertIsInstance(thresh, ChannelInt)

    def testHSobelFilter(self):
        convol = self.channelNotNormalized.convolveWith((np.array([[1, 2, 1], [0, 0, 0], [-1, -2, -1]]) / 4.0))
        self.assertEqual(convol, self.channelNotNormalized.getHorizontalSobelFilter())

    def testVSobelFilter(self):
        convol = self.channelNotNormalized.convolveWith((np.array([[1, 2, 1], [0, 0, 0], [-1, -2, -1]]) / 4.0).T)
        self.assertEqual(convol, self.channelNotNormalized.getVerticalSobelFilter())

    def testSobelFilter(self):
        hSobel = self.channelNotNormalized.convolveWith((np.array([[1, 2, 1], [0, 0, 0], [-1, -2, -1]]) / 4.0))
        vSobel = self.channelNotNormalized.convolveWith((np.array([[1, 2, 1], [0, 0, 0], [-1, -2, -1]]) / 4.0).T)
        HVSobel = np.sqrt(hSobel.pixels ** 2 + vSobel.pixels ** 2) / 2 ** (1 / 2)
        channelSobel = Channel(HVSobel)
        self.assertEqual(self.channelNotNormalized.getSobelFilter(), channelSobel)

    def testConvertTo8BitsUint(self):
        array = (self.channelNotNormalized.pixels * 255).astype(np.uint8)
        self.assertEqual(Channel(array), self.channelNotNormalized.convertTo8BitsUnsignedInteger())

    def testConvertTo16BitsUint(self):
        array = (self.channelNotNormalized.pixels * (2 ** 16 - 1)).astype(np.uint16)
        self.assertEqual(Channel(array), self.channelNotNormalized.convertTo16BitsUnsignedInteger())

    def testStandDevFilterWarningNan(self):
        array = np.zeros((10, 10), dtype=np.float32)
        array[0, 0] = np.nan
        with warnings.catch_warnings():
            warnings.simplefilter("error", category=RuntimeWarning)
            with self.assertRaises(RuntimeWarning):
                Channel(array).getStandardDeviationFilter(3)

    def testStandDevFilterChangeNan(self):
        array = np.zeros((10, 10), dtype=np.float32)
        array[0, 0] = np.nan
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", category=RuntimeWarning)
            stdDevFiltered = Channel(array).getStandardDeviationFilter(3)
        self.assertFalse(np.alltrue(np.isnan(stdDevFiltered.pixels)))


if __name__ == '__main__':
    unittest.main()
