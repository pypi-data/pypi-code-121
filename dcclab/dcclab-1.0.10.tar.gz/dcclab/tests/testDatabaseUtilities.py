import env
from dcclab import findFiles
import os
import unittest
import re


class TestDatabaseUtilities(env.DCCLabTestCase):
    def testFindFilesSomethingFound(self):
        directory = os.path.join(str(self.moduleDir), 'dcclab', 'database')
        self.assertTrue(findFiles(directory, 'py'))

    def testFindFilesNothingFound(self):
        directory = os.path.join(str(self.moduleDir), 'dcclab', 'database')
        self.assertFalse(findFiles(directory, 'czi'))

    def testFindFilesFolderDoesntExist(self):
        directory = os.path.join(str(self.moduleDir), 'thisFolderDoesntExist')
        self.assertFalse(findFiles(directory, 'py'))

    def testRegularExpressionsExtension(self):
        string = 'trucpatente.py'
        extension = 'py'
        self.assertTrue(re.search(r'\.{}$'.format(extension), string, re.IGNORECASE))

    def testRegularExpressionsMoreComplexExtension(self):
        string = 'someFile.tar.gz'
        extension = 'tar.gz'
        self.assertTrue(re.search(r'\.{}$'.format(extension), string, re.IGNORECASE))


if __name__ == '__main__':
    unittest.main()
