import env
from dcclab import *
import unittest
import numpy as np


class TestChannelInteger(env.DCCLabTestCase):
    def setUp(self) -> None:
        array = np.ones((5, 5), dtype=np.uint8)
        self.channelUint8 = Channel(array)
        self.channelUint16 = Channel(array.astype(np.uint16))

    def testValidComstructor(self):
        valid = np.ones((10, 10), dtype=np.uint8)
        self.assertIsInstance(Channel(valid), ChannelInt)

    def testValidBoolImage(self):
        valid = np.ones((100, 100), dtype=bool)
        self.assertIsInstance(Channel(valid), ChannelInt)

    def testGetHistogramValuesNotNormed(self):
        array = np.zeros((5, 5), dtype=np.uint8)
        for i in range(5):
            for j in range(5):
                array[i][j] = j * i
        channel = Channel(array)
        bins = np.arange(0, 18)
        hist = np.array([9, 1, 2, 2, 3, 0, 2, 0, 2, 1, 0, 0, 2, 0, 0, 0, 1])
        histValues = channel.getHistogramValues()
        self.assertTrue(np.array_equal(bins, histValues[-1]) and np.array_equal(hist, histValues[0]))

    def testGetHistogramValuesNormed(self):
        array = np.zeros((5, 5), dtype=np.uint8)
        for i in range(5):
            for j in range(5):
                array[i][j] = j * i
        channel = Channel(array)
        histValues = channel.getHistogramValues(True)
        self.assertEqual(sum(histValues[0]), 1)

    def testConvo(self):
        with warnings.catch_warnings():
            warnings.simplefilter('ignore', category=UserWarning)
            convo = self.channelUint8.convolveWith(np.identity(3))
            self.assertTrue(np.allclose(convo.pixels, 3 / 255) and isinstance(convo, ChannelFloat))

    def testApplyConv(self):
        self.channelUint8.applyConvolution([[1, 1, 1], [1, 1, 1]])
        self.assertTrue(self.channelUint8.pixels.dtype == np.uint8 and isinstance(self.channelUint8, ChannelInt))
        self.assertIsInstance(self.channelUint8, ChannelInt)

    def testGetGaussianFilter(self):
        sigma = 0.4
        array = np.zeros((5, 5), dtype=np.uint8)
        array[2][2] = 100
        channel = Channel(array)
        gaussianBlurredArray = np.zeros_like(array, dtype=np.float32)
        gaussianBlurredArray[2][2] = 100 / 255
        for i in range(5):
            for j in range(5):
                gaussianBlurredArray[i][j] = np.exp(-((i - 2) ** 2 + (j - 2) ** 2) / (2 * sigma ** 2)) / (
                        2 * np.pi * sigma ** 2)
        normalizedGaussianBlurredArray = gaussianBlurredArray / np.sum(gaussianBlurredArray) * 100 / 255
        with warnings.catch_warnings():
            warnings.simplefilter('ignore', category=UserWarning)
            channelGaussian = channel.getGaussianFilter(sigma)
        channelGaussianPixels = channelGaussian.pixels
        self.assertTrue(np.allclose(channelGaussianPixels,
                                    normalizedGaussianBlurredArray) and isinstance(channelGaussian, ChannelFloat))

    def testApplyGaussian(self):
        self.channelUint16.applyGaussianFilter(0.00254)
        self.assertTrue(self.channelUint16.pixels.dtype == np.uint16 and isinstance(self.channelUint16, ChannelInt))

    def testGetEntropyFiltering(self):
        filterSize = 3
        array = np.zeros((5, 5), dtype=np.uint8)
        array[2][2] = 1 / 255
        resultEntropyArray = np.zeros_like(array)
        for i in range(1, 4):
            for j in range(1, 4):
                resultEntropyArray[i][j] = 503.2583348E-3
        resultEntropyImage = Channel(resultEntropyArray)
        computedByClass = Channel(array).getEntropyFilter(filterSize)
        self.assertTrue(resultEntropyImage == computedByClass and isinstance(computedByClass, ChannelFloat))


    def testGetStandardDeviation(self):
        array = np.zeros((5, 5), dtype=np.uint16)
        # Padded array (internally happens when computing convolution with another matrix)
        paddedArray = np.zeros((7, 7))
        for i in range(1, 4):
            for j in range(1, 4):
                array[i][j] = 3
                paddedArray[i + 1][j + 1] = 3 / (2 ** 16 - 1)
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
        with warnings.catch_warnings():
            warnings.simplefilter('ignore', category=UserWarning)
            stdDevChannel = Channel(array).getStandardDeviationFilter(filterSize=3)
            stdDevChannelPixels = stdDevChannel.pixels

        self.assertTrue(np.allclose(resultArray, stdDevChannelPixels) and isinstance(stdDevChannel, ChannelFloat))

    def testGetHorizontalSobelFilter(self):
        array = np.zeros((5, 5), dtype=np.uint8)
        for i in range(1, 4):
            for j in range(1, 4):
                array[i][j] = 1
        channel = Channel(array.T)
        sobelResult = (np.array([[0.25, 0.75, 1, 0.75, 0.25], [0.25, 0.75, 1, 0.75, 0.25], [0, 0, 0, 0, 0],
                                [-0.25, -0.75, -1, -0.75, -0.25], [-0.25, -0.75, -1, -0.75, -0.25]]) / 255).T
        # Remove false edges:
        sobelResult[0, :] = 0
        sobelResult[-1, :] = 0
        sobelResult[:, 0] = 0
        sobelResult[:, -1] = 0
        with warnings.catch_warnings():
            warnings.simplefilter('ignore', category=UserWarning)
            computedSobel = channel.getHorizontalSobelFilter()
        self.assertTrue(np.allclose(computedSobel.pixels, sobelResult))
        self.assertIsInstance(computedSobel, ChannelFloat)

    def testGetVerticalSobelFilter(self):
        array = np.zeros((5, 5), dtype=np.uint8)
        for i in range(1, 4):
            for j in range(1, 4):
                array[i][j] = 1
        channel = Channel(array)
        sobelResult = (np.array([[0.25, 0.75, 1, 0.75, 0.25], [0.25, 0.75, 1, 0.75, 0.25], [0, 0, 0, 0, 0],
                                 [-0.25, -0.75, -1, -0.75, -0.25], [-0.25, -0.75, -1, -0.75, -0.25]]) / 255)
        # Remove false edges:
        sobelResult[0, :] = 0
        sobelResult[-1, :] = 0
        sobelResult[:, 0] = 0
        sobelResult[:, -1] = 0
        with warnings.catch_warnings():
            warnings.simplefilter('ignore', category=UserWarning)
            computedSobel = channel.getVerticalSobelFilter()
        self.assertTrue(np.allclose(computedSobel.pixels, sobelResult))
        self.assertIsInstance(computedSobel, ChannelFloat)

    def testGetSobelFilter(self):
        array = np.zeros((5, 5), dtype=np.uint8)
        for i in range(1, 4):
            for j in range(1, 4):
                array[i][j] = 1
        channel = Channel(array)
        HSobelResult = np.array([[0.25, 0.75, 1, 0.75, 0.25], [0.25, 0.75, 1, 0.75, 0.25], [0, 0, 0, 0, 0],
                                 [-0.25, -0.75, -1, -0.75, -0.25], [-0.25, -0.75, -1, -0.75, -0.25]]) / 255
        # Remove false edges:
        HSobelResult[0, :] = 0
        HSobelResult[-1, :] = 0
        HSobelResult[:, 0] = 0
        HSobelResult[:, -1] = 0
        VSobelResult = HSobelResult.T
        with warnings.catch_warnings():
            warnings.simplefilter('ignore', category=UserWarning)
            computedSobel = channel.getSobelFilter()
        sobelResult = np.sqrt(HSobelResult ** 2 + VSobelResult ** 2) / np.sqrt(2)
        self.assertTrue(np.allclose(computedSobel.pixels, sobelResult))
        self.assertIsInstance(computedSobel, ChannelFloat)

    def testIsodataThresh(self):
        # Calculation by hand
        thresholding = 0.5
        array = np.zeros((5, 5), dtype=np.uint8)
        for i in range(1, 4):
            for j in range(1, 4):
                array[i][j] = 1
        channel = Channel(array)
        handCalculatedThresholdedImage = Channel((array >= thresholding).astype("uint"))
        self.assertTrue(channel.getIsodataThresholding() == handCalculatedThresholdedImage)

    def testOtsuThresh(self):
        # Calculation by hand
        thresholding = 0.5
        array = np.zeros((5, 5), dtype=np.uint8)
        for i in range(1, 4):
            for j in range(1, 4):
                array[i][j] = 1
        channel = Channel(array)
        handCalculatedThresholdedImage = Channel((array >= thresholding).astype("uint"))
        self.assertTrue(channel.getOtsuThresholding() == handCalculatedThresholdedImage)

    def testAdaptiveThresholdMean(self):
        array = np.zeros((5, 5), dtype=np.uint8)
        array[1:4, 1:4] = 5
        threshArray = np.zeros_like(array)
        threshArray[1:4, 1:4] = 1
        threshArray[2, 2] = 0
        self.assertTrue(np.array_equal(Channel(array).getAdaptiveThresholdMean(3).pixels, threshArray))

    def testAdaptiveThresholdGaussian(self):
        array = np.arange(0, 25).reshape((5, 5)).astype(np.uint8)
        channel = Channel(array)
        self.assertTrue(channel.getAdaptiveThresholdGaussian(3).isBinary)

    def testConvertTo8BitsUint(self):
        array = np.arange(0, 1000).reshape((10, 100)).astype(np.uint16)
        self.assertTrue(Channel(array).convertTo8BitsUnsignedInteger().pixels.dtype == np.uint8)

    def testConvertTo8BitsUintCheckValues(self):
        array = np.ones((5, 5), dtype=np.uint16)
        array[2, 2] = 1023
        self.assertTrue(np.array_equal(Channel(array).convertTo8BitsUnsignedInteger().pixels,
                                       (array / (2 ** 16 - 1) * 255).astype(np.uint8)))

    def testConvertTo8BitsUintFrom8BitsUint(self):
        array = np.ones((100, 100), dtype=np.uint8) * 25
        self.assertTrue(np.array_equal(Channel(array).convertTo8BitsUnsignedInteger().pixels, array))

    def testConvertTo16BitsUint(self):
        array = np.ones((100, 100), dtype=np.uint8) * 201
        self.assertTrue(Channel(array).convertTo16BitsUnsignedInteger().pixels.dtype == np.uint16)

    def testConvertTo16BitsUintCheckValues(self):
        array = np.ones((5, 5), dtype=np.uint8) * 151
        self.assertTrue(np.array_equal(Channel(array).convertTo16BitsUnsignedInteger().pixels,
                                       (array / 255 * (2 ** 16 - 1)).astype(np.uint16)))

    def testConvertTo16BitsUintFrom16BitsUint(self):
        array = np.ones((1000, 1000), dtype=np.uint16) * 22222
        self.assertTrue(np.array_equal(Channel(array).convertTo16BitsUnsignedInteger().pixels, array))

    def testConvertToNormalizedFloat(self):
        array = np.ones((10000, 1000), dtype=np.uint8) * 250
        self.assertIsInstance(Channel(array).convertToNormalizedFloat(), ChannelFloat)

    def testConvertToNormalizedFloatValues(self):
        array = np.ones((100, 100), dtype=np.uint8) * 78
        self.assertTrue(np.allclose(Channel(array).convertToNormalizedFloat().pixels, array / 255))

    def testConvertToNormalizedFloatFromUint16(self):
        array = np.ones((10000, 1000), dtype=np.uint16) * 2500
        self.assertIsInstance(Channel(array).convertToNormalizedFloat(), ChannelFloat)

    def testConvertToNormalizedFloatFromUint16Values(self):
        array = np.ones((100, 100), dtype=np.uint16) * 7800
        self.assertTrue(np.allclose(Channel(array).convertToNormalizedFloat().pixels, array / (2 ** 16 - 1)))

    def testOtsuThreshError(self):
        array = np.ones((100, 100), dtype=np.uint16)
        with self.assertRaises(ValueError):
            Channel(array).getOtsuThresholding()

    def testApplyXDeriv(self):
        self.channelUint16.applyXDerivative()
        self.assertIsInstance(self.channelUint16, ChannelInt)

    def testApplyYDeriv(self):
        self.channelUint16.applyYDerivative()
        self.assertIsInstance(self.channelUint16, ChannelInt)

    def testNormalizationMinToZeroMaxToOne16Bits(self):
        for i in range(0, 10):
            i = np.random.randint(2, 1000)
            j = np.random.randint(2, 1000)
            channel = Channel(
                np.random.randint(0, 2 ** 16 - 1, (i, j)).astype(np.uint16)).convertToNormalizedFloatMinToZeroMaxToOne()
            self.assertTupleEqual(channel.getExtrema(), (0, 1))


if __name__ == '__main__':
    unittest.main()
