import unittest
from pypers.utils import execute
import subprocess
import os


class StreamMock:
    def __init__(self):
        pass

    def close(self):
        pass


class PopenMockObj:

    def __init__(self, *args, **kwargs):
        self.args = args
        self.kwargs = kwargs
        self.stdout = StreamMock()
        self.stderr = StreamMock()
        self.returncode = 0

    def communicate(self):
        return self.args, self.kwargs


class Test(unittest.TestCase):

    def setUp(self):
        self.mocker_suprocess = PopenMockObj()
        self.old_popen = subprocess.Popen
        subprocess.Popen = PopenMockObj

    def tearDown(self):
        subprocess.Popen = self.old_popen

    def test_execute(self):
        if os.environ.get('SHORT_TEST', None):
            return
        rc, err, out = execute.run_as(['ls'])
        self.assertEqual(err, {'shell': False, 'stderr': -1, 'stdout': -1})
        self.assertEqual(rc, 0)
        self.assertEqual(out, (['ls'],))
        rc, err, out = execute.run_as(['ls'], user='root')
        self.assertEqual(err, {'shell': False, 'stderr': -1, 'stdout': -1})
        self.assertEqual(rc, 0)


if __name__ == "__main__":
    unittest.main()
