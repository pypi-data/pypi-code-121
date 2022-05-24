import unittest
import sys
import re
import wx
import mwx
import mwx.utilus as ut
import mwx.graphman

app = wx.App()
frame = mwx.Frame(None)

class TestUtilus(unittest.TestCase):

    def test_typename(self):
        values = (
            (wx, "wx"),
            (mwx, "mwx"),
            (frame, "Frame"),
            (mwx.Frame, "Frame"),
            (mwx.funcall, "funcall"),
            (mwx.typename, "typename"),
            (mwx.graphman.Layer, "mwx.graphman:Layer"),
        )
        for obj, result in values:
            self.assertEqual(ut.typename(obj), result)
    
    def test_where(self):
        site = r"C:\\Python3[0-9]+\\lib\\site-packages"
        home = r"C:\\usr\\home\\lib\\python\\Lib\\mwx"
        values = (
            ## (sys, sys), #<module 'sys' (built-in)>
            (sys, None),
            
            (wx, fr"{site}\\wx\\__init__.py"),
            (wx.App, fr"{site}\\wx\\core.py:([0-9]+):class App"),
            (wx.Frame, fr"{site}\\wx\\_core.cp([0-9]+)-win_amd64.pyd"),
            (wx.Frame.Update, None),
            
            (app, fr"{site}\\wx\\core.py:([0-9]+):class App"),
            (frame, fr"{home}\\framework.py:([0-9]+):class Frame"),
            (frame.Update, None),
            
            (mwx, fr"{home}\\__init__.py"),
            (mwx.typename, fr"{home}\\utilus.py:([0-9]+):def typename"),
        )
        for obj, result in values:
            ret = ut.where(obj)
            print(obj, "#", ret)
            self.assertTrue(
                re.match(result, ret) if isinstance(result, str) else
                (ret is result))


if __name__ == "__main__":
    unittest.main()
