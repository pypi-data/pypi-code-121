import torch 
import torch.cuda.amp as amp


class AmpOptimizer:
    def __init__(self, optimizer):
        self.optimizer = optimizer 
        self.scaler = amp.grad_scaler.GradScaler()

    def zero_grad(self):
        self.optimizer.zero_grad()

    def step(self, compute_loss):
        with amp.autocast_mode.autocast():
            loss = compute_loss()
        self.scaler.scale(loss).backward() # type: ignore
        self.scaler.update()
