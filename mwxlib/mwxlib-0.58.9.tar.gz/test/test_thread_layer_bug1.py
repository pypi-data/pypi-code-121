import wx
import cv2
from mwx.controls import LParam, Button
from mwx.graphman import Layer, Thread, Frame


class Plugin(Layer):
    """Plugin template ver.1
    """
    template = property(lambda self: self.parent.require('template'))
    
    def Init(self):
        self.thread = Thread(self)
        
        self.params = (
            LParam("ksize", (1,99,2), 13, tip="kernel window size"),
            LParam("sigma", (0,100,1), 0, tip="sigma, default 0 as norm distribution"),
        )
        self.layout(
            self.params, title="blur params",
            row=1, expand=0, show=1, type='vspin', cw=0, lw=36, tw=36,
        )
        self.layout((
            Button(self, "Start", lambda v: self.thread.Start(self.run),
                tip="Gaussian blurring", icon='exe'),
            ),
            row=1, expand=0, show=1,
        )
    
    def run(self):
        with self.thread:
            k, s = (p.value for p in self.params)
            src = self.graph.buffer
            dst = cv2.GaussianBlur(src, (k,k), s)
            self.output['*gauss*'] = dst
        
        ## Load in the thread => Window-lost ? unsafe
        ## self.parent.load_plug("template", force=1)
        self.template.Show()
        return True


if __name__ == "__main__":
    app = wx.App()
    frm = Frame(None)
    frm.load_plug(__file__, show=1)
    frm.load_buffer(u"C:/usr/home/workspace/images/sample.bmp")
    frm.Show()
    app.MainLoop()
