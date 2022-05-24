# -*- coding: utf-8 -*-


class LinearDecayScheduledSampling(object):
    def __init__(
        self, max_epochs: int, k: float = 1.0, c: float = 1.0, eps: float = 0.0
    ):
        self.max_epochs = max_epochs
        self.k = k
        self.c = c
        self.eps = eps
        self.epoch = -1
        self.step()

    @property
    def teacher_forcing_ratio(self):
        return self.value

    def step(self) -> None:
        self.epoch += 1
        self.value = max(self.k - self.c * self.epoch / self.max_epochs, self.eps)
