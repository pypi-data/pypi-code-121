import unittest
from pypers.utils import ftpw
import shutil
import os


class MockFTPConnection:

    def __init__(self, path):
        self.path = path

    def cwd(self, path):
        if path == "..":
            return
        if os.path.abspath(self.path) not in os.path.abspath(path):
            raise Exception("Path not accepted")
        self.tmp_path = path

    def pwd(self):
        return self.path

    def retrlines(self, cmd, callback=None):
        results = ['d .', 'd ..']
        limit_files = False
        for root, dirs, files in os.walk(self.tmp_path):
            root = os.path.relpath(root, self.tmp_path)
            results.append("d %s" % root)
            if len(files) == 0 and not limit_files:
                limit_files = True
            if not limit_files:
                for file in files:
                    results.append("f %s" % file)
        for res in results:
            callback(res)


class Test(unittest.TestCase):

    def setUp(self):
        self.path = 'toto/'
        try:
            shutil.rmtree('toto/')
        except Exception as e:
            pass
        os.makedirs(self.path)
        for i in range(10):
            os.mkdir(os.path.join(self.path, '%s_f' % i))
            for j in range(10):
                with open(os.path.join(self.path,
                                       '%s_f' % i,
                                       '%s_f.xml' % j), 'w') as f:
                    f.write("test_file")
        self.connection = MockFTPConnection('toto')

    def tearDown(self):
        try:
            shutil.rmtree('toto/')
        except Exception as e:
            pass

    def test_walk(self):
        if os.environ.get('SHORT_TEST', None):
            return
        walker = ftpw.FTPWalk(self.connection)
        results = list(walker.walk("toto/"))
        self.assertEqual(len(results), 11)
        expected = ['8_f.xml', '9_f.xml', '3_f.xml', '1_f.xml', '5_f.xml',
                    '7_f.xml', '0_f.xml', '2_f.xml', '6_f.xml', '4_f.xml']
        for path, files in results:
            if len(files) == 0:
                self.assertEqual(path, 'toto/')
            else:
                self.assertEqual(sorted(files), sorted(expected))

    def test_exceptio_lisdir(self):
        if os.environ.get('SHORT_TEST', None):
            return
        walker = ftpw.FTPWalk(self.connection)
        folders, files = walker.listdir('indexiting/')
        self.assertEqual(folders, [])
        self.assertEqual(files, [])


if __name__ == "__main__":
    unittest.main()
