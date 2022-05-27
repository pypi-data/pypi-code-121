import env
from dcclab import *
from unittest.mock import Mock, patch
import unittest
import numpy as np
import re

class TestImageCollection(env.DCCLabTestCase):
    @classmethod
    def setUpClass(cls):
        super(TestImageCollection, cls).setUpClass()
        cls.largeImmutable = ImageCollection()
        for i in range(10):
            imageData = np.random.randint(low=0, high=255, size=(1024, 1024, 3))
            cls.largeImmutable.append(Image(imageData))
        cls.large = cls.largeImmutable

    """ https://hackernoon.com/timing-tests-in-python-for-fun-and-profit-1663144571 """
    # def setUp(self):
    #     # self.large = self.largeImmutable
    #     # self._started_at = time.time()

    # def tearDown(self):
    #     # elapsed = time.time() - self._started_at
    #     # print('{} ({}s)'.format(self.id(), round(elapsed, 2)))

    def testInit(self):
        self.assertIsNotNone(ImageCollection())

    def testInitWithPatternNoFile(self):
        coll = ImageCollection(pathPattern=self.dataFile(r'abc-(\d).tiff'))
        self.assertIsNotNone(coll)
        self.assertTrue(coll.images == [])

    def testTestFilesArePresent(self):
        pat = PathPattern(self.dataFile(r'test-(\d+).jpg'))
        self.assertTrue(pat.matchingFiles() == [self.dataFile('test-001.jpg'),
            self.dataFile('test-002.jpg'),self.dataFile('test-003.jpg')])

    def testInitWithPatternAndFiles(self):
        coll = ImageCollection(pathPattern=self.dataFile(r'test-(\d+).jpg'))
        self.assertIsNotNone(coll)
        self.assertTrue(coll.numberOfImages != 0)

    def testInitWithPattern(self):
        coll = ImageCollection(pathPattern=self.dataFile(r'abc-(\d).tiff'))
        self.assertIsNotNone(coll)

    def testInitWithImages(self):
        data = np.random.randint(low=0, high=255, size=(100, 200, 3))
        imgs = [Image(data)]
        self.assertIsNotNone(ImageCollection(imgs))

    def testInitWithGarbage(self):
        with self.assertRaises(Exception):
            self.assertIsNotNone(ImageCollection("string"))

    def testInitImageCollection(self):
        imgCollection = ImageCollection(pathPattern = self.dataFile(r"test-(\d+).jpg"))
        self.assertTrue(len(imgCollection) != 0)
        self.assertIsNotNone(imgCollection.images)
        self.assertTrue(imgCollection.numberOfImages > 0)

    def testFilterNoiseImageCollection(self):
        collection = ImageCollection()
        for i in range(100):
            imageData = np.random.randint(low=0, high=255, size=(100, 200, 3))
            collection.append(Image(imageData))
        collection.filterNoise()

    def testFilterNoiseImageCollection(self):
        collection = ImageCollection()
        for i in range(100):
            imageData = np.random.randint(low=0, high=255, size=(100, 200, 3))
            collection.append(Image(imageData))
        collection.threshold(value=128)

    def testThresholdLargeImageCollection(self):
        self.large.threshold(value=128)

    def testLargeImageCollectionAsArray(self):
        largeArray = self.large.asArray()

    def testMaskFromThreshold(self):
        self.large.setMaskFromThreshold(value=128)

    def testLabelComponents(self):
        self.large.setMaskFromThreshold(value=128)
        self.large.labelMaskComponents()
        self.large.analyzeComponents()

    def testValidConstructorEmpty(self):
        valid = True
        try:
            ImageCollection([])
        except AttributeError:
            valid = False

        self.assertTrue(valid)

    def testValidConstructorOneElement(self):
        array = np.ones((130, 145), dtype=np.int8)
        image = Image(array)
        collection = ImageCollection([image])
        self.assertIsInstance(collection, ImageCollection)

    def testValidConstructor100Elements(self):
        imageList = []
        for i in range(100):
            array = np.ones((256, 257), dtype=np.int8)
            array[i][i] = i
            image = Image(array)
            imageList.append(image)
        collection = ImageCollection(imageList)
        self.assertIsInstance(collection, ImageCollection)

    def testInvalidConstructor1Element(self):
        image = np.ones((10, 10))
        with self.assertRaises(NotImageException):
            ImageCollection([image])

    def testInvalidConstructor11Elements(self):
        imageList = []
        for i in range(10):
            array = np.ones((256, 257), dtype=np.int8)
            array[i][i] = i
            image = Image(array)
            imageList.append(image)
        imageList.append(np.ones((10, 10)))
        with self.assertRaises(NotImageException):
            ImageCollection(imageList)


