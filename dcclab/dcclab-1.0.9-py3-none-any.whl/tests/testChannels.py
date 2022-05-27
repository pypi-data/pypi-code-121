import env
from dcclab import *
import unittest
from unittest.mock import Mock, patch
import numpy as np


class TestChannels(env.DCCLabTestCase):

    def testInitWithComplexValues(self):
        array = np.ones((100, 100), dtype=complex) * (1 + 23.45j)
        with self.assertRaises(PixelTypeException):
            Channel(array.T)

    def testInitWith2DIntArray(self):
        array = np.ones((100, 100), dtype=np.int)
        channel = Channel(pixels=array.T)
        self.assertIsNotNone(channel)
        self.assertIsInstance(channel, Channel)

    def testInitWith2DFloatArray(self):
        array = np.ones((100, 100), dtype=np.float32)
        channel = Channel(pixels=array.T)
        self.assertIsNotNone(channel)
        self.assertIsInstance(channel, Channel)

    def testInitWith1DOR3DArrayFails(self):
        array = np.ones((100, 100, 3), dtype=np.float32)
        with self.assertRaises(DimensionException):
            channel = Channel(pixels=array.T)
        array = np.ones((100), dtype=np.float32)
        with self.assertRaises(DimensionException):
            channel = Channel(pixels=array.T)

    def testInitWith2DIntegerArray(self):
        array = np.random.randint(low=0, high=255, size=(100, 200))
        channel = Channel(pixels=array.T)
        self.assertEqual(array.all(), channel.pixels.all())

    def testStringRepresentation(self):
        array = np.random.randint(low=0, high=255, size=(100, 200), dtype=np.uint8)
        channel = Channel(pixels=array.T)
        self.assertEqual(str(array.T), str(channel))

    def testAddWithOtherChannel(self):
        array = np.array([[3, 3, 3, 3], [3, 3, 3, 3], [3, 3, 3, 3], [3, 3, 3, 3]])
        channel1 = Channel(pixels=array.T)
        array2 = np.array([[1, 1, 1, 1], [1, 1, 1, 1], [1, 1, 1, 1], [1, 1, 1, 1]])
        channel2 = Channel(pixels=array2.T)
        sub = channel1 + channel2
        supposedSub = Channel(pixels=np.array([[4] * 4, [4] * 4, [4] * 4, [4] * 4]).T)
        self.assertTrue(np.array_equal(sub.pixels, supposedSub.pixels))

    def testAddWithFloat(self):
        array = np.array([[3, 3, 3, 3], [3, 3, 3, 3], [3, 3, 3, 3], [3, 3, 3, 3]])
        channel1 = Channel(pixels=array.T)
        sub = channel1 + 1.9  # 1.1
        supposedSub = Channel(
            pixels=np.array([[3 + 1.9] * 4, [3 + 1.9] * 4, [3 + 1.9] * 4, [3 + 1.9] * 4]))
        self.assertTrue(np.array_equal(sub.pixels, supposedSub.pixels))

    def testAddWithInt(self):
        array = np.array([[3, 3, 3, 3], [3, 3, 3, 3], [3, 3, 3, 3], [3, 3, 3, 3]])
        channel1 = Channel(pixels=array.T)
        sub = channel1 + 1
        supposedSub = Channel(
            pixels=np.array([[4, 4, 4, 4], [4, 4, 4, 4], [4, 4, 4, 4], [4, 4, 4, 4]]))
        self.assertTrue(np.array_equal(sub.pixels, supposedSub.pixels))

    def testAddWithInvalidType(self):
        import numpy.core._exceptions as npExcep
        array = np.array([[3, 3, 3, 3], [3, 3, 3, 3], [3, 3, 3, 3], [3, 3, 3, 3]])
        channel1 = Channel(pixels=array.T)
        with self.assertRaises(npExcep.UFuncTypeError):
            channel1 + "a"

    def testAddWithInvalidShape(self):
        array = np.array([[3, 3, 3, 3], [3, 3, 3, 3], [3, 3, 3, 3], [3, 3, 3, 3]])
        channel1 = Channel(pixels=array.T)
        otherChannel = Channel(pixels=np.random.randint(0, 100, (10, 10)))
        with self.assertRaises(ValueError):
            channel1 + otherChannel

    def testAddWithOtherObject(self):
        import datetime
        channel = Channel(pixels=np.random.randint(0, 200, (10, 10)).T)
        with self.assertRaises(TypeError):
            channel + datetime.datetime.now()

    def testSubWithOtherChannel(self):
        array = np.array([[3, 3, 3, 3], [3, 3, 3, 3], [3, 3, 3, 3], [3, 3, 3, 3]])
        channel1 = Channel(pixels=array.T)
        array2 = np.array([[1, 1, 1, 1], [1, 1, 1, 1], [1, 1, 1, 1], [1, 1, 1, 1]])
        channel2 = Channel(pixels=array2.T)
        sub = channel1 - channel2
        supposedSub = Channel(pixels=np.array([[2, 2, 2, 2], [2, 2, 2, 2], [2, 2, 2, 2], [2, 2, 2, 2]]).T)
        self.assertTrue(np.array_equal(sub.pixels, supposedSub.pixels))

    def testSubWithFloat(self):
        array = np.array([[3, 3, 3, 3], [3, 3, 3, 3], [3, 3, 3, 3], [3, 3, 3, 3]])
        channel1 = Channel(pixels=array.T)
        sub = channel1 - 1.9  # 1.1
        supposedSub = Channel(
            pixels=np.array([[1.1, 1.1, 1.1, 1.1], [1.1, 1.1, 1.1, 1.1], [1.1, 1.1, 1.1, 1.1], [1.1, 1.1, 1.1, 1.1]]))
        self.assertTrue(np.array_equal(sub.pixels, supposedSub.pixels))

    def testSubdWithInt(self):
        array = np.array([[3, 3, 3, 3], [3, 3, 3, 3], [3, 3, 3, 3], [3, 3, 3, 3]])
        channel1 = Channel(pixels=array.T)
        sub = channel1 - 1
        supposedSub = Channel(
            pixels=np.array([[2, 2, 2, 2], [2, 2, 2, 2], [2, 2, 2, 2], [2, 2, 2, 2]]))
        self.assertTrue(np.array_equal(sub.pixels, supposedSub.pixels))

    def testSubWithInvalidType(self):
        import numpy.core._exceptions as npExcep
        array = np.array([[3, 3, 3, 3], [3, 3, 3, 3], [3, 3, 3, 3], [3, 3, 3, 3]])
        channel1 = Channel(pixels=array.T)
        with self.assertRaises(npExcep.UFuncTypeError):
            channel1 - "a"

    def testSubWithInvalidShape(self):
        array = np.array([[3, 3, 3, 3], [3, 3, 3, 3], [3, 3, 3, 3], [3, 3, 3, 3]])
        channel1 = Channel(pixels=array.T)
        otherChannel = Channel(pixels=np.random.randint(0, 100, (10, 10)))
        with self.assertRaises(ValueError):
            channel1 - otherChannel

    def testSubWithOtherObject(self):
        import datetime
        channel = Channel(pixels=np.random.randint(0, 200, (10, 10)).T)
        with self.assertRaises(TypeError):
            channel - datetime.datetime.now()

    def testInitCopiesPixels(self):
        array = np.random.randint(low=0, high=255, size=(100, 200))
        channel = Channel(pixels=array.T)
        self.assertFalse(array is channel.pixels)

    def testDimension(self):
        array = np.random.randint(low=0, high=255, size=(100, 200))
        channel = Channel(pixels=array.T)
        self.assertTrue(channel.dimension == 2)

    def testShape(self):
        array = np.random.randint(low=0, high=255, size=(100, 200))
        channel = Channel(pixels=array)
        self.assertTrue(channel.shape == array.shape)

    def testWidth(self):
        array = np.random.randint(low=0, high=255, size=(100, 200))
        channel = Channel(pixels=array.T)
        self.assertEqual(channel.width, 200)

    def testHeight(self):
        array = np.random.randint(low=0, high=255, size=(100, 200))
        channel = Channel(pixels=array.T)
        self.assertEqual(channel.height, 100)

    def testNumberOfPixels(self):
        array = np.random.randint(low=0, high=255, size=(100, 200))
        channel = Channel(pixels=array.T)
        self.assertTrue(channel.numberOfPixels == 100 * 200)

    def testSizeInBytes(self):
        array = np.random.randint(low=0, high=255, size=(100, 200))
        channel = Channel(pixels=array.T)
        self.assertTrue(channel.sizeInBytes == array.nbytes)

    def testEqualChannels(self):
        array = np.random.randint(low=0, high=255, size=(100, 200))
        channel1 = Channel(pixels=array.T)
        channel2 = Channel(pixels=array.T)
        self.assertEqual(channel1, channel2)

    def testEqualDifferentTypes(self):
        array = np.random.randint(low=0, high=255, size=(100, 200))
        channel = Channel(pixels=array.T)

        self.assertNotEqual(1, 'abc')  # not an error, simply false
        self.assertNotEqual(1, np)  # not an error, simply false
        self.assertNotEqual(1, channel)  # not an error, simply false

    def testPixelsCopy(self):
        array = np.random.randint(low=0, high=255, size=(100, 200))
        channel = Channel(pixels=array.T)
        pixels = channel.copy()
        self.assertFalse(pixels is array)

    def testIsBinary(self):
        array = np.random.randint(low=0, high=2, size=(100, 200))
        self.assertTrue(Channel(pixels=array.T).isBinary)
        self.assertFalse(Channel(pixels=array.T * 255).isBinary)
        self.assertFalse(Channel(pixels=array.T * 200).isBinary)

        array = np.random.randint(low=0, high=255, size=(100, 200))
        self.assertFalse(Channel(pixels=array.T).isBinary)

    @patch("matplotlib.pyplot.show", new=Mock())
    def testDisplayHistogramNormalized(self):
        channel = Channel(np.random.randint(0, 255, (10, 10), dtype=np.uint8).T)
        histValues, histBins = channel.getHistogramValues(True)
        displayValues, displayBins = channel.displayHistogram(True)
        self.assertTrue(np.array_equal(histValues, displayValues))
        self.assertTrue(np.array_equal(histBins, displayBins))

    @patch("matplotlib.pyplot.show", new=Mock())
    def testDisplayChannel(self):
        channel = Channel(np.random.randint(0, 255, (10, 10), dtype=np.uint8).T)
        obj = channel.display()
        self.assertEqual(obj, channel)

    def testApplySomethingChangesPixels(self):
        channel = Channel(np.random.randint(0, 255, (10, 10), dtype=np.uint8).T)
        originalPixels = channel.pixels
        channel.applyXDerivative()
        self.assertFalse(np.array_equal(originalPixels, channel.pixels))

    def testRestoreOriginal(self):
        channel = Channel(np.random.randint(0, 255, (10, 10), dtype=np.uint8).T)
        originalPixels = channel.pixels
        channel.applyXDerivative()
        channel.restoreOriginal()
        self.assertTrue(np.array_equal(originalPixels, channel.pixels))

    def testRestoreOriginalNotSavedBefore(self):
        channel = Channel(np.random.randint(0, 255, (10, 10), dtype=np.uint8).T)
        self.assertIsNone(channel.restoreOriginal())

    def testOriginalPixelsNone(self):
        channel = Channel(np.random.randint(0, 255, (10, 10), dtype=np.uint8).T)
        self.assertIsNone(channel.originalPixels)

    def testOriginalPixels(self):
        channel = Channel(np.random.randint(0, 255, (10, 10), dtype=np.uint8).T)
        originalPixels = channel.pixels
        channel.applyClosing(4)
        self.assertTrue(np.array_equal(originalPixels, channel.originalPixels))

    def testHasNoOriginalPixels(self):
        channel = Channel(np.random.randint(0, 255, (10, 10), dtype=np.uint8).T)
        self.assertFalse(channel.hasOriginal)

    def testHasOriginalPixels(self):
        channel = Channel(np.random.randint(0, 255, (10, 10), dtype=np.uint8).T)
        channel.applyConvolution([[1, 2, 3], [-3, -2, -1]])
        self.assertTrue(channel.hasOriginal)

    def testReplaceFromArrayOriginalSaved(self):
        channel = Channel(np.random.randint(0, 255, (10, 10), dtype=np.uint8).T)
        channel.replaceFromArray(np.random.randint(0, 255, (11, 11), dtype=np.uint8).T)
        self.assertTrue(channel.hasOriginal)

    def testReplaceFromArrayException(self):
        channel = Channel(np.random.randint(0, 255, (10, 10), dtype=np.uint8).T)
        with self.assertRaises(AssertionError):
            channel.replaceFromArray(np.array([1, 2, 3]))

    def testReplaceFromArrayNewValues(self):
        array = np.random.randint(0, 255, (10, 10), dtype=np.uint8)
        channel = Channel(np.random.randint(0, 255, (100, 100), dtype=np.uint8).T)
        channel.replaceFromArray(array.T)
        self.assertTrue(np.array_equal(channel.pixels, array.T))

    def testGetShannonEntropyArbitraryBase(self):
        def entropy(array, base):
            _, counts = np.unique(array, return_counts=True)
            probArray = counts / np.sum(counts)
            logArray = np.log(probArray) / np.log(base)
            entropy = -np.sum(probArray * logArray)
            return entropy

        base = 0
        while base <= 0:
            baseCoeff = np.random.randint(1, 10, size=(1,))
            base = np.random.rand() * baseCoeff
        channel = Channel(np.random.randint(1, 255, (100, 100), dtype=np.uint8).T)
        channelEntropyMedthod = channel.getShannonEntropy(base)
        testEntropy = entropy(channel.pixels, base)
        self.assertAlmostEqual(testEntropy, channelEntropyMedthod)

    def testGetExtrema(self):
        array = np.arange(0, 25, dtype=np.uint8).reshape((5, 5))
        channel = Channel(array.T)
        self.assertTupleEqual(channel.getExtrema(), (0, 24))

    def testGetMedian(self):
        array = np.arange(0, 100, dtype=np.uint8)
        np.random.shuffle(array)
        channel = Channel(array.reshape((10, 10)).T)
        self.assertEqual(channel.getMedian(), 49.5)

    def testPixelsOfIntensityOnTuple(self):
        array = np.ones((100, 100)) * 0.236
        i, j = np.random.randint(0, 100, (2,))
        array[i, j] = 0.56
        channel = Channel(array.T)
        self.assertListEqual([(j, i)], channel.getPixelsOfIntensity(0.56))

    def testPixlesOfIntensityRandomNumberOfTuple(self):
        import operator
        nbOfTuples = np.random.randint(1, 100)
        listOfTuples = []
        array = np.ones((132, 200)) * 0.14
        for _ in range(nbOfTuples):
            i, j = np.random.randint(0, 132), np.random.randint(0, 200)
            array[i, j] = 0.001
            listOfTuples.append((j, i))
        channel = Channel(array.T)
        listOfTuples = list(set(listOfTuples))
        listOfTuples.sort(key=operator.itemgetter(0, 1))
        self.assertListEqual(listOfTuples, channel.getPixelsOfIntensity(0.001))

    def testGetMinimumIndicesOneValue(self):
        array = np.ones((100, 100))
        i, j = np.random.randint(0, 100, (2,))
        array[i, j] = 0
        channel = Channel(array.T)
        self.assertListEqual([(j, i)], channel.getMinimum())

    def testGetMinimumIndicesRandomNumberOfValues(self):
        import operator
        nbOfTuples = np.random.randint(1, 100)
        listOfTuples = []
        array = np.ones((132, 200))
        for _ in range(nbOfTuples):
            i, j = np.random.randint(0, 132), np.random.randint(0, 200)
            array[i, j] = 0.99999
            listOfTuples.append((j, i))
        channel = Channel(array.T)
        listOfTuples = list(set(listOfTuples))
        listOfTuples.sort(key=operator.itemgetter(0, 1))
        self.assertListEqual(listOfTuples, channel.getMinimum())

    def testGetMaximumIndicesOneValue(self):
        array = np.zeros((100, 100))
        i, j = np.random.randint(0, 100, (2,))
        array[i, j] = 1
        channel = Channel(array.T)
        self.assertListEqual([(j, i)], channel.getMaximum())

    def testGetMaximumIndicesRandomNumberOfValues(self):
        import operator
        nbOfTuples = np.random.randint(1, 100)
        listOfTuples = []
        array = np.ones((132, 200))
        for _ in range(nbOfTuples):
            i, j = np.random.randint(0, 132), np.random.randint(0, 200)
            array[i, j] = 1.0001
            listOfTuples.append((j, i))
        channel = Channel(array.T)
        listOfTuples = list(set(listOfTuples))
        listOfTuples.sort(key=operator.itemgetter(0, 1))
        self.assertListEqual(listOfTuples, channel.getMaximum())

    def testConvolution(self):
        # FIXME: test result
        array = np.random.randint(low=0, high=255, size=(100, 200))
        kernel = [[-1, 0, 1], [1, 0, 1], [0, 1, 1]]
        channel = Channel(pixels=array).convolveWith(kernel)
        self.assertIsNotNone(channel)
        self.assertTrue(channel.pixels.shape == array.shape)

    def testXDerivative(self):
        array = np.array([[0, 0, 0], [1, 1, 1], [2, 2, 2]])
        expected = np.array([[0, 0, 0], [0, 0, 0], [0, 0, 0]])
        channel = Channel(pixels=array.T).getXAxisDerivative()
        self.assertIsNotNone(channel)
        self.assertTrue(channel.pixels.shape == array.shape)
        self.assertTrue(channel.pixels.all() == expected.all())

    def testYDerivative(self):
        array = np.array([[0, 1, 2], [0, 1, 2], [0, 1, 2]])
        expected = np.array([[0, 0, 0], [0, 0, 0], [0, 0, 0]])
        channel = Channel(pixels=array.T).getYAxisDerivative()
        self.assertIsNotNone(channel)
        self.assertTrue(channel.pixels.shape == array.shape)
        self.assertTrue(channel.pixels.all() == expected.all())

    def testAverage(self):
        array = np.array([[0, 1, 2], [0, 1, 2], [0, 1, 2]])
        expected = 1.0
        result = Channel(pixels=array.T).getAverageValueOfPixels()
        self.assertIsNotNone(channel)
        self.assertTrue(result == expected)

    def testStddev(self):
        array = np.array([[0, 1, 2], [0, 1, 2], [0, 1, 2]])
        channel = Channel(pixels=array.T).getStandardDeviation()
        self.assertIsNotNone(channel)

    @patch("matplotlib.pyplot.show", new=Mock())
    def testMultichannelDisplayNoColorMaps(self):
        listOfChannel = []
        nbChannel = np.random.randint(1, 10)
        for i in range(nbChannel):
            listOfChannel.append(Channel(np.random.randint(0, 255, (1000, 10000), np.uint8)))
        returnList = Channel.multiChannelDisplay(listOfChannel)
        self.assertListEqual(returnList, listOfChannel)

    @patch("matplotlib.pyplot.show", new=Mock())
    def testMultichannelDisplayNoColorMaps(self):
        listOfChannel = []
        listOfColorMaps = []
        nbChannel = np.random.randint(1, 10)
        for i in range(nbChannel):
            listOfChannel.append(Channel(np.random.randint(0, 255, (1000, 10000), np.uint8)))
            listOfColorMaps.append("gray")
        returnList = Channel.multiChannelDisplay(listOfChannel, listOfColorMaps)
        self.assertListEqual(returnList, listOfChannel)

    @patch("matplotlib.pyplot.show", new=Mock())
    def testMultichannelDisplayNoColorMaps(self):
        listOfChannel = []
        listOfColorMaps = ["gray"]
        nbChannel = np.random.randint(1, 10)
        for i in range(nbChannel):
            listOfChannel.append(Channel(np.random.randint(0, 255, (1000, 10000), np.uint8)))
        returnList = Channel.multiChannelDisplay(listOfChannel, listOfColorMaps)
        self.assertListEqual(returnList, listOfChannel)

    @patch("matplotlib.pyplot.show", new=Mock())
    def testMultichannelDisplayException(self):
        listOfChannel = []
        nbChannel = np.random.randint(1, 10)
        for i in range(nbChannel):
            listOfChannel.append(Channel(np.random.randint(0, 255, (1000, 10000), np.uint8)))
        listOfColorMaps = ["gray"] * (nbChannel + 1)
        with self.assertRaises(ValueError):
            Channel.multiChannelDisplay(listOfChannel, listOfColorMaps)

    def testNoMaskOnInit(self):
        array = np.array([[0, 1, 2], [0, 1, 2], [0, 1, 2]])
        channel = Channel(array.T)
        self.assertFalse(channel.hasMask)

    def testMaskFromThreshold(self):
        array = np.array([[0, 1, 2], [0, 1, 2], [0, 1, 2]])
        channel = Channel(array.T)
        channel.setMaskFromThreshold(1)
        self.assertTrue(channel.hasMask)
        self.assertTrue(channel.mask.pixels.all() == np.array([[0, 1, 1], [0, 1, 1], [0, 1, 1]]).all())

    def testMaskFromThreshold(self):
        array = np.array([[1, 0, 0, 0], [0, 2, 2, 0], [0, 0, 0, 3]])
        expectedMask = np.array([[1, 0, 0, 0], [0, 1, 1, 0], [0, 0, 0, 1]])
        channel = Channel(array.T)
        channel.setMaskFromThreshold(0.5)
        self.assertTrue(channel.hasMask)
        self.assertTrue(channel.mask.pixels.all() == expectedMask.all())

    def testLabelMask(self):
        array = np.array([[1, 0, 0, 0], [0, 2, 2, 0], [0, 0, 0, 3]])
        channel = Channel(array.T)
        channel.setMaskFromThreshold(1)
        channel.labelMaskComponents()

        expectedMask = np.array([[1, 0, 0, 0], [0, 1, 1, 0], [0, 0, 0, 1]])
        expectedComponents = np.array([[0, 0, 0, 0], [0, 1, 1, 0], [0, 0, 0, 2]])
        self.assertTrue(channel.labelledComponents.all() == expectedComponents.all())
        self.assertTrue(channel.numberOfComponents == 2)

    def testLabelWithoutMaskFail(self):
        array = np.array([[1, 0, 0, 0], [0, 2, 2, 0], [0, 0, 0, 3]])
        channel = Channel(array.T)
        with self.assertRaises(Exception):
            channel.labelMaskComponents()

    def testAnalyzeComponents(self):
        array = np.array([[1, 0, 0, 0], [0, 2, 2, 0], [0, 0, 0, 3]])
        channel = Channel(array.T)
        channel.setMaskFromThreshold(1)
        channel.labelMaskComponents()
        properties = channel.analyzeComponents()
        self.assertTrue(channel.numberOfComponents == 2)
        self.assertIsNotNone(properties)

    def testAnalyzeComponentsException(self):
        channel = Channel(np.random.randint(1, 255, (100, 100), dtype=np.uint8))
        with self.assertRaises(ValueError):
            channel.analyzeComponents()

    def testFilterNoise(self):
        array = np.array([[1, 0, 0, 0], [0, 2, 2, 0], [0, 0, 0, 3]])
        channel = Channel(array.T)
        channel.filterNoise()

    def testThreshold(self):
        array = np.array([[1, 0, 0, 0], [0, 2, 2, 0], [0, 0, 0, 3]])
        channel = Channel(array.T)
        channel.threshold(value=1.5)

    # def testSaveComponents(self):
    #     array = np.array([[1, 0, 0, 0],[0, 2,2, 0],[0, 0,0, 3]])
    #     channel = Channel(array)
    #     channel.setMaskFromThreshold(1)
    #     channel.labelMaskComponents()
    #     channel.analyzeComponents()
    #     channel.saveComponentsStatistics("/tmp/test.json")

    def testRepr(self):
        array = np.random.randint(0, 255, (1000, 1000), dtype=np.uint8).T
        channel = Channel(array)
        self.assertEqual(str(channel), repr(channel))

    def testSetMaskNotBinary(self):
        with self.assertRaises(NotImplementedError):
            mask = np.ones((1000, 1000), dtype=float) * 1E-9
            array = np.random.randint(0, 255, (1000, 1000), dtype=np.uint8).T
            channel = Channel(array)
            channel.setMask(Channel(mask))

    def testSetMask(self):
        mask = np.ones((1000, 1000), dtype=np.uint8)
        array = np.random.randint(0, 255, (1000, 1000), dtype=np.uint8).T
        channel = Channel(array)
        channel.setMask(Channel(mask))
        self.assertTrue(channel.hasMask)

    def testSetMaskFromThresholdNone(self):
        with self.assertRaises(NotImplementedError):
            array = np.random.randint(0, 255, (1000, 1000), dtype=np.uint8).T
            channel = Channel(array)
            channel.setMaskFromThreshold(None)

    def testApplyConvolutionSaveOriginal(self):
        array = np.random.randint(0, 255, (1000, 1000), dtype=np.uint8).T
        channel = Channel(array)
        self.assertFalse(channel.hasOriginal)
        channel.applyConvolution([[0, 0, 1], [1, 0, 0]])
        self.assertTrue(channel.hasOriginal)

    def testApplyConvolutionNewValues(self):
        array = np.random.rand(1000, 1000).T
        channel = Channel(array)
        channelCopy = channel.copy()
        channel.applyConvolution([[0, 0, 1], [0, 0, 1], [0, 0, 1]])
        self.assertNotEqual(channel, channelCopy)

    def testApplyXDerivative(self):
        array = np.random.rand(1000, 1000).T
        channel = Channel(array)
        channelCopy = channel.copy()
        channel.applyXDerivative()
        self.assertNotEqual(channel, channelCopy)

    def testApplyYDerivative(self):
        array = np.random.rand(1000, 1000).T
        channel = Channel(array)
        channelCopy = channel.copy()
        channel.applyYDerivative()
        self.assertNotEqual(channel, channelCopy)

    def testApplyGaussianFilter(self):
        array = np.sin(np.array([[i * np.pi / 100 for i in range(100)]] * 100))
        sigma = np.random.randint(1, 6) * np.random.rand(1) + 0.0001
        channel = Channel(array)
        channelCopy = channel.copy()
        channel.applyGaussianFilter(sigma[0])
        self.assertNotEqual(channel, channelCopy)

    def testApplyThresholdingNoValue(self):
        array = np.random.randint(0, 254, (1000, 1000), dtype=np.uint8).T
        channel = Channel(array)
        channel.applyThresholding()
        self.assertTrue(channel.isBinary)

    def testApplyThresholding(self):
        array = np.random.rand(1000, 1000).T
        channel = Channel(array)
        channel.applyThresholding(0.05)
        self.assertTrue(channel.isBinary)

    def testApplyIsodataThresholding(self):
        array = np.random.rand(1000, 1000)
        channel = Channel(array)
        otherChannel = channel.getIsodataThresholding()
        channel.applyIsodataThresholding()
        self.assertEqual(channel, otherChannel)
        self.assertTrue(channel.isBinary)

    def testApplyOtsuThresholding(self):
        array = np.random.rand(1000, 1000)
        channel = Channel(array)
        otherChannel = channel.getOtsuThresholding()
        channel.applyOtsuThresholding()
        self.assertEqual(channel, otherChannel)
        self.assertTrue(channel.isBinary)

    def testApplyOpeningNotBinary(self):
        array = np.random.randint(0, 255, (1000, 1000), dtype=np.uint8)
        channel = Channel(array)
        otherChannel = channel.getOpening(5)
        channel.applyOpening(5)
        self.assertEqual(channel, otherChannel)

    def testApplyOpeningBinary(self):
        array = np.random.randint(0, 2, (1000, 1000), dtype=np.uint8)
        channel = Channel(array)
        otherChannel = channel.getBinaryOpening(9)
        channel.applyOpening(9)
        self.assertEqual(channel, otherChannel)

    def testApplyNdImageBinClosingNotBinary(self):
        array = np.random.rand(100, 1000)
        channel = Channel(array)
        with self.assertRaises(TypeError):
            channel.applyNdImageBinaryClosing()

    def testApplyNdImageBinClosingNoneSize(self):
        array = np.random.rand(1000, 1000)
        channel = Channel(array)
        channel.applyThresholding(channel.getAverageValueOfPixels())
        channel.applyNdImageBinaryClosing()
        self.assertFalse(np.array_equal(channel.originalPixels, channel.pixels))

    def testApplyNdImageBinClosing(self):
        array = np.random.rand(1000, 1000)
        channel = Channel(array)
        channel.applyThresholding(channel.getAverageValueOfPixels())
        channel.applyNdImageBinaryClosing(9)
        self.assertFalse(np.array_equal(channel.originalPixels, channel.pixels))

    def testApplyNdImageBinOpeningNotBinary(self):
        array = np.random.rand(100, 1000)
        channel = Channel(array)
        with self.assertRaises(TypeError):
            channel.applyNdImageBinaryOpening()

    def testApplyNdImageBinOpeningNoneSize(self):
        array = np.random.rand(1000, 1000)
        channel = Channel(array)
        channel.applyThresholding(channel.getAverageValueOfPixels())
        channel.applyNdImageBinaryOpening()
        self.assertFalse(np.array_equal(channel.originalPixels, channel.pixels))

    def testApplyNdImageBinOpening(self):
        array = np.random.rand(1000, 1000)
        channel = Channel(array)
        channel.applyThresholding(channel.getAverageValueOfPixels())
        channel.applyNdImageBinaryOpening(9)
        self.assertFalse(np.array_equal(channel.originalPixels, channel.pixels))

    def testThresholdNoneValue(self):
        array = np.random.rand(1000, 1000)
        channel = Channel(array)
        channel.threshold(None)
        self.assertTrue(channel.isBinary)

    def testApplyErosion(self):
        array = np.random.randint(0, 255, (1000, 1000), dtype=np.uint8)
        channel = Channel(array)
        channel.applyErosion()
        self.assertFalse(np.array_equal(channel.originalPixels, channel.pixels))

    def testApplyNoiseFilterWithErosionAndDilation(self):
        array = np.random.rand(1000, 1000)
        channel = Channel(array)
        channel.applyNoiseFilterWithErosionDilation()
        self.assertFalse(np.array_equal(channel.originalPixels, channel.pixels))

    def testGetBinaryOpeningNotBinary(self):
        array = np.random.randint(2, 255, (1000, 1000), dtype=np.uint8)
        channel = Channel(array)
        with self.assertRaises(NotBinaryImageException):
            channel.getBinaryOpening()

    def testGetBinaryClosingNotBinary(self):
        array = np.random.randint(2, 255, (1000, 1000), dtype=np.uint8)
        channel = Channel(array)
        with self.assertRaises(NotBinaryImageException):
            channel.getBinaryClosing()

    def testGetConnectedComponentsNotBinary(self):
        array = np.random.randint(2, 255, (1000, 1000), dtype=np.uint8)
        channel = Channel(array)
        with self.assertRaises(NotBinaryImageException):
            channel.getConnectedComponents()

    def testGetConnectedComponents(self):
        array = np.array([[1, 1, 1, 0, 0, 1, 1], [1, 1, 1, 1, 0, 1, 1], [1, 1, 1, 0, 0, 1, 1], [1, 1, 1, 0, 1, 1, 1]],
                         dtype=bool)
        channel = Channel(array)
        tupleConnectedComponents = channel.getConnectedComponents()
        # Label array equality
        self.assertTrue(np.array_equal(tupleConnectedComponents[0].pixels, np.array(
            [[1, 1, 1, 0, 0, 2, 2], [1, 1, 1, 1, 0, 2, 2], [1, 1, 1, 0, 0, 2, 2], [1, 1, 1, 0, 2, 2, 2]],
            dtype=np.uint8)))
        # Number of components
        self.assertEqual(tupleConnectedComponents[1], 2)
        # Sizes of each component
        self.assertListEqual(tupleConnectedComponents[-1].tolist(), [0, 13, 9])

    def testDistanceTransformNotBinary(self):
        array = np.random.randint(0, 2, (1000, 1000), dtype=np.uint8)
        channel = Channel(array).getEntropyFilter(3)
        with self.assertRaises(NotBinaryImageException):
            channel.getDistanceTransform()

    def testDistanceTransformIndicesReturn(self):
        array = np.zeros((5, 5))
        array[2, 2] = 1
        channel = Channel(array)
        distanceTransformStuff = channel.getDistanceTransform(True)
        self.assertTrue(np.array_equal(distanceTransformStuff[0], array))
        self.assertTrue(np.array_equal(distanceTransformStuff[1][-1],
                                       [[0, 1, 2, 3, 4], [0, 1, 2, 3, 4], [0, 1, 1, 3, 4], [0, 1, 2, 3, 4],
                                        [0, 1, 2, 3, 4]]))
        self.assertTrue(np.array_equal(distanceTransformStuff[1][0],
                                       np.array([[0, 1, 2, 3, 4], [0, 1, 2, 3, 4], [0, 1, 2, 3, 4], [0, 1, 2, 3, 4],
                                                 [0, 1, 2, 3, 4]]).T))

    def testDistanceTransformNoIndices(self):
        array = np.array(
            [[1, 1, 0, 1, 0, 0], [1, 1, 1, 1, 1, 1], [1, 1, 1, 1, 1, 1], [0, 0, 1, 0, 0, 1], [1, 1, 0, 1, 1, 1],
             [0, 0, 1, 0, 0, 0]])
        distanceTransform = np.array(
            [[2, 1, 0, 1, 0, 0], [2, 2 ** 0.5, 1, 2 ** 0.5, 1, 1], [1, 1, 2 ** 0.5, 1, 1, 2 ** 0.5], [0, 0, 1, 0, 0, 1],
             [1, 1, 0, 1, 1, 1], [0, 0, 1, 0, 0, 0]])
        channel = Channel(array)
        self.assertTrue(np.array_equal(channel.getDistanceTransform(False), distanceTransform))

    @patch("matplotlib.pyplot.show", new=Mock())
    def testWatershedSegmentation4Connect(self):
        x, y = np.indices((1000, 1000))
        x1, y1, x2, y2 = 500, 502, 190, 360
        r1, r2 = 250, 175
        mask_circle1 = (x - x1) ** 2 + (y - y1) ** 2 < r1 ** 2
        mask_circle2 = (x - x2) ** 2 + (y - y2) ** 2 < r2 ** 2
        array = np.logical_or(mask_circle1, mask_circle2)
        noise = np.random.normal(0, 0.11, array.shape)
        array = np.clip(array + noise, 0, 1)
        channel = Channel(array)
        watershedResults = channel.watershedSegmentation(0.5)
        maskChannel = watershedResults[0]
        uniqueValues = np.unique(maskChannel.pixels)
        self.assertListEqual(uniqueValues.tolist(), [0, 1, 2])
        self.assertEqual(watershedResults[-1], 2)

    @patch("matplotlib.pyplot.show", new=Mock())
    def testWatershedSegmentation8Connect(self):
        x, y = np.indices((1000, 1000))
        x1, y1, x2, y2 = 700, 502, 190, 360
        r1, r2 = 250, 175
        mask_circle1 = (x - x1) ** 2 + (y - y1) ** 2 < r1 ** 2
        mask_circle2 = (x - x2) ** 2 + (y - y2) ** 2 < r2 ** 2
        array = np.logical_or(mask_circle1, mask_circle2)
        channel = Channel(array.astype(np.uint8))
        watershedResults = channel.watershedSegmentation(0, use4Connectivity=False)
        maskChannel = watershedResults[0]
        uniqueValues = np.unique(maskChannel.pixels)
        self.assertListEqual(uniqueValues.tolist(), [0, 1, 2])
        self.assertEqual(watershedResults[-1], 2)
        m1 = mask_circle1.astype(np.uint8)
        m1[mask_circle1] = 2
        m1[~mask_circle1] = 0
        m2 = mask_circle2.astype(np.uint8)
        m2[mask_circle2] = 1
        m2[~mask_circle2] = 0
        totalMask = m2 + m1
        self.assertTrue(np.array_equal(totalMask, maskChannel.pixels))


