"""Contains PyTorch specific utility methods."""
from enum import Enum
import logging

import pytorch_lightning.loggers as pl_loggers
import torch

logger = logging.getLogger(__name__)


def _autodetect_gpu() -> int:
    """Detects and returns the number of GPUs available."""
    # Run on GPU if available
    gpus: int = torch.cuda.device_count()
    if gpus > 0:
        gpu_0_name: str = torch.cuda.get_device_name(0)

    # Reduce to 1 GPU if multiple detected
    # TODO: [BIT-492] Add multi-GPU support.
    if gpus > 1:
        logger.warning(
            f"Bitfount model currently only supports one GPU. "
            f"Will use GPU 0 ({gpu_0_name})."
        )
        gpus = 1

    # Log GPU state
    if gpus == 1:
        logger.info(f"CUDA support detected. GPU ({gpu_0_name}) will be used.")
    else:
        logger.info("No supported GPU detected. Running model on CPU.")
    return gpus


class LoggerType(Enum):
    """Different types of loggers for PyTorchLightning.

    With the exception of CSVLogger and TensorBoardLogger, all loggers need to have
    their corresponding python libraries installed separately.

    More information about PyTorchLightning loggers can be found here:
    https://pytorch-lightning.readthedocs.io/en/latest/common/loggers.html
    """

    CSVLogger = pl_loggers.CSVLogger
    MLFlow = pl_loggers.MLFlowLogger
    Neptune = pl_loggers.NeptuneLogger
    TensorBoard = pl_loggers.TensorBoardLogger
    TestTube = pl_loggers.TestTubeLogger
    WeightsAndBiases = pl_loggers.WandbLogger
