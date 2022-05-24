from abc import ABCMeta
from abc import abstractmethod
from os import getpid
from pathlib import Path
from typing import Optional
from typing import Tuple
from typing import Union

import torch
from torch import nn
from torch.optim import Optimizer
from torch.utils.data import DataLoader
from torch_optimizer import RAdam
from tqdm.auto import tqdm

from enot.logging.trackers import RunningMeanLogger

# We are using absolute imports here instead of simple imports like
# ``from enot.quantization import calibrate_quantized_model``. This
# is because this file is part of the ``enot.quantization`` package,
# and it is used in enot.quantization.__init__.py file, so simple
# imports would cause circular import error.
#
# Please use simple imports in your projects instead of absolute ones.
from enot.quantization.calibration.network_calibration import calibrate_quantized_model
from enot.quantization.distillation.utils import DistillationLayerSelectionStrategy
from enot.quantization.distillation.utils import distillation_context
from enot.quantization.fake_quantized_model import FakeQuantizedModel
from enot.quantization.utils.common import float_model_from_quantized_model
from enot.utils.data.dataloaders import recursive_to
from enot.utils.dataloader2model import DataLoaderSampleToModelInputs
from enot.utils.dataloader2model import default_sample_to_model_inputs
from enot.utils.train import Scheduler


class RMSELoss(nn.Module):

    def __init__(self, eps: float = 1e-6):
        super().__init__()
        self.mse: nn.MSELoss = nn.MSELoss()
        self.eps: float = eps

    def forward(self, input: torch.Tensor, target: torch.Tensor) -> torch.Tensor:
        loss = torch.sqrt(self.mse(input, target) + self.eps)
        return loss


KNOWN_CRITERIA = {
    'RMSELoss': RMSELoss,
    'MSELoss': nn.MSELoss,
    'CrossEntropyLoss': nn.CrossEntropyLoss,
}


def parse_distillation_criterion(criterion: Union[torch.nn.Module, str]) -> torch.nn.Module:
    if isinstance(criterion, nn.Module):
        return criterion
    if isinstance(criterion, str):
        return KNOWN_CRITERIA[criterion]()
    raise TypeError(f'Unknown criterion type: {type(criterion)}')


class DistillerInterface(metaclass=ABCMeta):
    """Distiller base interface."""

    @abstractmethod
    def distill(self) -> None:
        """Launches distillation procedure."""
        pass


