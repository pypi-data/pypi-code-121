import env
from dcclab import *
import unittest
import numpy as np
from pathlib import Path, PureWindowsPath

class TestMATLABFile(env.DCCLabTestCase):

    def testInit(self):
        self.assertIsNotNone(MATLABFile(Path(self.dataDir / "test.mat")))

    def testInitWithVariable(self):
        self.assertIsNotNone(MATLABFile(Path(self.dataDir / "test.mat"), variable='image'))

    def testImageDataWithImageVariable(self):
        file = MATLABFile(Path(self.dataDir / "test.mat"), variable='image')
        data = file.imageDataFromPath()
        self.assertIsNotNone(data)
        self.assertTrue(isinstance(data, np.ndarray))
        self.assertEqual(data.ndim, 3)

    def testImageDataWithChannelVariable(self):
        file = MATLABFile(Path(self.dataDir / "test.mat"), variable='channel')
        data = file.imageDataFromPath()
        self.assertIsNotNone(data)
        self.assertTrue(isinstance(data, np.ndarray))
        self.assertEqual(data.ndim, 3)

    def testImageDataWithSomeVariable(self):
        file = MATLABFile(Path(self.dataDir / "test.mat"), variable='notAnImage')
        with self.assertRaises(ValueError):
            data = file.imageDataFromPath()

    def testImageDataWithoutVariableWithImageData(self):
        file = MATLABFile(Path(self.dataDir / "test.mat"))
        data = file.imageDataFromPath()
        self.assertIsNotNone(data)
        self.assertTrue(isinstance(data, np.ndarray))
        self.assertEqual(data.ndim, 3)

    def testImageDataWithoutVariableWithoutImageData(self):
        file = MATLABFile(Path(self.dataDir / "nothing.mat"))
        data = file.imageDataFromPath()
        self.assertIsNone(data)

    def testImageDataWithoutVariableWith2DChannelData(self):
        file = MATLABFile(Path(self.dataDir / "2dArray.mat"))
        data = file.imageDataFromPath()
        self.assertIsNotNone(data)
        self.assertTrue(isinstance(data, np.ndarray))
        self.assertEqual(data.ndim, 3)

    def testImageDataWithoutVariableWith2DChannelData(self):
        image = Image(path=Path(self.dataDir / "test.mat"))
        self.assertIsNotNone(image)
        self.assertIsNotNone(image.channels[0])
        pixels = image.channels[0].pixels
        self.assertTrue(isinstance(pixels, np.ndarray))
        self.assertEqual(pixels.ndim, 2)

if __name__ == '__main__':
    unittest.main()
