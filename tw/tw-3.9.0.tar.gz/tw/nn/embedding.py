# Copyright 2021 The KaiJIN Authors. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# ==============================================================================
r"""Embedding
"""

import math
import torch
import torch.nn as nn

#!<-----------------------------------------------------------------------------
#!<  AngleLinear used in SphereFace for AngleLoss
#!<-----------------------------------------------------------------------------


class AngleLinear(nn.Module):

  def __init__(self, in_features, out_features, m=4, phiflag=True):
    super(AngleLinear, self).__init__()
    self.in_features = in_features
    self.out_features = out_features
    self.weight = nn.Parameter(torch.Tensor(in_features, out_features))
    self.weight.data.uniform_(-1, 1).renorm_(2, 1, 1e-5).mul_(1e5)
    self.phiflag = phiflag
    self.m = m
    self.mlambda = [
        lambda x: x**0,
        lambda x: x**1,
        lambda x: 2 * x**2 - 1,
        lambda x: 4 * x**3 - 3 * x,
        lambda x: 8 * x**4 - 8 * x**2 + 1,
        lambda x: 16 * x**5 - 20 * x**3 + 5 * x
    ]

  @staticmethod
  def myphi(x, m):
    x = x * m
    return 1 - x**2 / math.factorial(2) + x**4 / math.factorial(4) - x**6 / \
        math.factorial(6) + x**8 / math.factorial(8) - x**9 / math.factorial(9)

  def forward(self, input):
    x = input   # size=(B,F)，F为特征长度，如512
    w = self.weight  # size=(F,C)

    # 对w进行归一化，renorm使用L2范数对第1维度进行归一化，将大于1e-5的截断，乘以1e5，使得最终归一化到1.如果1e-5设置的过大，裁剪时某些很小的值最终可能小于1。注意，第0维度只对每一行进行归一化（每行平方和为1），第1维度指对每一列进行归一化。由于w的每一列为x的权重，因而此处需要对每一列进行归一化。如果要对x归一化，需要对每一行进行归一化，此时第二个参数应为0
    ww = w.renorm(2, 1, 1e-5).mul(1e5)
    # 对输入x求平方，而后对不同列求和，再开方，得到每行的模，最终大小为第0维的，即B(由于对x不归一化，但是计算余弦时需要归一化，因而可以先计算模。但是对于w，不太懂为何不直接使用这种方式，而是使用renorm函数？)
    xlen = x.pow(2).sum(1).pow(0.5)
    wlen = ww.pow(2).sum(0).pow(0.5)  # 对权重w求平方，而后对不同行求和，再开方，得到每列的模（理论上之前已经归一化，此处应该是1，但第一次运行到此处时，并不是1，不太懂），最终大小为第1维的，即C

    cos_theta = x.mm(ww)  # 矩阵相乘(B,F)*(F,C)=(B,C)，得到cos值，由于此处只是乘加，故未归一化
    cos_theta = cos_theta / xlen.view(-1, 1) / wlen.view(1, -1)  # 对每个cos值均除以B和C，得到归一化后的cos值
    cos_theta = cos_theta.clamp(-1, 1)  # 将cos值截断到[-1,1]之间，理论上不截断应该也没有问题，毕竟w和x都归一化后，cos值不可能超出该范围

    if self.phiflag:
      cos_m_theta = self.mlambda[self.m](cos_theta)  # 通过cos_theta计算cos_m_theta，mlambda为cos_m_theta展开的结果
      theta = torch.autograd.Variable(cos_theta.data.acos())  # 通过反余弦，计算角度theta，(B,C)
      k = (self.m * theta / 3.14159265).floor()  # 通过公式，计算k，(B,C)。此处为了保证theta大于k*pi/m，转换过来就是m*theta/pi，再向上取整
      n_one = k * 0.0 - 1  # 通过k的大小，得到同样大小的-1矩阵，(B,C)
      phi_theta = (n_one**k) * cos_m_theta - 2 * k  # 通过论文中公式，得到phi_theta。(B,C)
    else:
      theta = cos_theta.acos()  # 得到角度theta，(B, C)，每一行为当前特征和w的每一列的夹角
      phi_theta = AngleLinear.myphi(theta, self.m)
      phi_theta = phi_theta.clamp(-1 * self.m, 1)

    cos_theta = cos_theta * xlen.view(-1, 1)  # 由于实际上不对x进行归一化，此处cos_theta需要乘以B。(B,C)
    phi_theta = phi_theta * xlen.view(-1, 1)  # 由于实际上不对x进行归一化，此处phi_theta需要乘以B。(B,C)
    output = (cos_theta, phi_theta)