class QuantizationDistiller(DistillerInterface):
    """Quantized model distillation class with a simple distillation implementation."""

    def __init__(
            self,
            quantized_model: FakeQuantizedModel,
            dataloader: DataLoader,
            optimizer: Optional[Optimizer] = None,
            scheduler: Optional[Scheduler] = None,
            distillation_layer_selection_strategy: DistillationLayerSelectionStrategy =
            DistillationLayerSelectionStrategy.DISTILL_LAST_QUANT_LAYERS,
            distillation_criterion: Union[torch.nn.Module, str] = 'RMSELoss',
            n_epochs: int = 1,
            device: Union[str, torch.device] = 'cuda:0',
            sample_to_model_inputs: DataLoaderSampleToModelInputs = default_sample_to_model_inputs,
            logdir: Optional[Union[str, Path]] = None,
            save_every: Optional[int] = None,
            verbose: int = 0,
    ):
        """
        Parameters
        ----------
        quantized_model : FakeQuantizedModel
            Fake-quantized model.
        dataloader : torch.utils.data.DataLoader
            Dataloader with model inputs for distillation.
        optimizer : torch.optim.Optimizer or None, optional
            Optimizer instance.
        scheduler : Scheduler or None, optional
            Scheduler instance.
        distillation_layer_selection_strategy : DistillationStrategy, optional
            Distillation layer selection strategy. Default value is DISTILL_LAST_QUANT_LAYERS.
        distillation_criterion : Callable, optional
            Distillation criterion module. Default criterion is RMSE.
        n_epochs : int, optional
            Number of epochs for distillation. Default value is 1.
        device : str or torch.device, optional
            Device to use during distillation. Default value is "cuda:0".
        sample_to_model_inputs : Callable, optional
            Function to map dataloader samples to model input format. Default value is
            :func:`.default_sample_to_model_inputs`. See more :ref:`here <s2mi ref>`.
        logdir : str or Path or None, optional
            Save directory. Default value is None, which disables logging to directory.
        save_every : int or None, optional
            Save checkpoint every n steps. Default value is None, which disables intermediate model checkpoints.
        verbose : int, optional
            Verbosity level. Default value is 0.

        """
        self.quantized_model = quantized_model
        self.dataloader = dataloader

        self.optimizer = optimizer
        self.scheduler = scheduler

        self.distillation_strategy = distillation_layer_selection_strategy
        self.distillation_criterion = parse_distillation_criterion(distillation_criterion)

        self.n_epochs = n_epochs
        self.device = device
        self.sample_to_model_inputs = sample_to_model_inputs

        self.logdir = logdir
        self.save_every = save_every
        self.verbose = verbose

        self.quantized_model.to(self.device)
        self.quantized_model.train()
        self.quantized_model.enable_quantization_mode(True)

        self.loss_logger = RunningMeanLogger()

        self.minimal_loss_value: Optional[float] = None

        if self.logdir is not None:
            self.logdir = Path(self.logdir)
            self.logdir.mkdir(exist_ok=True, parents=True)

    def distill(self) -> None:
        with distillation_context(self.quantized_model, self.distillation_strategy):
            quantized_model = self.quantized_model
            regular_model = float_model_from_quantized_model(quantized_model)
            self._base_distill(quantized_model, regular_model)

    def save(self, checkpoint_path: Path) -> None:
        """Saves quantized model state dict to the specified path."""
        torch.save(self.quantized_model.state_dict(), checkpoint_path)

    def _base_distill(
            self,
            quantized_model: FakeQuantizedModel,
            regular_model: FakeQuantizedModel,
    ) -> None:
        """Main distillation fine-tuning loop."""
        best_model_path = None

        checkpoint_dir = None
        if self.logdir is not None:
            checkpoint_dir = self.logdir / 'model_checkpoints'
            checkpoint_dir.mkdir(exist_ok=True)

        total_steps = 0
        for epoch in range(self.n_epochs):

            tqdm_iterator = tqdm(self.dataloader, disable=(self.verbose == 0))
            for batch in tqdm_iterator:

                self.optimizer.zero_grad()

                model_args, model_kwargs = self.sample_to_model_inputs(batch)
                recursive_to(model_args, device=self.device, ignore_non_tensors=True)
                recursive_to(model_kwargs, device=self.device, ignore_non_tensors=True)

                quantized_output = quantized_model(*model_args, **model_kwargs)
                with torch.no_grad():
                    regular_output = regular_model(*model_args, **model_kwargs)

                loss: Union[float, torch.Tensor] = 0.0
                for q_out, r_out in zip(quantized_output, regular_output):
                    loss += self.distillation_criterion(q_out, r_out)

                loss.backward()

                self.optimizer.step()
                if self.scheduler is not None:
                    self.scheduler.step()

                total_steps += 1

                self.loss_logger.tracked_value = loss.item()

                min_loss_updated = False
                if self.minimal_loss_value is None or (self.loss_logger.tracked_value < self.minimal_loss_value):
                    self.minimal_loss_value = self.loss_logger.tracked_value
                    min_loss_updated = True

                if checkpoint_dir is not None:

                    if self.save_every is not None and total_steps % self.save_every == self.save_every - 1:
                        self.save(checkpoint_dir / f'model_{epoch}_{total_steps}.pth')

                    if min_loss_updated:
                        best_model_path = checkpoint_dir / 'best_model.pth'
                        self.save(best_model_path)

                tqdm_iterator.set_description(
                    f'loss: {self.loss_logger.tracked_value:.5f}, '
                    f'min loss: {self.minimal_loss_value:.5f}'
                )

        if best_model_path is not None:
            quantized_model.load_state_dict(torch.load(best_model_path))


class SequentialDistiller(DistillerInterface):
    """Compound distillation class which performs sequential distillation with multiple strategies."""

    def __init__(self, *distillers: DistillerInterface):
        """
        Parameters
        ----------
        distillers : tuple with DistillerInterface
            Tuple with distiller instances.

        """
        self.distillers: Tuple[DistillerInterface] = distillers

    def distill(self) -> None:
        for distiller in self.distillers:
            distiller.distill()


