import env
from dcclab import *
from unittest.mock import Mock, patch
import numpy as np
import unittest


class TestZStack(env.DCCLabTestCase):

    def setUp(self):
        self.depth = 5
        self.grayStack = np.zeros((10, 10, 1, self.depth))
        self.grayStack[1:9, 1:9, 0, :] = 0.5
        self.grayStack[3:7, 3:7, 0,  1:self.depth-1] = 1
        self.zStack = ZStack(imagesArray=self.grayStack)

    def testImageCollectionFrom4DArray(self):
        collection = ImageCollection(imagesArray=self.grayStack)

        self.assertTrue(len(collection) == self.depth)
        self.assertTrue(collection[0].shape == (10, 10, 1))

    def testZStackFrom4DArray(self):
        self.assertTrue(len(self.zStack) == self.depth)
        self.assertTrue(self.zStack[0].shape == (10, 10, 1))

    def testZStackFromBad4DArray(self):
        imageArrays = [self.grayStack[:, :, :, i] for i in range(self.grayStack.shape[3])]
        imageArrays[0] = np.zeros((2, 2, 1))

        imageList = [Image(imageData=imageArray) for imageArray in imageArrays]

        with self.assertRaises(ValueError):
            ZStack(imageList)

    @unittest.skip("Need a small sample stack test folder. ")
    def testZStackFromFolder(self):
        # TODO
        pass

    def testImagesAreSimilar(self):
        self.assertTrue(self.zStack.imagesAreSimilar)

    def testImagesAreNotSimilar(self):
        self.zStack[0].replaceFromArray(np.zeros((2, 2, 1)))
        self.assertFalse(self.zStack.imagesAreSimilar)

    def testNumberOfChannels(self):
        self.assertTrue(self.zStack.numberOfChannels, 1)

    def testShape(self):
        self.assertTrue(self.zStack.shape == (10, 10, 1, 5))

    def testLength(self):
        self.assertTrue(len(self.zStack) == 5)

    def testAsArray(self):
        stackArray = self.zStack.asArray()

        self.assertIsInstance(stackArray, np.ndarray)
        self.assertTrue(stackArray.shape == (10, 10, 1, 5))

    def testAsChannelArray(self):
        stackArray = self.zStack.asChannelArray(channel=0)

        self.assertIsInstance(stackArray, np.ndarray)
        self.assertTrue(stackArray.shape == (10, 10, 5))

    def testAsOriginalArrayNotModified(self):
        originalStack = self.zStack.asOriginalArray()

        self.assertTrue(np.array_equal(originalStack, self.grayStack))

    def testAsOriginalChannelArrayNotModified(self):
        originalStack = self.zStack.asOriginalChannelArray(0)

        self.assertTrue(np.array_equal(originalStack, self.grayStack[:, :, 0, :]))

    def testApply3DFilterProcessDimensionNotDefined(self):
        self.zStack.processIn3D = None

        with self.assertRaises(ZStackProcessDimensionIsNotDefined):
            self.zStack.apply3DFilter(ndimage.grey_opening, size=4)

    def testApply3DFilter(self):
        self.zStack.apply3DFilter(ndimage.grey_opening, size=4)

        self.assertFalse(np.array_equal(self.zStack.asArray(), self.grayStack))

    def testAsOriginalArray(self):
        self.zStack.apply3DFilter(ndimage.grey_opening, size=4)
        originalArray = self.zStack.asOriginalArray()

        self.assertIsInstance(originalArray, np.ndarray)
        self.assertTrue(np.array_equal(originalArray, self.grayStack))
        self.assertTrue(originalArray.shape == (10, 10, 1, 5))

    def testAsOriginalChannelArray(self):
        self.zStack.apply3DFilter(ndimage.grey_opening, size=4)
        originalArray = self.zStack.asOriginalChannelArray(channel=0)

        self.assertIsInstance(originalArray, np.ndarray)
        self.assertTrue(np.array_equal(originalArray, self.grayStack[:, :, 0, :]))
        self.assertTrue(originalArray.shape == (10, 10, 5))

    def testApplyOpening(self):
        self.zStack.applyOpening(size=4)

        self.assertFalse(np.array_equal(self.zStack.asArray(), self.grayStack))

    def testApplyOpeningProcessIn2D(self):
        self.zStack.processIn3D = False

        self.zStack.applyOpening(size=4)

        self.assertTrue(np.array_equal(self.zStack.asArray(), self.grayStack))

    def testApplyClosing(self):
        self.zStack.applyClosing(size=4)

        self.assertFalse(np.array_equal(self.zStack.asArray(), self.grayStack))

    def testApplyErosion(self):
        self.zStack.applyErosion(size=4)

        self.assertFalse(np.array_equal(self.zStack.asArray(), self.grayStack))

    def testApplyDilation(self):
        self.zStack.applyDilation(size=4)

        self.assertFalse(np.array_equal(self.zStack.asArray(), self.grayStack))

    def testApplyNoisefilter(self):
        self.zStack.applyNoiseFilter()

        self.assertFalse(np.array_equal(self.zStack.asArray(), self.grayStack))

    def testApplyNoiseFilterProcessDimensionNotDefined(self):
        self.zStack.processIn3D = None

        with self.assertRaises(ZStackProcessDimensionIsNotDefined):
            self.zStack.applyNoiseFilterWithErosionDilation()

    def testApplyNoiseFilterWithErosionDilation(self):
        self.zStack.applyNoiseFilterWithErosionDilation()

        self.assertFalse(np.array_equal(self.zStack.asArray(), self.grayStack))

    def testApplyNoiseFilterBadAlgorithm(self):
        with self.assertRaises(NotImplementedError):
            self.zStack.applyNoiseFilter(algorithm="Nada")

    def testApplyNoiseFilterProcessIn2D(self):
        self.zStack.processIn3D = False

        self.zStack.applyNoiseFilter()

        self.assertTrue(np.array_equal(self.zStack.asArray(), self.grayStack))

    def testSetMaskFromThreshold(self):
        self.zStack.setMaskFromThreshold(self.grayStack.mean())

        self.assertTrue(self.zStack.hasMask)
        self.assertTrue(self.zStack[0][0].mask.pixels.max() == 1)

    def testGetChannelMaskArrayNotDefined(self):
        with self.assertRaises(AssertionError):
            maskArray = self.zStack.getChannelMaskArray(channel=0)

    def testGetChannelMaskArray(self):
        self.zStack.setMaskFromThreshold(self.grayStack.mean())
        onesRegion = np.ones((6, 6, self.depth-2))

        maskArray = self.zStack.getChannelMaskArray(channel=0)

        self.assertEqual(maskArray.shape, (10, 10, 5))
        self.assertTrue(maskArray.max() == 1)
        self.assertTrue(np.array_equal(maskArray[2:8, 2:8, 1:self.depth-1], onesRegion))

    def testApplyOpeningToMaskWithoutMask(self):
        with self.assertRaises(AssertionError):
            self.zStack.applyOpeningToMask()

    def testApplyOpeningToMask(self):  # Fixme: test image collection instead
        self.zStack.setMaskFromThreshold(self.grayStack.mean())
        originalMask = self.zStack.getChannelMaskArray(0)

        self.zStack.applyOpeningToMask()

        self.assertFalse(np.array_equal(originalMask, self.zStack.getChannelMaskArray(0)))

    def testApplyClosingToMask(self):
        self.zStack.setMaskFromThreshold(self.grayStack.mean())
        originalMask = self.zStack.getChannelMaskArray(0)

        self.zStack.applyClosingToMask(size=4)

        self.assertFalse(np.array_equal(originalMask, self.zStack.getChannelMaskArray(0)))

    def testLabelMaskComponentsWithoutMask(self):
        with self.assertRaises(AssertionError):
            self.zStack.labelMaskComponents()

    def testLabelMaskComponents(self):
        self.zStack.setMaskFromThreshold(self.grayStack.mean())
        self.zStack.labelMaskComponents()

        self.assertTrue(self.zStack.hasLabelledComponents)
        self.assertTrue(self.zStack[0][0].labelledComponents.max() == 1)

    def testComponentsPropertiesNotDefined(self):
        self.assertTrue(len(self.zStack.componentsProperties) == 0)

    def testLabellingSetComponentsProperties(self):
        self.zStack.setMaskFromThreshold(self.grayStack.mean())
        self.zStack.labelMaskComponents()

        nbOfObjects = self.zStack.componentsProperties["Channel 0"]["nbOfObjects"]

        self.assertTrue(nbOfObjects == 1)

    def testGetChannelLabelArrayNotDefined(self):
        with self.assertRaises(AssertionError):
            self.zStack.getChannelLabelArray(channel=0)

    def testGetChannelLabelArray(self):
        self.zStack.setMaskFromThreshold(self.grayStack.mean())
        self.zStack.labelMaskComponents()
        onesRegion = np.ones((6, 6, self.depth-2))

        labelArray = self.zStack.getChannelLabelArray(channel=0)

        self.assertTrue(np.array_equal(labelArray[2:8, 2:8, 1:self.depth-1], onesRegion))

    def testSetChannelLabelsFromArray(self):
        labelArray = np.zeros((10, 10, 5))

        self.zStack.channelLabelsFromArray(0, labelArray)

        self.assertTrue(np.array_equal(self.zStack.getChannelLabelArray(0), labelArray))

    def testAnalyzeComponents(self):
        self.zStack.setMaskFromThreshold(self.grayStack.mean())
        self.zStack.labelMaskComponents()

        self.zStack.analyzeComponents()
        channelComponentsDict = self.zStack.componentsProperties["Channel 0"]

        self.assertTrue(len(channelComponentsDict) == 7)
        self.assertTrue(channelComponentsDict["totalSize"] == 320)

    def testAnalyzeComponentsWithOriginal(self):
        self.zStack.filterNoise()
        self.zStack.setMaskFromThreshold(self.grayStack.mean())
        self.zStack.labelMaskComponents()

        self.zStack.analyzeComponents()
        channelComponentsDict = self.zStack.componentsProperties["Channel 0"]

        self.assertTrue(len(channelComponentsDict) == 7)
        self.assertTrue(channelComponentsDict["totalSize"] == 320)

    def testGetObjectsSize(self):
        maskArray = np.ones((2, 2))
        labelArray = maskArray.copy()

        objectsSize = self.zStack.getObjectsSize(maskArray, labelArray)

        self.assertTrue(len(objectsSize) == 1)
        self.assertTrue(objectsSize[0] == 4)

    def testGetObjectsMass(self):
        maskArray = np.ones((2, 2))
        originalArray = maskArray.copy()
        originalArray[0] = [0.5, 0.5]
        labelArray = maskArray.copy()

        objectsMass = self.zStack.getObjectsMass(originalArray, labelArray)

        self.assertTrue(len(objectsMass) == 1)
        self.assertTrue(objectsMass[0] == 3)

    def testGetObjectsCenterOfMass(self):
        maskArray = np.ones((2, 2))
        originalArray = maskArray.copy()
        labelArray = maskArray.copy()

        objectsCM = self.zStack.getObjectsCenterOfMass(originalArray, labelArray)

        self.assertTrue(len(objectsCM) == 1)
        self.assertTrue(objectsCM[0] == (0.5, 0.5))

    def testSaveComponentsProperties(self):
        self.zStack.setMaskFromThreshold(self.grayStack.mean())
        self.zStack.labelMaskComponents()
        self.zStack.analyzeComponents()

        filepath = Path(self.tmpDir / "testParams.json").__str__()
        self.zStack.saveComponentsProperties(filepath)
        self.assertTrue(os.path.exists(filepath))

        os.remove(filepath)

    def testSaveComponentsPropertiesToBadFileExtension(self):
        self.zStack.setMaskFromThreshold(self.grayStack.mean())
        self.zStack.labelMaskComponents()
        self.zStack.analyzeComponents()

        filepath = Path(self.tmpDir / "testParams.txt").__str__()
        self.zStack.saveComponentsProperties(filepath)
        self.assertTrue(os.path.exists(filepath + ".json"))

        os.remove(filepath + ".json")

    @unittest.skip("Cropping not tested: method will propably change.")
    def testAsk2DCropIndices(self):
        # fixme: careful with crop logic: maybe move to image
        pass

    @unittest.skip('')
    def testCrop4DArray(self):
        pass

    @unittest.skip('')
    def testCrop(self):
        pass

    @unittest.skip('')
    def testZStackFrom4DArrayCropAtInit(self):
        pass

    def testChannelStacksInMemory(self):
        self.zStack.setMaskFromThreshold(self.grayStack.mean())
        self.zStack.labelMaskComponents()

        stacksInMemory = self.zStack.channelStacksInMemory(channel=0)

        self.assertTrue(len(stacksInMemory) == 3)

    def testChannelStacksInMemoryOrdered(self):
        self.zStack.applyNoiseFilter()
        self.zStack.setMaskFromThreshold(self.grayStack.mean())
        self.zStack.labelMaskComponents()
        orderedKeys = ["Original ", "", "Mask ", "Label "]

        stacksInMemory = self.zStack.channelStacksInMemory(channel=0)

        self.assertTrue(len(stacksInMemory) == len(orderedKeys))
        for key, orderedKey in zip(stacksInMemory.keys(), orderedKeys):
            self.assertEqual(key, orderedKey)

    @patch("matplotlib.pyplot.show", new=Mock())
    def testShow(self):
        self.zStack.show(channel=0)
        # todo: test more indepth ?

    @patch("matplotlib.pyplot.show", new=Mock())
    def testShowAllChannelStacks(self):
        self.zStack.applyNoiseFilter()
        self.zStack.setMaskFromThreshold(self.grayStack.mean())
        self.zStack.labelMaskComponents()

        self.zStack.showAllStacks(channel=0)
        # todo: test more indepth ?

    @patch("matplotlib.pyplot.show", new=Mock())
    def testShowAllStacks(self):
        self.zStack.applyNoiseFilter()
        self.zStack.setMaskFromThreshold(self.grayStack.mean())
        self.zStack.labelMaskComponents()

        with self.assertRaises(NotImplementedError):
            self.zStack.showAllStacks()
