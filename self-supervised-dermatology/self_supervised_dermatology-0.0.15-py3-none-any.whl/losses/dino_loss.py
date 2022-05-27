import torch
import numpy as np
import torch.nn.functional as F
import torch.distributed as dist
from torch import nn


class DINOLoss(nn.Module):
    def __init__(self,
                 out_dim,
                 n_crops,
                 n_g_crops,
                 warmup_teacher_temp,
                 teacher_temp,
                 warmup_teacher_temp_epochs,
                 n_epochs,
                 student_temp=0.1,
                 center_momentum=0.9):
        super().__init__()
        self.student_temp = student_temp
        self.center_momentum = center_momentum
        self.n_crops = n_crops
        self.n_g_crops = n_g_crops
        self.register_buffer("center", torch.zeros(1, out_dim))
        # we apply a warm up for the teacher temperature because
        # a too high temperature makes the training instable at the beginning
        self.teacher_temp_schedule = np.concatenate(
            (np.linspace(warmup_teacher_temp, teacher_temp, warmup_teacher_temp_epochs),
             np.ones(n_epochs - warmup_teacher_temp_epochs) * teacher_temp))

    def forward(self, student_output, teacher_output, epoch):
        """
        Cross-entropy between softmax outputs of the teacher and student networks.
        """
        student_out = student_output / self.student_temp
        student_out = student_out.chunk(self.n_crops)

        # teacher centering and sharpening
        temp = self.teacher_temp_schedule[epoch]
        teacher_out = F.softmax((teacher_output - self.center) / temp, dim=-1)
        teacher_out = teacher_out.detach().chunk(self.n_g_crops)

        total_loss = 0
        n_loss_terms = 0
        for i_t in range(len(teacher_out)):
            for i_s in range(len(student_out)):
                if i_s == i_t:
                    # we skip cases where student and teacher
                    # operate on the same view
                    continue
                q = teacher_out[i_t]
                loss = torch.sum(-q * F.log_softmax(student_out[i_s], dim=-1),
                                 dim=-1)
                total_loss += loss.mean()
                n_loss_terms += 1
        total_loss /= n_loss_terms
        self.update_center(teacher_output)
        return total_loss

    @torch.no_grad()
    def update_center(self, teacher_output):
        """
        Update center used for teacher output.
        """
        batch_center = torch.sum(teacher_output, dim=0, keepdim=True)
        dist.all_reduce(batch_center)
        batch_center = batch_center / (len(teacher_output) * dist.get_world_size())

        # ema update
        self.center = self.center * self.center_momentum + batch_center * (
            1 - self.center_momentum)
