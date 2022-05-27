import env
import unittest
import os
from pathlib import Path

class TestBaseClass(env.DCCLabTestCase):
    def testInit(self):
        self.assertIsNotNone(self.tmpDir)
        self.assertIsNotNone(self.dataDir)

    def testModuleDir(self):
        self.assertIsNotNone(self.moduleDir)
        self.assertTrue(os.path.exists(Path(self.moduleDir / 'dcclab')))

    def testTestDir(self):
        self.assertIsNotNone(self.testsDir)
        self.assertTrue(os.path.exists(Path(self.testsDir / 'env.py')))

    def testTmpDirExists(self):
        self.assertTrue(os.path.exists(self.tmpDir), "Temporary directory not created")

    def testTmpDirCanBeEmptied(self):
        someFile = Path(self.tmpDir / "abcd.txt")
        someFile.write_bytes(b'1')
        self.assertTrue(someFile.exists())
        self.deleteTempDirectoriesAndFiles()
        self.assertFalse(self.tmpDir.exists())
        #but we need to recreate because that is what the class expects
        self.createTempDirectories()
 
    def testTmpDirIsEmpty(self):
        files = []
        for filename in Path(self.tmpDir).iterdir():
            files.append(filename)
        self.assertTrue(len(files) == 0, "Temporary directory empty")

    def testDataDirExists(self):
        self.assertTrue(os.path.exists(self.dataDir), "Data directory not present")

    def testDataDirNotEmpty(self):
        files = []
        for filename in self.dataDir.iterdir():
            files.append(filename)
        self.assertTrue(len(files) != 0)

if __name__ == '__main__':
    unittest.main()
