import logging

import numpy as np
import pytorch_lightning as pl
import torch
from pytorch_lightning.callbacks import TQDMProgressBar
from pytorch_lightning.utilities.warnings import PossibleUserWarning
import warnings

from .data import MUSEDataModule
from .modules import MUSE


def fit_predict(
        transcript_features: np.array,
        morphology_features: np.array,
        transcript_labels: np.array,
        morphology_labels: np.array,
        batch_size: int = 512,
        **kwargs,
):

    warnings.filterwarnings("ignore", category=PossibleUserWarning)
    warnings.filterwarnings("ignore", ".*value needs to be floating point.*")
    muse = MUSE(transcript_features.shape[1],
                morphology_features.shape[1], **kwargs)

    muse_datamodule = MUSEDataModule(
        transcript_features, morphology_features, transcript_labels, morphology_labels, batch_size)

    trainer = pl.Trainer(accelerator='gpu', devices=1, max_epochs=-1,
                         callbacks=[TQDMProgressBar()], log_every_n_steps=1)

    trainer.fit(muse, muse_datamodule,)

    out = trainer.predict(muse, muse_datamodule,)

    # Combine outputs
    z = []
    x_hat = []
    y_hat = []
    latent_x = []
    latent_y = []

    for batch in out:
        z.append(batch['z'])
        x_hat.append(batch['x_hat'])
        y_hat.append(batch['y_hat'])
        latent_x.append(batch['latent_x'])
        latent_y.append(batch['latent_y'])

    z = torch.cat(z, dim=0)
    x_hat = torch.cat(x_hat, dim=0)
    y_hat = torch.cat(y_hat, dim=0)
    latent_x = torch.cat(latent_x, dim=0)
    latent_y = torch.cat(latent_y, dim=0)

    return z, x_hat, y_hat, latent_x, latent_y
