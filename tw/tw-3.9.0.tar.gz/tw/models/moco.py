# Copyright (c) Facebook, Inc. and its affiliates. All Rights Reserved
import torch
import torch.nn as nn


class MoCo(nn.Module):
  """
  Build a MoCo model with: a query encoder, a key encoder, and a queue
  https://arxiv.org/abs/1911.05722
  """

  def __init__(self, base_encoder, dim=256, K=32 * 256, m=0.999, T=0.07, mlp=False):
    """
    dim: feature dimension (default: 128)
    K: queue size; number of negative keys (default: 65536)
    m: moco momentum of updating key encoder (default: 0.999)
    T: softmax temperature (default: 0.07)
    """
    super(MoCo, self).__init__()

    self.K = K
    self.m = m
    self.T = T

    # create the encoders
    # num_classes is the output fc dimension
    self.encoder_q = base_encoder()
    self.encoder_k = base_encoder()

    for param_q, param_k in zip(self.encoder_q.parameters(), self.encoder_k.parameters()):
      param_k.data.copy_(param_q.data)  # initialize
      param_k.requires_grad = False  # not update by gradient

    # create the queue
    self.register_buffer("queue", torch.randn(dim, K))
    self.queue = nn.functional.normalize(self.queue, dim=0)

    self.register_buffer("queue_ptr", torch.zeros(1, dtype=torch.long))

  @torch.no_grad()
  def _momentum_update_key_encoder(self):
    """
    Momentum update of the key encoder
    """
    for param_q, param_k in zip(self.encoder_q.parameters(), self.encoder_k.parameters()):
      param_k.data = param_k.data * self.m + param_q.data * (1. - self.m)

  @torch.no_grad()
  def _dequeue_and_enqueue(self, keys):
    # gather keys before updating queue
    # keys = concat_all_gather(keys)
    batch_size = keys.shape[0]

    ptr = int(self.queue_ptr)
    assert self.K % batch_size == 0  # for simplicity

    # replace the keys at ptr (dequeue and enqueue)
    self.queue[:, ptr:ptr + batch_size] = keys.transpose(0, 1)
    ptr = (ptr + batch_size) % self.K  # move pointer

    self.queue_ptr[0] = ptr

  @torch.no_grad()
  def _batch_shuffle_ddp(self, x):
    """
    Batch shuffle, for making use of BatchNorm.
    *** Only support DistributedDataParallel (DDP) model. ***
    """
    # gather from all gpus
    batch_size_this = x.shape[0]
    x_gather = concat_all_gather(x)
    batch_size_all = x_gather.shape[0]

    num_gpus = batch_size_all // batch_size_this

    # random shuffle index
    idx_shuffle = torch.randperm(batch_size_all).cuda()

    # broadcast to all gpus
    torch.distributed.broadcast(idx_shuffle, src=0)

    # index for restoring
    idx_unshuffle = torch.argsort(idx_shuffle)

    # shuffled index for this gpu
    gpu_idx = torch.distributed.get_rank()
    idx_this = idx_shuffle.view(num_gpus, -1)[gpu_idx]

    return x_gather[idx_this], idx_unshuffle

  @torch.no_grad()
  def _batch_unshuffle_ddp(self, x, idx_unshuffle):
    """
    Undo batch shuffle.
    *** Only support DistributedDataParallel (DDP) model. ***
    """
    # gather from all gpus
    batch_size_this = x.shape[0]
    x_gather = concat_all_gather(x)
    batch_size_all = x_gather.shape[0]

    num_gpus = batch_size_all // batch_size_this

    # restored index for this gpu
    gpu_idx = torch.distributed.get_rank()
    idx_this = idx_unshuffle.view(num_gpus, -1)[gpu_idx]

    return x_gather[idx_this]

  def forward(self, im_q, im_k):
    """
    Input:
        im_q: a batch of query images
        im_k: a batch of key images
    Output:
        logits, targets
    """
    if self.training:
      # compute query features
      embedding, q, feat = self.encoder_q(im_q)  # queries: NxC
      q = nn.functional.normalize(q, dim=1)

      # compute key features
      with torch.no_grad():  # no gradient to keys
        self._momentum_update_key_encoder()  # update the key encoder

        _, k, feat = self.encoder_k(im_k)  # keys: NxC
        k = nn.functional.normalize(k, dim=1)

      # compute logits
      # Einstein sum is more intuitive
      # positive logits: Nx1
      l_pos = torch.einsum('nc,nc->n', [q, k]).unsqueeze(-1)
      # negative logits: NxK
      l_neg = torch.einsum('nc,ck->nk', [q, self.queue.clone().detach()])

      # logits: Nx(1+K)
      logits = torch.cat([l_pos, l_neg], dim=1)

      # apply temperature
      logits /= self.T

      # labels: positive key indicators
      labels = torch.zeros(logits.shape[0], dtype=torch.long).to(im_q.device)

      # dequeue and enqueue
      self._dequeue_and_enqueue(k)

      return embedding, logits, labels, feat
    else:
      embedding, _, feat = self.encoder_q(im_q)

      return embedding, feat


# utils
@torch.no_grad()
def concat_all_gather(tensor):
  """
  Performs all_gather operation on the provided tensors.
  *** Warning ***: torch.distributed.all_gather has no gradient.
  """
  tensors_gather = [torch.ones_like(tensor)
                    for _ in range(torch.distributed.get_world_size())]
  torch.distributed.all_gather(tensors_gather, tensor, async_op=False)

  output = torch.cat(tensors_gather, dim=0)
  return output


# class Encoder(nn.Module):

#   def __init__(self):
#     super(Encoder, self).__init__()

#     self.E = nn.Sequential(
#         nn.Conv2d(1, 64, kernel_size=3, padding=1),
#         nn.BatchNorm2d(64),
#         nn.LeakyReLU(0.1, True),
#         nn.Conv2d(64, 64, kernel_size=3, padding=1),
#         nn.BatchNorm2d(64),
#         nn.LeakyReLU(0.1, True),
#         nn.Conv2d(64, 128, kernel_size=3, stride=2, padding=1),
#         nn.BatchNorm2d(128),
#         nn.LeakyReLU(0.1, True),
#         nn.Conv2d(128, 128, kernel_size=3, padding=1),
#         nn.BatchNorm2d(128),
#         nn.LeakyReLU(0.1, True),
#         nn.Conv2d(128, 256, kernel_size=3, stride=2, padding=1),
#         nn.BatchNorm2d(256),
#         nn.LeakyReLU(0.1, True),
#         nn.Conv2d(256, 256, kernel_size=3, padding=1),
#         nn.BatchNorm2d(256),
#         nn.LeakyReLU(0.1, True),
#         nn.AdaptiveAvgPool2d(1),
#     )
#     self.mlp = nn.Sequential(
#         nn.Linear(256, 256),
#         nn.LeakyReLU(0.1, True),
#         nn.Linear(256, 256),
#     )

#   def forward(self, x):
#     fea = self.E(x).squeeze(-1).squeeze(-1)
#     out = self.mlp(fea)

#     return fea, out


# if __name__ == "__main__":

#   moco = MoCo(base_encoder=Encoder)
#   moco.cuda()

#   lr_query = torch.randn(8, 1, 360, 640).cuda()
#   lr_key = torch.randn(8, 1, 360, 640).cuda()

#   with torch.no_grad():
#     feat, logits, labels = moco(lr_query, lr_key)
#     print(logits.mean(dim=1))
#     print(labels)
#     print(feat.shape, logits.shape, labels.shape)
