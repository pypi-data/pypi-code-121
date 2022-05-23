import torch
import torch.nn as nn
from typing import *  # type: ignore
from torch.utils.data import DataLoader

from torch.cuda.amp.autocast_mode import autocast
from torch.cuda.amp.grad_scaler import GradScaler
import itertools
import contextlib
import pandas as pd
from tqdm import tqdm


Inputs = TypeVar("Inputs", bound=dict[str, torch.Tensor] | torch.Tensor)
Preds = TypeVar("Preds", bound=dict[str, torch.Tensor] | torch.Tensor)
Targets = TypeVar("Targets", bound=dict[str, torch.Tensor] | torch.Tensor)

Loss = torch.Tensor
Losses = pd.DataFrame

Score = torch.Tensor  # Scores are losses which do not require differentiability
Metrics = dict[str, torch.Tensor]


def training_loop(
    model: Callable[[Inputs], Preds],
    *,
    dataloader: Iterable[tuple[Inputs, Targets]],  # type: ignore
    criterions: dict[str, tuple[float, Callable[[Inputs, Targets], Loss]]],
    optimizers: list[torch.optim.Optimizer],
    schedulers: list[torch.optim.lr_scheduler._LRScheduler] = [],
) -> Callable[[], Iterator[Losses]]:
    def loop():
        assert len(optimizers) > 0

        losses = pd.DataFrame(columns=list(criterions.keys()) + ["objective"])

        def step_fn(inputs, targets):
            preds = model(inputs)

            # Compute the losses for this iteration
            step_losses = {
                label: criterion(preds, targets)
                for label, (_, criterion) in criterions.items()
            }
            step_losses["objective"] = sum(
                [
                    criterions[label][0] * loss.mean(dim=0)
                    for label, loss in step_losses.items()
                ],
                torch.tensor(0.0),
            )

            # Append the losses to the dataframe object
            frame = pd.DataFrame(
                {label: [loss.item()] for label, loss in step_losses.items()}
            )
            assert set(frame.columns) == set(losses.columns)
            losses.loc[len(losses)] = frame.loc[0]  # todo nicer

            # Run backprop and return
            step_losses[
                "objective"
            ].backward()  #! what about 2 optimizers? this will call `backward` twice
            return step_losses["objective"]

        i = 0
        while True:
            for inputs, targets in dataloader:
                for optimizer in optimizers:
                    optimizer.zero_grad()
                    optimizer.step(lambda: step_fn(inputs, targets))

                for scheduler in schedulers:
                    scheduler.step()

                yield losses

                i += 1

    return loop



def evaluation_loop(
    model: Callable[[Inputs], Preds],
    *,
    dataloader: Iterable[Tuple[Inputs, Targets]],
    metrics: dict[str, Callable[[Preds, Targets], Score]],
) -> Callable[[], Iterable[tuple[Preds, pd.DataFrame]]]:

    @torch.inference_mode()
    def loop():
        scores = pd.DataFrame(columns=list(metrics.keys()))

        for inputs, targets in tqdm(dataloader, leave=False):
            preds = model(inputs)
            step_scores = {
                label: criterion(preds, targets) for label, criterion in metrics.items()
            }

            # Append the metrics to the dataframe object
            frame = pd.DataFrame(
                {label: [loss.item()] for label, loss in step_scores.items()}
            )
            assert set(frame.columns) == set(scores.columns)
            scores.loc[len(scores)] = frame.loc[0]  # todo nicer

            yield preds, scores

    return loop
