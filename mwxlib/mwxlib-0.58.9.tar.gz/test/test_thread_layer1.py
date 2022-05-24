#! python
# -*- coding: utf-8 -*-
import threading
import time
import wx
from mwx.controls import LParam, Button
from mwx.graphman import Layer, Thread, Frame


class Plugin(Layer):
    def Init(self):
        self.ksize = LParam("ksize", (1,99,2), 13, tip="kernel window size")
        
        self.btn = wx.Button(self, label="Run")
        self.btn.Bind(wx.EVT_BUTTON, self.start)
        
        self.layout((self.ksize, self.btn), type='vspin', lw=36, tw=30)
    
    def start(self, evt):
        self.thread = TestThread()
        self.thread.start()
        time.sleep(4)
        self.thread.active = 0 # flag to quit
        del self.thread


class TestThread(threading.Thread):
    def run(self):
        self.active = 1
        t = time.time()
        while self.active:
            print('\b'*20, time.time()-t, end='', flush=1)
            time.sleep(0.1)
        else:
            print("done")


if __name__ == "__main__":
    app = wx.App()
    frm = Frame(None)
    frm.load_plug(Plugin, show=1, dock=4)
    frm.show_pane("graph", False)
    frm.Show()
    app.MainLoop()
