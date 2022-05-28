import env
import os
import unittest
import numpy as np
import re
import time

from dcclab import PathPattern
from pathlib import Path, PureWindowsPath, PurePosixPath

class TestPatterns(env.DCCLabTestCase):
    def testInit(self):
        self.assertIsNotNone(PathPattern('abc'))

    def testInitInvalid(self):
        with self.assertRaises(Exception):
            PathPattern('(abc')

    def testInitNoCaptureGroups(self):
        pat = PathPattern('abc')
        self.assertFalse(pat.hasCaptureGroups)

    def testInitWithCaptureGroups(self):
        pat = PathPattern(r'abc(\d)')
        self.assertTrue(pat.hasCaptureGroups)

    def testFindCaptureGroups(self):
        match = re.search(r"(\(.*\))", "abc(daniel)def")
        self.assertIsNotNone(match)
        self.assertTrue(len(match.groups()) == 1)
        strings = re.findall(r"(\(.+?\))", "abc(daniel)(def)")
        self.assertTrue(len(strings) == 2)

    def testInitWith0CaptureGroup(self):
        pat = PathPattern(r'abckjhasd')
        self.assertTrue(pat.numberOfCaptureGroups == 0)

    def testInitWith1CaptureGroup(self):
        pat = PathPattern(r'abc(\d)')
        self.assertTrue(pat.numberOfCaptureGroups == 1)

    def testInitWith2CaptureGroups(self):
        pat = PathPattern(r'abc(\d)...(lkha)')
        self.assertTrue(pat.numberOfCaptureGroups == 2)

    def testInitWith3CaptureGroups(self):
        pat = PathPattern(r'abc(\d)...(lkha)bla(asd)')
        self.assertTrue(pat.numberOfCaptureGroups == 3)

    def testInitWith1PythonFormatString(self):
        pat = PathPattern(r'abl{0}')
        self.assertTrue(pat.isPythonFormatString)
        self.assertTrue(pat.numberOfFormatGroups == 1)

    def testInitWith2PythonFormatString(self):
        pat = PathPattern(r'abl{0}blabal{1:03f}')
        self.assertTrue(pat.isPythonFormatString)
        self.assertTrue(pat.numberOfFormatGroups == 2)

    def testInitWithoutPythonFormatString(self):
        pat = PathPattern(r'abl')
        self.assertFalse(pat.isPythonFormatString)
        self.assertTrue(pat.numberOfFormatGroups == 0)

    def testIsWritePattern(self):
        pat = PathPattern(r'abl{0}blabal{1:03f}')
        self.assertTrue(pat.isWritePattern)
        self.assertFalse(pat.isReadPattern)

    def testIsReadPattern(self):
        pat = PathPattern(r'abl(\d)')
        self.assertTrue(pat.isReadPattern)
        self.assertFalse(pat.isWritePattern)

    def testOsPathModule(self):
        self.assertTrue('test.tiff' == os.path.basename(r"test.tiff"))
        self.assertTrue('test.tiff' == os.path.basename(r"/Users/test.tiff"))

    # def testPathLib(self):
    #     self.assertEqual(r"c:\daniel\test.tiff", str(PureWindowsPath(r"c:\daniel\test.tiff")))
    #     self.assertEqual(r"c:/daniel/test.tiff", Path(PureWindowsPath(r"c:\daniel\test.tiff")))

    def testUnixPathPatternPattern(self):
        pat = PathPattern(r"/Users/dccote/test.tiff")
        self.assertEqual(pat.pattern, "/Users/dccote/test.tiff")
        self.assertEqual(pat.pattern, r"/Users/dccote/test.tiff")
        self.assertEqual(str(pat.normalizedPathPattern), r"/Users/dccote/test.tiff")

    def testUnixPattern(self):
        pat = PathPattern(r"/Users/dccote/test.tiff")
        self.assertEqual(pat.pattern, "/Users/dccote/test.tiff")

    def testUnixExtension(self):
        pat = PathPattern(r'/Users/dccote/test.tiff')
        self.assertEqual(pat.extension, "tiff")

    def testUnixDirectory(self):
        pat = PathPattern(r'/Users/dccote/test.tiff')
        self.assertEqual(pat.directory, "/Users/dccote")

    def testEmptyDirectory(self):
        pat = PathPattern(r'test.tiff')
        self.assertEqual(pat.directory, ".")

    def testUnixBasename(self):
        pat = PathPattern("/Users/dccote/test.tiff")
        self.assertEqual(pat.basePattern, "test.tiff")

    def testUnixBasename2(self):
        pat = PathPattern("/Users/dccote/test.tif")
        self.assertEqual(pat.basePattern, "test.tif")

    def testUnixBasename3(self):
        pat = PathPattern("/Users/dccote/test/")
        self.assertEqual(pat.basePattern, "")

    def testBasenameWithFormats(self):
        pat = PathPattern(r'/Users/dccote/test-{0}.tiff')
        self.assertEqual(pat.basePattern, r"test-{0}.tiff")

    def testBasenameWithCapture(self):
        pat = PathPattern(r'/Users/dccote/test-(\d+).tiff')
        self.assertEqual(pat.basePattern, r"test-(\d+).tiff")

    def testFindFiles(self):
        # Use this test directory
        pat = PathPattern(r'test.+\.py')
        files = pat.matchingFiles()
        self.assertTrue(len(files) != 0)

    def testFailedFindFilesWritePattern(self):
        # Use this test directory
        pat = PathPattern(r'test.{0}.py')
        with self.assertRaises(ValueError):
            files = pat.matchingFiles()

    def testFindFilesCheckExist(self):
        # Use this test directory
        pat = PathPattern(r'test.+\.py')
        files = pat.matchingFiles()
        for filePath in files:
            self.assertTrue(os.path.exists(filePath))

    def testFileExpansion(self):
        pat = PathPattern(r'test-{0}.py')
        for i in range(4):
            self.assertEqual(pat.filePathWithIndex(i), "test-{0}.py".format(i))

    def testFileExpansionWithFancyFormat(self):
        pat = PathPattern(r'test-{0:03d}.py')
        self.assertEqual(pat.filePathWithIndex(1), "test-001.py")
        for i in range(4):
            self.assertEqual(pat.filePathWithIndex(i), "test-{0:03d}.py".format(i))

    def testFileExpansion2Indices(self):
        pat = PathPattern(r'test-{0}-{1}.py')
        for i in range(4):
            for j in range(4):
                self.assertEqual(pat.filePathWithIndex(i,j), "test-{0}-{1}.py".format(i,j))

    def testFileExpansion3Indices(self):
        pat = PathPattern(r'test-{0}-{1}-{2}.py')
        for i in range(4):
            for j in range(4):
                for k in range(4):
                    self.assertEqual(pat.filePathWithIndex(i,j,k), "test-{0}-{1}-{2}.py".format(i,j,k))

    def testFileExpansionMissingIndices(self):
        pat = PathPattern(r'test-{0}-{1}-{2}.py')
        for i in range(4):
            for j in range(4):
                for k in range(4):
                    with self.assertRaises(ValueError):
                        pat.filePathWithIndex(i,j)

    def testFileExpansionMissingPatternIndices(self):
        pat = PathPattern(r'test-{0}-{1}.py')
        for i in range(4):
            for j in range(4):
                for k in range(4):
                    with self.assertRaises(ValueError):
                        pat.filePathWithIndex(i,j,k)

    def testFileExpansionWithReadPattern(self):
        pat = PathPattern(r'test-(\d).py')
        for i in range(4):
            for j in range(4):
                for k in range(4):
                    with self.assertRaises(ValueError):
                        pat.filePathWithIndex(i,j,k)

    def testFileExpansionWithTooManyIndices(self):
        pat = PathPattern(r'test-{0}-{1}-{2}-{3}.py')
        for i in range(4):
            for j in range(4):
                for k in range(4):
                    with self.assertRaises(ValueError):
                        pat.filePathWithIndex(i,j,k)

    def testWindowsPathPatternPattern(self):
        with self.assertRaises(ValueError):
            pat = PathPattern(r'C:\Users\dccote\test.tiff')

    @unittest.skip("Windows file name not supported: unable to separate separator from regex special patterns")
    def testWindowsPattern(self):
        pat = PathPattern(r'C:\Users\dccote\test.tiff')
        self.assertEqual(pat.pattern, r'C:\Users\dccote\test.tiff')

    @unittest.skip("Windows file name not supported: unable to separate separator from regex special patterns")
    def testWindowsExtension(self):
        pat = PathPattern(r'C:\Users\dccote\test.tiff')
        self.assertEqual(pat.extension, "tiff")

    @unittest.skip("Windows file name not supported: unable to separate separator from regex special patterns")
    def testWindowsDirectory(self):
        pat = PathPattern(r'C:\Users\dccote\test.tiff')
        self.assertEqual(pat.directory, r'C:\Users\dccote')

    @unittest.skip("Windows file name not supported: unable to separate separator from regex special patterns")
    def testWindowsBasename(self):
        pat = PathPattern(r'C:\\Users\\dccote\\test.tiff')
        self.assertEqual(pat.basePattern, "test.tiff")

    @unittest.skip("Windows file name not supported: unable to separate separator from regex special patterns")
    def testWindowsBasename2(self):
        pat = PathPattern(r'C:\Users\dccote\test.tif')
        self.assertEqual(pat.basePattern, "test.tif")

    @unittest.skip("Windows file name not supported: unable to separate separator from regex special patterns")
    def testWindowsBasename3(self):
        pat = PathPattern(r'C:\Users\dccote\test')
        self.assertEqual(pat.basePattern, "")



if __name__ == '__main__':
    unittest.main()
