import env
from dcclab import cziUtil
import unittest
import numpy as np
from unittest.mock import Mock, patch


class TestCziUtil(env.DCCLabTestCase):

    def TestReadCziFile(self):
        import czifile
        czi = cziUtil.readCziImage(self.dataFile("testCziFileTwoChannels.czi"))
        self.assertIsInstance(czi, czifile.CziFile)
        cziUtil.closeCziFileObject(czi)

    def testReadCziFileInvalid(self):
        with self.assertRaises(FileNotFoundError):
            cziUtil.readCziImage(self.dataFile("test_czi_.czi"))

    def testReadFileNotCzi(self):
        with self.assertRaises(ValueError):
            cziUtil.readCziImage(self.dataFile("testNotCziFile.jpg"))

    def testClose(self):
        czi = cziUtil.readCziImage(self.dataFile("testCziFileTwoChannels.czi"))
        cziUtil.closeCziFileObject(czi)
        with self.assertRaises(RuntimeError):
            cziUtil.getImagesFromCziFileObject(czi)

    def testExtractMetadatNoSave(self):
        czi = cziUtil.readCziImage(self.dataFile("testCziFileTwoChannels.czi"))
        metadata = cziUtil.extractMetadataFromCziFileObject(czi)
        self.assertIsInstance(metadata, str)
        cziUtil.closeCziFileObject(czi)

    def testExtractMetadataSave(self):
        czi = cziUtil.readCziImage(self.dataFile("testCziFileTwoChannels.czi"))
        cziUtil.extractMetadataFromCziFileObject(czi, "test_meta")
        cziUtil.closeCziFileObject(czi)
        ok = True
        try:
            file = open("test_meta.xml", "r")
            file.close()
        except FileNotFoundError:
            ok = False

        self.assertTrue(ok)


    def testExtractImages(self):
        czi = cziUtil.readCziImage(self.dataFile("testCziFileTwoChannels.czi"))
        images = cziUtil.getImagesFromCziFileObject(czi)
        cziUtil.closeCziFileObject(czi)
        self.assertIsInstance(images, np.ndarray)

    def testExtractNumberImages(self):
        czi = cziUtil.readCziImage(self.dataFile("testCziFileTwoChannels.czi"))
        images = cziUtil.getImagesFromCziFileObject(czi)
        nb_images = images.shape[0]
        cziUtil.closeCziFileObject(czi)
        self.assertEqual(nb_images, 2)

    @patch("matplotlib.pyplot.show", new=Mock)
    def testShowImages(self):
        czi = cziUtil.readCziImage(self.dataFile("testCziFileTwoChannels.czi"))
        images = cziUtil.showImagesFromCziFileObject(czi)
        cziUtil.closeCziFileObject(czi)
        self.assertIsInstance(images, np.ndarray)

    def testSaveImagesToTIFF(self):
        czi = cziUtil.readCziImage(self.dataFile("testCziFileTwoChannels.czi"))
        images = cziUtil.getImagesFromCziFileObject(czi)
        isSaved = cziUtil.saveImagesToTIFF(images, "testSaveTIFF")
        self.assertTrue(isSaved)
        cziUtil.closeCziFileObject(czi)

    def testSaveImagesToTIFFFilesExist(self):
        import os
        czi = cziUtil.readCziImage(self.dataFile("testCziFileTwoChannels.czi"))
        images = cziUtil.getImagesFromCziFileObject(czi)
        cziUtil.closeCziFileObject(czi)

        cziUtil.saveImagesToTIFF(images, self.dataFile("testSaveTIFF"))
        filesExist = True
        try:
            os.remove(self.dataFile("testSaveTIFF_1.tif"))
            os.remove(self.dataFile("testSaveTIFF_2.tif"))
        except FileNotFoundError:
            filesExist = False
        self.assertTrue(filesExist)

    def testSaveImagesToTIFFEmptyArray(self):
        images = []
        isSaved = cziUtil.saveImagesToTIFF(images, "test0Images")
        self.assertFalse(isSaved)

    def testMetadataFormatted(self):
        meta = "<Test>Hello</Test>"
        formattedMeta = cziUtil.getFormatedMetadata(meta)
        self.assertEqual(formattedMeta, "Test : Hello\n")

    def testMetadataFormattedBigger(self):
        meta = "<Test>\n<Test2>\nHello\n</Test2>\n</Test>"
        formattedMeta = cziUtil.getFormatedMetadata(meta)
        self.assertEqual(formattedMeta, "Test : \n\nTest2 : \nHello\n\n")

    def testMetadataFormattedInvalid(self):
        meta = "Hello. <This>String</This><is><not>good</not></is>"
        with self.assertRaises(ValueError):
            cziUtil.getFormatedMetadata(meta)


if __name__ == '__main__':
    unittest.main()
