import env
import unittest
from dcclab.cziFile import CZIFile
from dcclab.DCCExceptions import *
import numpy as np
from pathlib import Path


class TestConstructor(env.DCCLabTestCase):

    def testValidCziFile(self):
        try:
            CZIFile(Path(self.dataDir / "testCziYX0Tiny.czi"))
        except InvalidFileFormatException:
            self.fail()

    def testInvalidNotCzi(self):
        with self.assertRaises(InvalidFileFormatException):
            CZIFile(Path(self.dataDir / "test.gif"))

    def testInvalidFileNotFound(self):
        with self.assertRaises(FileNotFoundError):
            CZIFile(Path(self.dataDir / "FileNotFound.czi"))

    def testInvalidZstackAndTimeSeries(self):
        with self.assertRaises(NotImplementedError):
            CZIFile(Path(self.dataDir / "testCziTSeries_ZStack.czi"))

    def testInvalidScenesAndTimeSeries(self):
        with self.assertRaises(NotImplementedError):
            CZIFile(Path(self.dataDir / "testCziTSeries_Scenes.czi"))

    def testInvalidScenesAndZStack(self):
        with self.assertRaises(NotImplementedError):
            CZIFile(Path(self.dataDir / "testCziScenes_ZStack.czi"))


class TestMethodsAndProperties(env.DCCLabTestCase):

    def testNumberOfChannels(self):
        czi2Channels = CZIFile(Path(self.dataDir / "testCziFile.czi"))
        cziOneChannel = CZIFile(Path(self.dataDir / "testOneChannel2Scenes.czi"))
        czi0Channel = CZIFile(Path(self.dataDir / "testCziYX0Tiny.czi"))
        self.assertEqual(czi2Channels.numberOfChannels, 2)
        self.assertEqual(cziOneChannel.numberOfChannels, 1)
        self.assertEqual(czi0Channel.numberOfChannels, 0)

    def testTotalWidth(self):
        czi2x3 = CZIFile(Path(self.dataDir / "testTinyCzi.czi"))
        self.assertEqual(czi2x3.totalWidth, 2)

    def testTotalHeight(self):
        czi2x3 = CZIFile(Path(self.dataDir / "testTinyCzi.czi"))
        self.assertEqual(czi2x3.totalHeight, 3)

    def testIsZStackNo(self):
        czi = CZIFile(Path(self.dataDir / "testCziFileTwoScenesTiny.czi"))
        self.assertFalse(czi.isZstack)

    def testIsZStackYes(self):
        czi = CZIFile(Path(self.dataDir / "testCziZStack4.czi"))
        self.assertTrue(czi.isZstack)

    def testIsTimeSerieNo(self):
        czi = CZIFile(Path(self.dataDir / "testCziFileTwoScenesTiny.czi"))
        self.assertFalse(czi.isTimeSerie)

    def testIsTimeSerieNoDim1(self):
        # todo find file with timeserie dim 1
        pass

    def testIsSceneNo(self):
        czi = CZIFile(Path(self.dataDir / "testCziYX0Tiny.czi"))
        self.assertFalse(czi.isScenes)

    def testIsSceneNoDim1(self):
        czi = CZIFile(Path(self.dataDir / "testCziBSCZY0Tiny.czi"))
        self.assertFalse(czi.isScenes)

    def testIsScenesYes(self):
        czi = CZIFile(Path(self.dataDir / "testCziFileTwoScenesTiny.czi"))
        self.assertTrue(czi.isScenes)

    def testShape(self):
        czi1936x1460 = CZIFile(Path(self.dataDir / "testCziFile.czi"))
        czi2x3 = CZIFile(Path(self.dataDir / "testCziZStack4Tiny.czi"))
        czi2x2 = CZIFile(Path(self.dataDir / "testCziYX0Tiny.czi"))
        czi2x3_2 = CZIFile(Path(self.dataDir / "testTinyCzi.czi"))
        self.assertTupleEqual(czi2x3_2.shape, (1, 2, 3, 2, 1))
        self.assertTupleEqual(czi2x2.shape, (2, 2, 3))
        self.assertTupleEqual(czi1936x1460.shape, (1, 2, 1460, 1936, 1))
        self.assertTupleEqual(czi2x3.shape, (1, 2, 4, 3, 2, 1))



    def testTileMapKeysZStack(self):
        czi = CZIFile(Path(self.dataDir / "testCziZStack4.czi"))
        keys = list(czi.tileMap.keys())
        supposedKeys = [(range(0, 61), range(0, 61), 0, None, None, 0), (range(0, 61), range(0, 61), 3, None, None, 0),
                        (range(0, 61), range(0, 61), 2, None, None, 1), (range(0, 61), range(0, 61), 2, None, None, 0),
                        (range(0, 61), range(0, 61), 0, None, None, 1), (range(0, 61), range(0, 61), 1, None, None, 1),
                        (range(0, 61), range(0, 61), 1, None, None, 0), (range(0, 61), range(0, 61), 3, None, None, 1)]
        self.assertListEqual(keys, supposedKeys)

    def testTileMapYX0None(self):
        czi = CZIFile(Path(self.dataDir / "testCziYX0Tiny.czi"))
        self.assertIsNone(czi.tileMap)

    def testAxesYX0(self):
        czi = CZIFile(Path(self.dataDir / "testCziYX0Tiny.czi"))
        self.assertEqual(czi.axes, "YX0")

    def testAxesBCZYX0(self):
        czi = CZIFile(Path(self.dataDir / "testCziZStack4.czi"))
        self.assertEqual(czi.axes, "BCZYX0")

    def testAxesBCYX0(self):
        czi = CZIFile(Path(self.dataDir / "testCziFile.czi"))
        self.assertEqual(czi.axes, "BCYX0")

    def testAxesBSCYX0(self):
        czi = CZIFile(Path(self.dataDir / "testOneChannel2Scenes.czi"))
        self.assertEqual(czi.axes, "BSCYX0")

    def testOriginalDType(self):
        czi = CZIFile(Path(self.dataDir / "testCziFile.czi"))
        self.assertEqual(czi.originalDType, np.uint16)

    def testAllDataYX0(self):
        czi = CZIFile(Path(self.dataDir / "testCziYX0Tiny.czi"))
        allData = czi.allData()
        data = np.dstack((np.array([[7, 7], [6, 6]]), np.array([[46, 48], [51, 47]]), np.array([[32, 29], [33, 28]])))
        # FIXME: should try to get version of package.
        self.assertTrue(np.array_equal(allData, data),
                        "It is possible cziFile is an old version.  pip install czifile --upgrade")

    def testImageDataYX0Axes(self):
        try:
            czi = CZIFile(Path(self.dataDir / "testCziYX0Tiny.czi"))
            self.assertIsNotNone(czi.imageData())
        except:
            self.fail("Exception raised.")

    def testImageDataMultipleImagesException(self):
        czi = CZIFile(Path(self.dataDir / "testCziFileTwoScenesTiny.czi"))
        with self.assertRaises(ValueError):
            czi.imageData()

    def testImageDataYX0Values(self):
        czi = CZIFile(Path(self.dataDir / "testCziYX0Tiny.czi"))
        values = np.dstack((np.array([[7, 7], [6, 6]]), np.array([[46, 48], [51, 47]]), np.array([[32, 29], [33, 28]])))
        # FIXME: should try to get version of package.
        self.assertTrue(np.array_equal(czi.imageData().asArray(), values.transpose((1, 0, 2))),
                        "It is possible cziFile is an old version.  pip install czifile --upgrade")

    def testImageDataBSCYX0Values(self):
        czi = CZIFile(Path(self.dataDir / "testCziBSCZY0Tiny.czi"))
        values = np.dstack((np.array([[596, 652], [622, 618]]), np.array([[1059, 1061], [1133, 1087]]),
                            np.array([[510, 511], [505, 497]])))
        self.assertTrue(np.array_equal(czi.imageData().asArray(), values.transpose((1, 0, 2))))

    def testScenesDataOneSceneNone(self):
        czi = CZIFile(Path(self.dataDir / "testCziBSCZY0Tiny.czi"))
        self.assertIsNone(czi.scenesData())

    def testScenesDataValues(self):
        czi = CZIFile(Path(self.dataDir / "testCziFileTwoScenesTiny.czi"))
        values1 = np.dstack((np.array([[103, 101], [99, 86]]), np.array([[171, 190], [216, 166]])))
        values2 = np.dstack((np.array([[99, 89], [78, 92]]), np.array([[180, 187], [186, 205]])))
        images = czi.scenesData().images
        self.assertTrue(np.array_equal(images[0].asArray(), values1.transpose((1, 0, 2))))
        self.assertTrue(np.array_equal(images[1].asArray(), values2.transpose((1, 0, 2))))

    def testScenesDataOneChannel(self):
        czi = CZIFile(Path(self.dataDir / "testOneChannel2Scenes.czi"))
        images = czi.scenesData().images
        for image in images:
            self.assertTupleEqual(image.shape, (2, 2, 1))

    def testZStackDataNone(self):
        czi = CZIFile(Path(self.dataDir / "testOneChannel2Scenes.czi"))
        self.assertIsNone(czi.zStackData())

    def testZStackDataValues(self):
        czi = CZIFile(Path(self.dataDir / "testCziZStack4Tiny.czi"))
        images = czi.zStackData().images
        values1 = np.dstack(
            (np.array([[290, 276], [270, 334], [312, 296]]), np.array([[700, 649], [660, 704], [681, 679]])))
        values2 = np.dstack(
            (np.array([[305, 330], [297, 306], [292, 283]]), np.array([[690, 672], [686, 670], [644, 667]])))
        values3 = np.dstack(
            (np.array([[278, 268], [278, 296], [282, 316]]), np.array([[691, 701], [654, 719], [678, 711]])))
        values4 = np.dstack(
            (np.array([[312, 276], [288, 296], [307, 315]]), np.array([[664, 668], [662, 647], [654, 699]])))
        self.assertTrue(np.array_equal(images[0].asArray(), values1.transpose((1, 0, 2))))
        self.assertTrue(np.array_equal(images[1].asArray(), values2.transpose((1, 0, 2))))
        self.assertTrue(np.array_equal(images[2].asArray(), values3.transpose((1, 0, 2))))
        self.assertTrue(np.array_equal(images[3].asArray(), values4.transpose((1, 0, 2))))

    def testZStackDataOneChannel(self):
        czi = CZIFile(Path(self.dataDir / "testCziZStack4TinyOneChannel.czi"))
        images = czi.zStackData().images
        for image in images:
            self.assertTupleEqual(image.shape, (2, 3, 1))


if __name__ == '__main__':
    unittest.main()
