import torch
from online_triplet_loss.losses import batch_hard_triplet_loss


class ReconstructionLoss:
    def __init__(self, ):
        pass

    def __call__(self, x, x_hat):
        return torch.mean(torch.norm(x_hat - x, p=2))


class ZIReconstructionLoss:
    def __init__(self, ):
        pass

    def __call__(self, x, x_hat):
        x_mask = torch.sign(x)
        return torch.sum(torch.norm(torch.multiply(x_mask, (x_hat - x)), p=2)) / torch.sum(x_mask)


class TripletLoss:
    def __init__(self, margin):
        self.margin = margin

    def __call__(self, labels, embeddings):
        return batch_hard_triplet_loss(labels, embeddings, margin=self.margin)
