import torch
import torch.nn.functional as F


class DistanceLoss(torch.nn.Module):

    def __init__(self):
        super(DistanceLoss, self).__init__()

    def forward(self, q: torch.Tensor, z: torch.Tensor) -> torch.Tensor:
        norm_q = F.normalize(q, dim=-1, p=2)
        norm_z = F.normalize(z, dim=-1, p=2)
        loss = 2 - 2 * (norm_q * norm_z).sum(dim=-1)
        return loss.mean()
