import torch
import torch.nn as nn
from typing import *  # type: ignore
from torch.utils.data import DataLoader

from torch.cuda.amp.autocast_mode import autocast
from torch.cuda.amp.grad_scaler import GradScaler
from contextlib import nullcontext
import pandas as pd
from tqdm import tqdm
import dataclasses
from dataclasses import dataclass, field


Inputs = TypeVar("Inputs")
Preds = TypeVar("Preds")
Targets = TypeVar("Targets")

Loss = torch.Tensor
Losses = dict[str, Loss]

# Scores are losses which do not require differentiability
Score = torch.Tensor  
Scores = dict[str, Score]

Weight = float
Criterion = Callable[[Preds, Targets], Loss]


Metric = Callable[[Preds, Targets], Score]


@dataclass
class TrainingLoop(Generic[Inputs, Preds, Targets]):
    model: Callable[[Inputs], Preds]
    _ = dataclasses.KW_ONLY
    dataloader: Iterable[tuple[Inputs, Targets]]
    criterions: dict[str, tuple[Weight, Criterion]]
    optimizers: Iterable[torch.optim.Optimizer]
    schedulers: Iterable[torch.optim.lr_scheduler._LRScheduler] = ()
    amp: bool = True
    seed: int = 0

    _scaler: Optional[GradScaler] = None

    def __post_init__(self):
        self._scaler = GradScaler() if self.amp else None

    def step(self, inputs: Inputs, targets: Targets) -> tuple[Preds, dict[str, Loss]]:
        preds = self.model(inputs)

        losses = {
            label: criterion(preds, targets)
            for label, (_, criterion) in self.criterions.items()
        }

        objective = torch.tensor(0.0)
        for label, loss in losses.items():
            weight = self.criterions[label][0]
            objective += weight * loss.mean(dim=0)

        return preds, (losses | {"objective": objective})

    def __iter__(self) -> Iterator[tuple[Preds, Losses]]:
        torch.manual_seed(self.seed)

        i = 0
        for inputs, targets in self.dataloader:
            for optimizer in self.optimizers:
                optimizer.zero_grad()

            with autocast() if self.amp else nullcontext():
                preds, losses = self.step(inputs, targets)

            if self._scaler is not None:
                self._scaler.scale(losses["objective"]).backward()  # type: ignore
            else:
                losses["objective"].backward()

            for optimizer in self.optimizers:
                if self._scaler is not None:
                    self._scaler.step(optimizer) # type: ignore
                else:
                    optimizer.step()

            for scheduler in self.schedulers:
                scheduler.step()

            if self._scaler is not None:
                self._scaler.update()

            yield preds, losses

            i += 1


@dataclass
class EvaluationLoop(Generic[Inputs, Preds, Targets]):
    model: Callable[[Inputs], Preds]
    _ = dataclasses.KW_ONLY
    dataloader: Iterable[tuple[Inputs, Targets]]
    metrics: dict[str, Callable[[Preds, Targets], Score]]
    amp: bool = True
    seed: int = 0

    def __iter__(self) -> Iterator[tuple[Preds, Scores]]:
        torch.manual_seed(self.seed)

        with torch.inference_mode():
            was_training = self.model.training
            self.model.train(False)
            
            for inputs, targets in self.dataloader:
                with autocast() if self.amp else nullcontext():
                    preds = self.model(inputs)
                    scores = {
                        label: criterion(preds, targets)
                        for label, criterion in self.metrics.items()
                    }

                
                    yield preds, scores

            self.model.train(was_training)
