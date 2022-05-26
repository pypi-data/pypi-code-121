# Copyright 2022 The KaiJIN Authors. All Rights Reserved.
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
"""Nvidia diffrast render

   This script is the differentiable renderer for Deep3DFaceRecon_pytorch
    Attention, antialiasing step is missing in current version.
"""
import numpy as np
import torch
from torch import nn
import torch.nn.functional as F
import nvdiffrast.torch as dr


def ndc_projection(x=0.1, n=1.0, f=50.0):
  return np.array([
      [n / x, 0, 0, 0],
      [0, n / -x, 0, 0],
      [0, 0, -(f + n) / (f - n), -(2 * f * n) / (f - n)],
      [0, 0, -1, 0],
  ]).astype(np.float32)


class MeshRenderer(nn.Module):

  def __init__(self, rasterize_fov, znear=0.1, zfar=10, rasterize_size=224):
    super(MeshRenderer, self).__init__()
    x = np.tan(np.deg2rad(rasterize_fov * 0.5)) * znear
    self.ndc_proj = torch.tensor(ndc_projection(x=x, n=znear, f=zfar))
    self.ndc_proj = self.ndc_proj.matmul(torch.diag(torch.tensor([1.0, -1, -1, 1])))
    self.rasterize_size = rasterize_size
    self.glctx = None

  def forward(self,
              vertex,
              tri,
              image_size,
              color=None,
              uv=None,
              z=None,
              albedo=None,
              normal=None,
              face_mask=None):
    """render coeff to 3d obj

    Args:
        vertex (torch.tensor): size (B, N, 3)
        tri (torch.tensor): size (B, M, 3) or (M, 3), triangles
        image_size (torch.tensor):
        color (torch.tensor, optional):
        uv (torch.tensor, optional):
        z (torch.tensor, optional):
        albedo (torch.tensor, optional):
        normal (torch.tensor, optional):
        face_mask (torch.tensor, optional):

    Returns:
        mask: torch.tensor, size (B, 1, H, W)
        depth: torch.tensor, size (B, 1, H, W)
        features (optional): torch.tensor, size (B, C, H, W) if feat is not None

    """

    device = vertex.device
    rsize = int(self.rasterize_size)
    uv4d = torch.zeros([vertex.shape[0], vertex.shape[1], 4]).to(vertex.device)
    ndc_proj = self.ndc_proj.to(device)

    # for deep3d
    if uv is None:
      # trans to homogeneous coordinates of 3d vertices, the direction of y is the same as v
      if vertex.shape[-1] == 3:
        vertex = torch.cat([vertex, torch.ones([*vertex.shape[:2], 1]).to(device)], dim=-1)
        vertex[..., 1] = -vertex[..., 1]

    else:  # for frnet
      if z is None:
        raise RuntimeError("In Render forward: uv is not None, z should not be None either!")

      z_min = torch.min(z, axis=1, keepdim=True).values
      z_max = torch.max(z, axis=1, keepdim=True).values
      z_buffer = (z - z_min) / (z_max - z_min)

      uv_u = uv[:, :, 0] * 2.0 / image_size - 1
      uv_v = -uv[:, :, 1] * 2.0 / image_size + 1
      uv2d = torch.stack([uv_u, uv_v], axis=-1)
      uv4d = torch.cat([uv2d, z_buffer, torch.ones_like(z).to(device)], axis=-1)

    # TODO(Wang Yejiao): deep3d calculates perspective projection on face_vertex here, while frnet directly uses
    # projection results before. These two should be equivalent and may be verified later.
    vertex_ndc = (vertex @ ndc_proj.t()) if uv is None else uv4d
    if self.glctx is None:
      self.glctx = dr.RasterizeGLContext(device=device)
      # print("create glctx on device cuda:%d" % device.index)

    ranges = None
    if isinstance(tri, list) or len(tri.shape) == 3:
      vum = vertex_ndc.shape[1]
      fnum = torch.tensor([f.shape[0] for f in tri]).unsqueeze(1).to(device)
      fstartidx = torch.cumsum(fnum, dim=0) - fnum
      ranges = torch.cat([fstartidx, fnum], axis=1).type(torch.int32).cpu()
      for i in range(tri.shape[0]):
        tri[i] = tri[i] + i * vum
      vertex_ndc = torch.cat(vertex_ndc, dim=0)
      tri = torch.cat(tri, dim=0)

    # for range_mode vetex: [B*N, 4], tri: [B*M, 3], for instance_mode vetex: [B, N, 4], tri: [M, 3]
    tri = tri.type(torch.int32).contiguous()
    rast_out, _ = dr.rasterize(
        self.glctx,
        vertex_ndc.contiguous(),
        tri,
        resolution=[rsize, rsize],
        ranges=ranges)
    mask = (rast_out[..., 3] > 0).float().unsqueeze(1)

    rendered_albedo = None
    rendered_normal = None
    rendered_mask = None
    rendered_image = None
    depth = None

    if albedo is not None:
      rendered_albedo, _ = dr.interpolate(albedo.contiguous(), rast_out, tri)
      rendered_albedo = rendered_albedo.permute(0, 3, 1, 2)

    if normal is not None:
      rendered_normal, _ = dr.interpolate(normal.contiguous(), rast_out, tri)
      rendered_normal = rendered_normal.permute(0, 3, 1, 2)

    if face_mask is not None:
      rendered_mask, _ = dr.interpolate(face_mask.contiguous(), rast_out, tri)
      rendered_mask = rendered_mask.permute(0, 3, 1, 2)

    if color is not None:
      rendered_image, _ = dr.interpolate(color.contiguous(), rast_out, tri)
      rendered_image = rendered_image.permute(0, 3, 1, 2)

    if uv is None:
      vertex_depth = (
          vertex.reshape([-1, 4])[..., 2]
          if uv is None
          else vertex.reshape([-1, 3])[..., 2])
      depth, _ = dr.interpolate(vertex_depth.unsqueeze(1).contiguous(), rast_out, tri)
      depth = depth.permute(0, 3, 1, 2)
      depth = mask * depth

    return mask, depth, rendered_image, rendered_albedo, rendered_normal, rendered_mask
