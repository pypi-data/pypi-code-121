import env
import unittest
import os

from dcclab import Dataset

from pathlib import Path

class TestMLDatasets(env.DCCLabTestCase):

    def testExtractDataSingleChannel(self):
        dataset = Dataset(os.path.join(self.dataDir, "labelledDataset"))
        self.assertIsNotNone(dataset)

    def testGetFolders(self):
        folders = list(os.walk(("/kjasdkjhasdkhjasdkhjasdkhj")))
        self.assertTrue(len(folders) == 0)

    def testExtractDataSingleChannelNoDirectory(self):
        with self.assertRaises(FileNotFoundError):
            dataset = Dataset(os.path.join(self.dataDir, "labelledDatasetasdasda"))

    def testExtractDataSingleChannelTagIsSemantic(self):
        dataset = Dataset(os.path.join(self.dataDir, "labelledDataset"))
        self.assertIsNotNone(dataset)
        self.assertTrue(dataset.isSemantic)

    def testExtractDataSingleChannelTagIsNotSemantic(self):
        dataset = Dataset(os.path.join(self.dataDir, "notSemantic"))
        self.assertIsNotNone(dataset)
        self.assertTrue(dataset.isSemantic)

    def testExtractDataSingleChannelTagIsNotSemantic(self):
        dataset = Dataset(os.path.join(self.dataDir, "notSemantic"))
        self.assertTrue(dataset.isValid)


if __name__ == '__main__':
    unittest.main()
