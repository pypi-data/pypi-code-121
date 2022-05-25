import sys,unittest
from TestProxy import MethodTest
sys.path.append('.')
def test_import():
    try:
        from IutyLib.commonutil.convert import str2float
    except Exception as err:
        raise AssertionError("import module error")
from IutyLib.commonutil.convert import str2float

class TestDemo(unittest.TestCase):
    def test_str2float(self):
        v = "19.365"
        vf = str2float(v)
        self.assertEqual(vf,19.36)

    def test_str2float1(self):
        v = "19.365"
        vf = str2float(v,3)
        self.assertEqual(vf,19.36)

suite = unittest.TestSuite()
suite.addTest(TestDemo("test_str2float"))
suite.addTest(TestDemo("test_str2float1"))

with open('ut_log.txt', 'a') as fp:
    runner = unittest.TextTestRunner(stream=fp, verbosity=1)
    runner.run(suite)