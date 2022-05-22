import __init__
import unittest

from TDhelper.generic.requier import R
class TestReflect(unittest.TestCase):
    def test_reflect(self):
        bb=R("a.b:ab").Call('gg')
        print(bb)

if __name__ == "__main__":
    unittest.main()