class TestImageCollectionMethods(env.DCCLabTestCase):

    def setUp(self) -> None:
        self.imageList = []
        for i in range(12):
            array = (i+1)*np.ones((100,100,3), dtype=np.int8)
            image = Image(array)
            self.assertIsNotNone(image)
            self.imageList.append(image)
        self.collection = ImageCollection(self.imageList)
        self.assertIsNotNone(self.collection)
        self.assertTrue(self.collection.numberOfImages > 0)

    def testImageInCollectionInvalidImage(self):
        invalidImage = np.ones((256, 257), dtype=np.int8)
        self.assertFalse(self.collection.contains(invalidImage))

    def testImageNotInCollection(self):
        arrayNotInCollection = np.ones((256, 257), dtype=np.int8)
        arrayNotInCollection[0][0] = 0.00001
        imageNotInCollection = Image(arrayNotInCollection)
        self.assertFalse(self.collection.contains(imageNotInCollection))

    def testImageInCollection(self):
        imageInCollection = self.imageList[-1]
        self.assertTrue(self.collection.contains(imageInCollection))

    def testGetIndexOfInvalidImage(self):
        invalidImage = np.ones((256, 257), dtype=np.int8)
        index = self.collection.indexOf(invalidImage)
        self.assertIsNone(index)

    def testindexOfNotInCollection(self):
        arrayNotInCollection = np.ones((256, 257), dtype=np.int8)
        arrayNotInCollection[0][0] = 0.00001
        imageNotInCollection = Image(arrayNotInCollection)

        index = self.collection.indexOf(imageNotInCollection)
        self.assertIsNone(index)

    def testGetIndexImageInCollection(self):
        anImage = self.imageList[2]
        self.assertEqual(self.collection.indexOf(anImage), 2)

    def testAddInvalidImage(self):
        invalidImage = np.ones((256, 257), dtype=np.int8)
        with self.assertRaises(NotImageException):
            self.collection.append(invalidImage)

    def testAddImageAlreadyIn(self):
        existingImage = self.imageList[-1]
        with self.assertRaises(ImageAlreadyInCollectionException):
            self.collection.append(existingImage)

    def testAddImageNotAlreadyIn(self):
        newImage = Image(np.zeros((256, 257, 3), dtype=np.int8))
        self.assertIsNotNone(newImage)
        lastIndex = self.collection.numberOfImages - 1
        self.collection.append(newImage)
        self.assertEqual(self.collection.indexOf(newImage), lastIndex + 1)

    def testremoveAtOutOfBound(self):
        with self.assertRaises(IndexError):
            self.collection.removeAt(500)

    def testRemoveImageAtIndex(self):
        imageToRemove = self.imageList[-1]
        removedImage = self.collection[-1]
        self.collection.removeAt(-1)
        self.assertTrue(imageToRemove == removedImage)

    def testRemoveImageWithInvalidImage(self):
        invalidImage = np.ones((125, 12547), dtype=np.int8)
        with self.assertRaises(NotImageException):
            self.collection.remove(invalidImage)

    def testRemoveImageWithImageNotInCollection(self):
        arrayNotInStack = np.ones((256, 257), dtype=np.int8)
        arrayNotInStack[0][0] = 0.00001
        imageNotInStack = Image(arrayNotInStack)
        with self.assertRaises(ImageNotInCollectionException):
            self.collection.remove(imageNotInStack)

    def testRemoveImageWithImage(self):
        imageInStack = self.imageList[0]
        # IF anything is wrong, exception is thrown
        self.collection.remove(imageInStack)

    def testGetNumberOfImages(self):
        numberOfImages = len(self.imageList)
        self.assertEqual(self.collection.numberOfImages, numberOfImages)

    def testGetNumberOfImagesAddedImage(self):
        numberOfImages = len(self.imageList)
        imageNotAlreadyIn = Image(np.zeros((256, 257), dtype=np.int8))
        self.collection.append(imageNotAlreadyIn)
        self.assertEqual(self.collection.numberOfImages, numberOfImages + 1)

    def testGetNumberOfImagesRemovedImage(self):
        numberOfImages = len(self.imageList)
        self.collection.removeAt(0)
        self.assertEqual(self.collection.numberOfImages, numberOfImages - 1)

    def testImageCollectionAsNumpyArray(self):
        arrayFromCollection = self.collection.asArray()
        self.assertEqual(arrayFromCollection.ndim, 4)

    def testClearCollection(self):
        self.collection.clear()
        self.assertTrue(len(self.collection) == 0)

    # @patch("matplotlib.pyplot.show", new=Mock)
    # def testShowImages(self):
    #     nbOfImagesShown = self.collection.showAllSequentially()
    #     self.assertEqual(nbOfImagesShown, 5)

    def testIndexingOutOfBound(self):
        image = Image(np.ones((5, 5), dtype=np.int8))
        listOfImage = ImageCollection([image])
        with self.assertRaises(IndexError):
            listOfImage[2]

    def testIndexing(self):
        image = Image(np.ones((5, 5), dtype=np.int8))
        listOfImage = ImageCollection([image])
        self.assertTrue(listOfImage[0] == image)

    def testSaveCollection(self):
        self.collection.save(self.tmpFile('test-{0:03d}.gif'))
        self.collection.save(self.tmpFile('test-{0:03d}.png'))
        self.collection.save(self.tmpFile('test-{0:03d}.jpg'))
        self.collection.save(self.tmpFile('test-{0:03d}.tif'))

    def testCollectionDimension(self):
        self.assertTrue(self.collection.dimension == 1)
        self.assertTrue(self.collection.dimension == 1)

    def testCollectionShape(self):
        self.assertTrue(self.collection.shape == (len(self.collection),))

    def testCollectionReshape(self):
        self.assertTrue(self.collection.shape == (len(self.collection),))
        self.collection.reshape((3,4))
        self.assertTrue(self.collection.shape == (3,4))
        self.assertTrue(self.collection.dimension == 2)

    def testCollectionReshapeAccess(self):
        self.collection.reshape((3,4))
        self.assertIsNotNone(self.collection[(1,2)])

if __name__ == '__main__':
    unittest.main()
