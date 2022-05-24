import torch
from torch import nn
from torch.autograd import Function

"""
Earth Mover's Distance for point clouds.

Code from:
https://github.com/Colin97/MSN-Point-Cloud-Completion

Author: Minghua Liu
"""

import emdcuda  # type: ignore


class EMD_CUDA_Function(Function):
    @staticmethod
    def forward(ctx, xyz1, xyz2, eps, iters):  # type: ignore

        batchsize, n, _ = xyz1.size()
        _, m, _ = xyz2.size()

        assert n == m
        assert xyz1.size()[0] == xyz2.size()[0]
        assert n % 1024 == 0
        assert batchsize <= 512

        xyz1 = xyz1.contiguous().float().cuda()
        xyz2 = xyz2.contiguous().float().cuda()
        dist = torch.zeros(batchsize, n, device="cuda").contiguous()
        assignment = torch.zeros(batchsize, n, device="cuda", dtype=torch.int32).contiguous() - 1
        assignment_inv = (
            torch.zeros(batchsize, m, device="cuda", dtype=torch.int32).contiguous() - 1
        )
        price = torch.zeros(batchsize, m, device="cuda").contiguous()
        bid = torch.zeros(batchsize, n, device="cuda", dtype=torch.int32).contiguous()
        bid_increments = torch.zeros(batchsize, n, device="cuda").contiguous()
        max_increments = torch.zeros(batchsize, m, device="cuda").contiguous()
        unass_idx = torch.zeros(batchsize * n, device="cuda", dtype=torch.int32).contiguous()
        max_idx = torch.zeros(batchsize * m, device="cuda", dtype=torch.int32).contiguous()
        unass_cnt = torch.zeros(512, dtype=torch.int32, device="cuda").contiguous()
        unass_cnt_sum = torch.zeros(512, dtype=torch.int32, device="cuda").contiguous()
        cnt_tmp = torch.zeros(512, dtype=torch.int32, device="cuda").contiguous()

        emdcuda.forward(
            xyz1,
            xyz2,
            dist,
            assignment,
            price,
            assignment_inv,
            bid,
            bid_increments,
            max_increments,
            unass_idx,
            unass_cnt,
            unass_cnt_sum,
            cnt_tmp,
            max_idx,
            eps,
            iters,
        )

        ctx.save_for_backward(xyz1, xyz2, assignment)
        return dist, assignment

    @staticmethod
    def backward(ctx, graddist, gradidx):  # type: ignore
        xyz1, xyz2, assignment = ctx.saved_tensors
        graddist = graddist.contiguous()

        gradxyz1 = torch.zeros(xyz1.size(), device="cuda").contiguous()
        gradxyz2 = torch.zeros(xyz2.size(), device="cuda").contiguous()

        emdcuda.backward(xyz1, xyz2, gradxyz1, graddist, assignment)
        return gradxyz1, gradxyz2, None, None


class EMD_CUDA(nn.Module):
    def __init__(self) -> None:
        super(EMD_CUDA, self).__init__()

    def forward(self, input1, input2, eps, iters):  # type: ignore
        return EMD_CUDA_Function.apply(input1, input2, eps, iters)
