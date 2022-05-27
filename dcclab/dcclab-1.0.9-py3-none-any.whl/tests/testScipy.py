import env
from scipy import ndimage, misc, sparse
import numpy as np
import unittest


class TestScipyFilters(env.DCCLabTestCase):
    """ Testing if scipy filters are dimension dependent """

    def setUp(self):
        """ Generating a list of random images. All images are different """
        self.imageList = [sparse.random(5, 5, density=0.5).A for i in range(10)]
        self.sampleStackArray = np.dstack(self.imageList)

    def testSampleStackSize(self):
        print(self.imageList[0].shape, self.imageList[0])
        self.assertTrue(self.sampleStackArray.shape == (5, 5, 10))

    def scipyWithZStack(self, scipyFilter):
        return scipyFilter(self.sampleStackArray, size=2)

    def scipyWithChannels(self, scipyFilter):
        erodedImages = []
        for image in self.imageList:
            erodedImages.append(scipyFilter(image, size=2))
        return np.dstack(erodedImages)

    def testOriginalsAreEqual(self):
        self.assertTrue(np.array_equal(self.sampleStackArray[:, :, 0], self.imageList[0]))
        self.assertTrue(np.array_equal(self.sampleStackArray, np.dstack(self.imageList)))

    def testFilteredWithClosingAreEqual(self):
        filteredZStack = self.scipyWithZStack(scipyFilter=ndimage.grey_closing)
        filteredChannels = self.scipyWithChannels(scipyFilter=ndimage.grey_closing)

        self.assertTrue(np.array_equal(filteredZStack, filteredChannels))

    def testFilteredWithErosionAreEqual(self):
        filteredZStack = self.scipyWithZStack(scipyFilter=ndimage.grey_erosion)
        filteredChannels = self.scipyWithChannels(scipyFilter=ndimage.grey_erosion)

        self.assertTrue(np.array_equal(filteredZStack, filteredChannels))


if __name__ == '__main__':
    unittest.main()
