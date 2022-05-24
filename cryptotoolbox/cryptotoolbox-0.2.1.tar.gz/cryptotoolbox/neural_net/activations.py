import torch.nn as nn
import torch.nn.functional as F
import enum

class GeneralRelu(nn.Module):
    def __init__(self, leak=None, sub=None, maxv=None):
        super().__init__()
        self.leak,self.sub,self.maxv = leak,sub,maxv

    def forward(self, x):
        x = F.leaky_relu(x,self.leak) if self.leak is not None else F.relu(x)
        if self.sub is not None: x.sub_(self.sub)
        if self.maxv is not None: x.clamp_max_(self.maxv)
        return x



class ActivationsType(enum.IntEnum):
    SIGMOID=1
    LEAK_0SUB_0MAX0=2
    LEAK_0dot1SUB_0MAX6=3
    LEAK_0dot1SUB_0dot4MAX6=4
    LEAK_0SUB_0MAX6=5
    LEAK_0SUB_0MAX1=6
    LEAK_0SUB_0MAX20=7
    LEAK_0dot1SUB_0MAX50=8
    SOFTPLUS=9


