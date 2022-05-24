1from cryptotoolbox.neural_net import activations
import torch
import torch.nn.functional as F

def convertActivationType(activation_type):
    if activation_type is activations.ActivationsType.SIGMOID:
        return torch.sigmoid
    if activation_type is activations.ActivationsType.LEAK_0dot1SUB_0MAX6:
        return activations.GeneralRelu(leak=0.1, sub=None, maxv = 6.)
    if activation_type is activations.ActivationsType.LEAK_0dot1SUB_0dot4MAX6:
        return activations.GeneralRelu(leak=0.1, sub=0.4, maxv = 6.)
    if activation_type is activations.ActivationsType.LEAK_0SUB_0MAX0:
        return activations.GeneralRelu(leak=None, sub=None, maxv = None)
    if activation_type is activations.ActivationsType.LEAK_0SUB_0MAX6:
        return activations.GeneralRelu(leak=None, sub=None, maxv = 6.)
    if activation_type is activations.ActivationsType.LEAK_0dot1SUB_0MAX50:
        return activations.GeneralRelu(leak=None, sub=None, maxv = 50.)
    if activation_type is activations.ActivationsType.SOFTPLUS:
        return F.softplus