class ThresholdsQuantizationDistiller(QuantizationDistiller):
    """Quantization distiller for thresholds with a default well-performing distillation configuration."""

    def __init__(
            self,
            quantized_model: FakeQuantizedModel,
            dataloader: DataLoader,
            device: Union[str, torch.device] = 'cuda:0',
            sample_to_model_inputs: DataLoaderSampleToModelInputs = default_sample_to_model_inputs,
            logdir: Optional[Union[str, Path]] = None,
            save_every: Optional[int] = None,
            n_batches_calibrate: int = 10,
            verbose: int = 0,
    ):
        """
        Parameters
        ----------
        quantized_model : FakeQuantizedModel
            Fake-quantized model.
        dataloader : torch.utils.data.DataLoader
            Dataloader with model inputs for distillation.
        device : str or torch.device, optional
            Device to use during distillation. Default value is "cuda:0".
        sample_to_model_inputs : Callable, optional
            Function to map dataloader samples to model input format. Default value is
            :func:`.default_sample_to_model_inputs`. See more :ref:`here <s2mi ref>`.
        logdir : str or Path or None, optional
            Save directory. Default value is None, which disables logging to directory.
        save_every : int or None, optional
            Save checkpoint every n steps. Default value is None, which disables intermediate model checkpoints.
        verbose : int, optional
            Verbosity level. Default value is 0.

        """
        n_epochs = 1
        batches_in_epoch = len(dataloader)
        self.n_batches_calibrate: int = n_batches_calibrate

        if logdir is not None:
            logdir = Path(logdir) / f'{getpid()}_{id(quantized_model)}'
            if verbose:
                print(f'The working directory is {logdir.as_posix()}')
        threshold_logdir = None if logdir is None else (logdir / 'threshold_distillation')

        threshold_optimizer = RAdam(
            params=quantized_model.quantization_parameters(),
            lr=0.05,
            betas=(0.9, 0.95)
        )
        threshold_scheduler = torch.optim.lr_scheduler.CosineAnnealingLR(
            optimizer=threshold_optimizer,
            T_max=batches_in_epoch * n_epochs,
        )

        super().__init__(
            quantized_model=quantized_model,
            dataloader=dataloader,
            optimizer=threshold_optimizer,
            scheduler=threshold_scheduler,
            distillation_layer_selection_strategy=DistillationLayerSelectionStrategy.DISTILL_LAST_QUANT_LAYERS,
            distillation_criterion=RMSELoss(),
            n_epochs=n_epochs,
            device=device,
            sample_to_model_inputs=sample_to_model_inputs,
            logdir=threshold_logdir,
            save_every=save_every,
            verbose=verbose,
        )

    def distill(self) -> None:
        calibrate_quantized_model(
            quantized_model=self.quantized_model,
            dataloader=self.dataloader,
            n_steps=self.n_batches_calibrate,
            sample_to_model_inputs=self.sample_to_model_inputs,
            verbose=self.verbose,
        )
        if self.verbose >= 2:
            print('Fine-tuning quantization thresholds.')
        super().distill()


class ScaleFactorsQuantizationDistiller(QuantizationDistiller):
    """
    Quantization distiller for thresholds and scale factors
    with a default well-performing distillation configuration.
    """

    def __init__(
            self,
            quantized_model: FakeQuantizedModel,
            dataloader: DataLoader,
            device: Union[str, torch.device] = 'cuda:0',
            sample_to_model_inputs: DataLoaderSampleToModelInputs = default_sample_to_model_inputs,
            logdir: Optional[Union[str, Path]] = None,
            save_every: Optional[int] = None,
            n_batches_calibrate: int = 10,
            verbose: int = 0,
    ):
        """
        Parameters
        ----------
        quantized_model : FakeQuantizedModel
            Fake-quantized model.
        dataloader : torch.utils.data.DataLoader
            Dataloader with model inputs for distillation.
        device : str or torch.device, optional
            Device to use during distillation. Default value is "cuda:0".
        sample_to_model_inputs : Callable, optional
            Function to map dataloader samples to model input format. Default value is
            :func:`.default_sample_to_model_inputs`. See more :ref:`here <s2mi ref>`.
        logdir : str or Path or None, optional
            Save directory. Default value is None, which disables logging to directory.
        save_every : int or None, optional
            Save checkpoint every n steps. Default value is None, which disables intermediate model checkpoints.
        verbose : int, optional
            Verbosity level. Default value is 0.

        """
        n_epochs = 1
        batches_in_epoch = len(dataloader)
        self.n_batches_calibrate: int = n_batches_calibrate

        if logdir is not None:
            logdir = Path(logdir) / f'{getpid()}_{id(quantized_model)}'
            if verbose:
                print(f'The working directory is {logdir.as_posix()}')
        threshold_logdir = None if logdir is None else (logdir / 'threshold_distillation')

        threshold_optimizer = RAdam(
            params=[*quantized_model.quantization_parameters(), *quantized_model.scale_factors()],
            lr=0.005,
            betas=(0.9, 0.95),
        )
        threshold_scheduler = torch.optim.lr_scheduler.CosineAnnealingLR(
            optimizer=threshold_optimizer,
            T_max=batches_in_epoch * n_epochs,
        )

        super().__init__(
            quantized_model=quantized_model,
            dataloader=dataloader,
            optimizer=threshold_optimizer,
            scheduler=threshold_scheduler,
            distillation_layer_selection_strategy=DistillationLayerSelectionStrategy.DISTILL_ALL_QUANT_LAYERS,
            distillation_criterion=RMSELoss(),
            n_epochs=n_epochs,
            device=device,
            sample_to_model_inputs=sample_to_model_inputs,
            logdir=threshold_logdir,
            save_every=save_every,
            verbose=verbose,
        )

    def distill(self) -> None:
        calibrate_quantized_model(
            quantized_model=self.quantized_model,
            dataloader=self.dataloader,
            n_steps=self.n_batches_calibrate,
            sample_to_model_inputs=self.sample_to_model_inputs,
            verbose=self.verbose,
        )
        if self.verbose >= 2:
            print('Fine-tuning quantization thresholds and scale factors.')
        super().distill()


DefaultQuantizationDistiller = ScaleFactorsQuantizationDistiller
