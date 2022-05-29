from datetime import datetime
import __init__
import unittest

from TDhelper.generic.requier import R
class TestReflect(unittest.TestCase):
    def test_reflect(self):
        bb=R("a.b:ab").Call('gg')
        print(bb)

    def test_type(self):
        try:
            from django.http import HttpRequest
            cc=R('django.http:HttpRequest')
            ccc= R("rest_framework.request:Request",*(cc,)).getType()
            print(ccc)
        except Exception as e:
            print(e.args)
        #print(isinstance(1,R(int).getInstance()))

if __name__ == "__main__":
    unittest.main()