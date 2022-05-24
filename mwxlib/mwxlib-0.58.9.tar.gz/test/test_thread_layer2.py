#! python
# -*- coding: utf-8 -*-
import threading
import time
import cv2
import wx
from mwx.utilus import funcall
from mwx.controls import LParam, Button
from mwx.graphman import Layer, Thread, Frame


class Plugin(Layer):
    def Init(self):
        self.thread = Thread(self)
        
        self.ksize = LParam("ksize", (1,99,2), 13, tip="kernel window size")
        
        self.btn = wx.Button(self, label="Run")
        ## self.btn.Bind(wx.EVT_BUTTON, funcall(self.run))
        ## self.btn.Bind(wx.EVT_BUTTON, self.thread(self.run))
        self.btn.Bind(wx.EVT_BUTTON, self.start)
        
        self.layout((self.ksize, self.btn),
                    expand=0, type='vspin', lw=36, tw=30)
    
    def start(self, evt):
        self.thread.Start(self.run)
    
    def run(self):
        k = self.ksize.value
        src = self.graph.buffer
        dst = cv2.GaussianBlur(src, (k,k), 0.)
        self.output.load(dst, name='*gauss*')


if __name__ == "__main__":
    app = wx.App()
    frm = Frame(None)
    frm.load_plug(Plugin, show=1, dock=4)
    frm.load_buffer("../demo/sample.bmp")
    frm.Show()
    app.MainLoop()
