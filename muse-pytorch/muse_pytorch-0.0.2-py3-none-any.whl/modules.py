import os
from this import d
from typing import Tuple
import muse_sc

import numpy as np
import phenograph
import pytorch_lightning as pl
import torch
from scipy.spatial.distance import pdist

from .blocks import Decoder, Encoder, MultiViewEncoder, WeightMatrix
from .losses import ReconstructionLoss, TripletLoss, ZIReconstructionLoss
from .utils import block_print, enable_print


class MUSE(pl.LightningModule):
    def __init__(self,
                 ts_input_dim: int = 500,
                 ml_input_dim: int = 2048,
                 latent_dim: int = 128,
                 joint_latent_dim: int = 100,
                 lambda_reg: float = 5.,
                 lambda_sup: float = 5.,
                 lr: float = 1e-04,
                 init_epochs: int = 100,
                 refine_epochs: int = 100,
                 cluster_epochs: int = 100,
                 cluster_update_epoch: int = 50
                 ) -> None:
        """MUSE implementation in pytorch-lightning.

        This implementation tries to stay as close as possible to the original one, but it is not always possible.
        For convenience, the training has been divided in 3 phases that I arbitrarily called initialziation, refinement and clustering.

         - The initialziation phase only aims at optimizing the reconstruction part of the network. 
        For this reason in the first phase no self-supervised loss or clustering is computed.
        At the end of the initialization phase the margin of the triplet loss is estimated and the self-supervised loss is activated.
         - The refinement phase trains both on the recosntruction and self-supervised loss. 
         Although, at this time no further clustering of the samples is computed, and the loss uses only the reference labels
          - The clustering phase also refines the initial clusters, by running a clustering algorithm every cluster_update_epoch epochs.

        Args:
            ts_input_dim (int, optional): Number of features in the transcript modality. Defaults to 500.
            ml_input_dim (int, optional): Number of features in the morphology modality. Defaults to 2048.
            latent_dim (int, optional): Size of the latent dimension of the encoded single modalities (hx and yx in the paper). Defaults to 128.
            joint_latent_dim (int, optional): Size of the latent dimension of the joint modalities (z in the paper). Defaults to 100.
            lambda_reg (float, optional): Wegith for the regularization term in the loss function (lambda_regularization in the paper). Defaults to 5..
            lambda_sup (float, optional): Wegith for the self-supervised term in the loss function (lambda_supervise in the paper). Defaults to 5..
            lr (float, optional): Learning rate for the model. Defaults to 1e-04.
            init_epochs (int, optional): Number of epochs of the initialiation part of training. Defaults to 100.
            refine_epochs (int, optional): Number of epochs of the refining part of training. Defaults to 100.
            cluster_epochs (int, optional): Number of epochs for the clustering part of training. Defaults to 100.
            cluster_update_epoch (int, optional): Number of epoch after which the clustering on the single modalities are updated. Defaults to 50.
        """
        super().__init__()

        self.save_hyperparameters()
        self.mve = MultiViewEncoder(
            in_features_x=ts_input_dim,
            in_features_y=ml_input_dim,
            sm_latent_dim=latent_dim,
            joint_latent_dim=joint_latent_dim
        )

        self.wm_x = WeightMatrix(joint_latent_dim=joint_latent_dim)
        self.wm_y = WeightMatrix(joint_latent_dim=joint_latent_dim)

        self.decoder_x = Decoder(
            in_features=joint_latent_dim,
            out_features=ts_input_dim
        )

        self.decoder_y = Decoder(
            in_features=joint_latent_dim,
            out_features=ml_input_dim
        )

        # Triplet loss function
        self.triplet_loss = TripletLoss(margin=0)
        # Reconstruction loss function
        self.rec_loss = ReconstructionLoss()
        # Zero Inflated reconstruction loss function
        self.zi_rec_loss = ZIReconstructionLoss()

        self.phase = 'init'

    # Move this function into the datamodule

    def _cluster_latent(self, latent_x: torch.Tensor, latent_y: torch.Tensor) -> Tuple[np.array]:
        """Performs clustering over latent representations of single modalities.

        Args:
            latent_x (torch.Tensor): Latent representation of the transcript modality
            latent_y (torch.Tensor): Latent representation of the morphological modality

        Returns:
            Tuple[np.array]: containing the cluster labels for each sample in both modalities.
        """

        block_print()
        labels_x, _, Q_x = phenograph.cluster(latent_x.detach().cpu())
        labels_y, _, Q_y = phenograph.cluster(latent_y.detach().cpu())
        enable_print()

        print(f'Clustering done! Q scores for x and y are {Q_x}\t{Q_y} ')

        return labels_x, labels_y

    def estimate_margin(self, z: torch.Tensor) -> None:
        """Compute margin estimation and redefine triplet loss with the newly computer margin

        Args:
            z (torch.Tensor): Joint latent representation 
        """

        latent_pd_matrix = pdist(z.detach().cpu(), 'euclidean')
        latent_pd_sort = np.sort(latent_pd_matrix)
        select_top_n = np.int(latent_pd_sort.size * 0.2)
        margin_estimate = np.median(
            latent_pd_sort[-select_top_n:]) - np.median(latent_pd_sort[:select_top_n])

        # Store margin and re-initialize loss
        self.hparams.triplet_margin = margin_estimate
        self.triplet_loss = TripletLoss(margin=margin_estimate)

    def configure_optimizers(self):
        optimizer = torch.optim.Adam(
            self.parameters(), lr=self.hparams.lr)
        return optimizer

    def predict_step(self, batch, batch_idx):

        x, y = batch

        z, latent_x, latent_y = self.mve(x, y)

        z_x, z_y = self.wm_x(z), self.wm_y(z)

        x_hat,  y_hat = self.decoder_x(z_x), self.decoder_y(z_y)

        return {'z': z, 'x_hat': x_hat, 'y_hat': y_hat, 'latent_x': latent_x, 'latent_y': latent_y}

    def training_step(self, batch, batch_idx):

        # I will try to keep the same naming as the original implementation
        (x, y), (labels_x, labels_y) = batch['features'], batch['labels']

        # Get Single Modality and joint latent spaces from the multi-view encoder
        z, latent_x, latent_y = self.mve(x, y)

        # Get modality specific latent space from joint latent space
        z_x, z_y = self.wm_x(z), self.wm_y(z)

        # Decode the modality specific latent spaces to reconstruct original features
        x_hat,  y_hat = self.decoder_x(z_x), self.decoder_y(z_y)

        #==== Loss ====#
        # Frobenious norm minimization
        sparse_penality = self.wm_x.fnorm() + self.wm_y.fnorm()

        # Reconstruction loss for each single modality
        rec_loss = self.rec_loss(x, x_hat) + self.rec_loss(y, y_hat)

        # Triplet loss (not computed during init phase)
        if self.phase != 'init':
            triplet_loss = self.triplet_loss(labels_x, latent_x) \
                + self.triplet_loss(labels_y, latent_y)
        else:
            triplet_loss = 0

        loss = rec_loss + self.hparams.lambda_reg * \
            sparse_penality + self.hparams.lambda_sup * triplet_loss

        self.log(f"loss",
                 {"reconstruction": rec_loss, "triplet": triplet_loss, "total": loss},
                 prog_bar=False, on_step=False, on_epoch=True)

        return {'loss': loss, 'latent_x': latent_x, 'latent_y': latent_y, 'z': z}

    def training_epoch_end(self, outputs) -> None:

        # Switch training phase according to input parameters
        # End of init phase -> refine phase
        if self.trainer.current_epoch + 1 == self.hparams.init_epochs:
            self.phase = 'refine'

            # At the end of the refine phase we can estimate the margin for the triplet loss
            z = torch.cat([batch['z'] for batch in outputs])
            self.estimate_margin(z)

            print('Initalization phase completed. Moving to Refining phase.')

        elif self.trainer.current_epoch + 1 == self.hparams.init_epochs + self.hparams.refine_epochs:
            self.phase = 'cluster'

            print('Refining phase completed. Moving to Clustering phase.')

        # When running cluster, we must update our labels
        if self.phase == 'cluster':

            cluster_epoch = self.trainer.current_epoch - \
                (self.hparams.init_epochs + self.hparams.refine_epochs)

            # Update clusters every cluster_update_epoch epochs for the start of the cluster phase
            if cluster_epoch % self.hparams.cluster_update_epoch == 0:
                latent_x = torch.cat([batch['latent_x']
                                      for batch in outputs])
                latent_y = torch.cat([batch['latent_y']
                                      for batch in outputs])

                x_labels, y_labels = self._cluster_latent(
                    latent_x, latent_y)

                self.trainer.datamodule.update_labels(x_labels, y_labels)
                self.trainer.reset_train_dataloader()

        if self.trainer.current_epoch + 1 == self.hparams.init_epochs + self.hparams.refine_epochs + self.hparams.cluster_epochs:
            self.trainer.should_stop = True
            self.z = torch.cat([batch['z'] for batch in outputs])
            torch.save(self.z, os.path.join(self.trainer.log_dir, "z.pt"))
            print('Clustering phase completed. Training done.')