class TestChannelSpectralFiltering(env.DCCLabTestCase):

    def testFourierTransform(self):
        def fourierTransform(array):
            returnArray = np.zeros_like(array, dtype=complex)
            m, n = array.shape
            for k in range(m):
                for l in range(n):
                    sum_ = 0
                    for i in range(m):
                        for j in range(n):
                            sum_ += array[i, j] * np.exp(-1j * 2 * np.pi * ((k * i) / m + (l * j) / n))
                    returnArray[k, l] = sum_
            return returnArray

        array = np.arange(0, 28).reshape((7, 4))
        channel = Channel(array)
        fftChannel = channel.fourierTransform(False)
        fftArray = fourierTransform(array)
        self.assertTrue(np.allclose(fftChannel, fftArray))

    def testFourierTransformShift(self):
        shape = (4, 3)
        array = np.random.randint(0, 1000, shape, dtype=np.uint16)
        channel = Channel(array)
        centerY, centerX = shape[0] // 2, shape[1] // 2
        fftChannelShift = channel.fourierTransform()
        fftChannel = channel.fourierTransform(False)
        self.assertFalse(np.array_equal(fftChannelShift, fftChannel))
        self.assertEqual(fftChannelShift[centerY, centerX], fftChannel[0, 0])

    def testHighPassFilterRectMask(self):
        image = Image(path=Path(self.dataDir / "testCziFile.czi"))
        channel = image.channels[0]
        fftChannel = channel.applyHighPassFilterFromRectangularMask(30)
        self.assertFalse(np.allclose(channel.pixels, fftChannel.pixels))

    def testLowPassFilterRectMask(self):
        image = Image(path=Path(self.dataDir / "testCziFile.czi"))
        channel = image.channels[0]
        fftChannel = channel.applyLowPassFilterFromRectangularMask(40)
        self.assertFalse(np.allclose(channel.pixels, fftChannel.pixels))

    def testCreatXYGridsAllOdd(self):
        nbRows = 3
        nbCols = 5
        array = np.ones((nbRows, nbCols))
        x, y = Channel.createXYGridsFromArray(array, False)
        row = [i for i in range(nbCols)]
        handComputedX = np.array([row] * nbRows)
        column = [i for i in range(nbRows)]
        handComputedY = np.array([column] * nbCols).T
        self.assertTrue(np.array_equal(x, handComputedX))
        self.assertTrue(np.array_equal(y, handComputedY))

    def testCreateXYGridsOneOdd(self):
        nbRows = 8
        nbCols = 5
        array = np.ones((nbRows, nbCols))
        x, y = Channel.createXYGridsFromArray(array, False)
        row = [i for i in range(nbCols)]
        handComputedX = np.array([row] * nbRows)
        column = [i for i in range(nbRows)]
        handComputedY = np.array([column] * nbCols).T
        self.assertTrue(np.array_equal(x, handComputedX))
        self.assertTrue(np.array_equal(y, handComputedY))

    def testCreateXYGridsAllEven(self):
        nbRows = 8
        nbCols = 10
        array = np.ones((nbRows, nbCols))
        x, y = Channel.createXYGridsFromArray(array, False)
        row = [i for i in range(nbCols)]
        handComputedX = np.array([row] * nbRows)
        column = [i for i in range(nbRows)]
        handComputedY = np.array([column] * nbCols).T
        self.assertTrue(np.array_equal(x, handComputedX))
        self.assertTrue(np.array_equal(y, handComputedY))

    def testCreateXYGridsAllOddOriginAtCenter(self):
        array = np.ones((5, 5))
        x, y = Channel.createXYGridsFromArray(array)
        handComputedX = np.array([[-2] * 5, [-1] * 5, [0] * 5, [1] * 5, [2] * 5]).T
        handComputedY = np.flipud(handComputedX.T)
        self.assertTrue(np.array_equal(x, handComputedX))
        self.assertTrue(np.array_equal(y, handComputedY))

    def testCreateXYGridsOneOddOriginAtCenter(self):
        array = np.ones((5, 6))
        x, y = Channel.createXYGridsFromArray(array)
        handComputedX = np.array([[-3] * 5, [-2] * 5, [-1] * 5, [0] * 5, [1] * 5, [2] * 5]).T
        handComputedY = np.flipud(np.array([np.arange(-2, 3)] * 6).T)
        self.assertTrue(np.array_equal(x, handComputedX))
        self.assertTrue(np.array_equal(y, handComputedY))

    def testCreateXYGridsAllEvenOriginAtCenter(self):
        array = np.ones((6, 6))
        x, y = Channel.createXYGridsFromArray(array)
        handComputedX = np.array([[-3] * 6, [-2] * 6, [-1] * 6, [0] * 6, [1] * 6, [2] * 6]).T
        handComputedY = np.flipud(np.array([np.arange(-2, 4)] * 6).T)
        self.assertTrue(np.array_equal(x, handComputedX))
        self.assertTrue(np.array_equal(y, handComputedY))

    def testCreateGaussianMask(self):
        array = np.ones((3, 3))
        xy = Channel.createXYGridsFromArray(array)
        mask = Channel.createGaussianMask(xy, 1 / np.sqrt(2))
        e = np.exp
        handComputedMask = np.array([[e(-2), e(-1), e(-2)], [e(-1), e(0), e(-1)], [e(-2), e(-1), e(-2)]])
        self.assertTrue(np.allclose(mask, handComputedMask))

    def testCreateSigmoidMask(self):
        array = np.ones((3, 3))
        xy = Channel.createXYGridsFromArray(array)
        radius = 1
        mask = Channel.createSigmoidMask(xy, radius)

        def sigmoid(expArg: float) -> float:
            return 1 / (1 + np.exp(-expArg))

        handComputedMask = np.array(
            [[sigmoid(1 - 2 ** (1 / 2)), 1 / 2, sigmoid(1 - 2 ** (1 / 2))], [1 / 2, sigmoid(1), 1 / 2],
             [sigmoid(1 - 2 ** (1 / 2)), 1 / 2, sigmoid(1 - 2 ** (1 / 2))]])
        self.assertTrue(np.allclose(mask, handComputedMask))

    def testPowerSpectrum(self):
        image = Image(path=Path(self.dataDir / "testCziFile.czi"))
        channel = image.channels[-1]
        fftChannel = np.fft.fft2(channel.pixels)
        fftShiftChannel = np.fft.fftshift(fftChannel)
        amplitude = np.abs(fftShiftChannel) ** 2
        self.assertTrue(np.array_equal(channel.powerSpectrum(), amplitude / np.sum(amplitude)))

    def testPowerSpectrumValues(self):
        array = np.array([[i * 2 * np.pi / 8 for i in range(30)]] * 30)
        values = (np.sin(array) + 1) * 255 / 2
        channel = Channel(values.astype(np.uint8) + values.astype(np.uint8).T)
        centerY, centerX = channel.shape[1] // 2, channel.shape[0] // 2
        ps = channel.powerSpectrum()
        sumToMultiply = np.sum(
            np.abs(np.fft.fftshift(np.fft.fft2(values.astype(np.uint8) + values.astype(np.uint8).T))) ** 2)
        # Check if center value is the DC component (after sqrt and normalization)
        self.assertAlmostEqual(np.sqrt(ps[centerY, centerX] * sumToMultiply),
                               np.sum(channel.pixels))

    def testPowerSpectrumMaxValueInCenter(self):
        oddXodd = Channel(np.arange(0, 25).reshape((5, 5)).T)
        oddXeven = Channel(np.arange(0, 20).reshape((5, 4)).T)
        evenXeven = Channel(np.arange(0, 36).reshape((6, 6)).T)
        evenXodd = Channel(np.arange(0, 20).reshape((4, 5)).T)
        listPS = [oddXodd.powerSpectrum(), oddXeven.powerSpectrum(), evenXeven.powerSpectrum(),
                  evenXodd.powerSpectrum()]
        for ps in listPS:
            centerX, centerY = ps.shape[0] // 2, ps.shape[1] // 2
            self.assertEqual(ps.max(), ps[centerX, centerY], msg=ps.shape)

    def testAzimuthalAverage(self):
        array = np.array([[2, 2, 2, 2], [2, 1, 1, 1], [2, 1, 0, 1], [2, 1, 1, 1]], dtype=np.uint8)
        azmAvg = Channel.azimuthalAverage(array).tolist()
        self.assertListEqual(azmAvg, (
                np.array([0 * 1 / 1, 1 * 8 / 8, 2 * 7 / 7]) / np.sum([0 * 1 / 1, 1 * 8 / 8, 2 * 7 / 7])).tolist())
        self.assertAlmostEqual(np.sum(azmAvg), 1)

    def testAngularAverage(self):
        array = [[3 - abs(i)] * 8 for i in range(-2, 3)]
        array = np.concatenate((array, array))
        angAvg, index = Channel.angularAverage(array)
        tempIndex = np.array([[79, 68, 59], [76, 63, 53], [72, 56, 45], [63, 45, 34], [45, 27, 18], [0, 0, 0]])
        supposedIndex = np.concatenate((np.array([[129, 135, 143, 153, 166, 180]]).T, 180 - np.fliplr(tempIndex),
                                        np.array([[90, 90, 90, 90, 90, 180]]).T, tempIndex), 1)
        self.assertListEqual(np.unique(supposedIndex).tolist(), index.tolist())
        supposedAngAvg = [1, 1, 1, 2, 2, 2, 3, 1, 2, 1, 3, 2, 1, 1.8, 1, 2, 3, 1, 2, 1, 3, 2, 1, 2, 3, 2, 1.5, 1, 1, 1]
        self.assertListEqual(angAvg.tolist(), (np.array(supposedAngAvg) / np.sum(supposedAngAvg)).tolist())
        self.assertAlmostEqual(np.sum(angAvg), 1)


if __name__ == '__main__':
    unittest.main()
