import torch
from torch import nn
from torch.autograd import Function

"""
Chamfer Distance for 3D points CUDA extension.

Code from:
https://github.com/ThibaultGROUEIX/ChamferDistancePytorch

Author: Thibault Groueix
"""

import chamfercuda  # type: ignore


class Chamfer_CUDA_Function(Function):
    @staticmethod
    def forward(ctx, xyz1, xyz2):  # type: ignore
        batchsize, n, dim = xyz1.size()
        assert (
            dim == 3
        ), "Wrong last dimension for the chamfer distance 's input! Check with .size()"
        _, m, dim = xyz2.size()
        assert (
            dim == 3
        ), "Wrong last dimension for the chamfer distance 's input! Check with .size()"
        device = xyz1.device

        device = xyz1.device

        dist1 = torch.zeros(batchsize, n)
        dist2 = torch.zeros(batchsize, m)

        idx1 = torch.zeros(batchsize, n).type(torch.IntTensor)  # type: ignore
        idx2 = torch.zeros(batchsize, m).type(torch.IntTensor)  # type: ignore

        dist1 = dist1.to(device)
        dist2 = dist2.to(device)
        idx1 = idx1.to(device)
        idx2 = idx2.to(device)
        torch.cuda.set_device(device)

        chamfercuda.forward(xyz1, xyz2, dist1, dist2, idx1, idx2)
        ctx.save_for_backward(xyz1, xyz2, idx1, idx2)
        return dist1, dist2, idx1, idx2

    @staticmethod
    def backward(ctx, graddist1, graddist2, gradidx1, gradidx2):  # type: ignore
        xyz1, xyz2, idx1, idx2 = ctx.saved_tensors
        graddist1 = graddist1.contiguous()
        graddist2 = graddist2.contiguous()
        device = graddist1.device

        gradxyz1 = torch.zeros(xyz1.size())
        gradxyz2 = torch.zeros(xyz2.size())

        gradxyz1 = gradxyz1.to(device)
        gradxyz2 = gradxyz2.to(device)
        chamfercuda.backward(xyz1, xyz2, gradxyz1, gradxyz2, graddist1, graddist2, idx1, idx2)
        return gradxyz1, gradxyz2


class Chamfer_CUDA(nn.Module):
    def __init__(self) -> None:
        super(Chamfer_CUDA, self).__init__()

    def forward(self, input1, input2):  # type: ignore
        input1 = input1.contiguous()
        input2 = input2.contiguous()
        return Chamfer_CUDA_Function.apply(input1, input2)
