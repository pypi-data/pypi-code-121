from typing import Optional

import numpy as np
import pytorch_lightning as pl
import torch
from torch.utils.data import DataLoader, Dataset


class MUSEFeaturesDataset(Dataset):
    def __init__(self,
                 transcript_features: np.array,
                 morphology_features: np.array) -> None:

        self.morphology_features = morphology_features
        self.transcript_features = transcript_features

        assert morphology_features.shape[0] == transcript_features.shape[
            0], "The first dimension of both features should be equal to the sample size"

    def get_sample_size(self):
        return self.morphology_features.shape[0]

    def __getitem__(self, index: int):
        return (
            torch.tensor(self.transcript_features[index]).float(),
            torch.tensor(self.morphology_features[index]).float(),)

    def __len__(self):
        return self.transcript_features.shape[0]


class MUSELabelsDataset(Dataset):
    def __init__(self,
                 transcript_labels: np.array,
                 morphology_labels: np.array) -> None:

        self.transcript_labels = list(transcript_labels)
        self.morphology_labels = list(morphology_labels)

        assert len(self.transcript_labels) == len(self.morphology_labels)

    def __getitem__(self, index: int):
        return (
            torch.tensor(self.transcript_labels[index]).float(),
            torch.tensor(self.morphology_labels[index]).float(),)

    def __len__(self):
        return len(self.transcript_labels)


class MUSEDataModule(pl.LightningDataModule):
    def __init__(self,
                 transcript_features: np.array,
                 morphology_features: np.array,
                 transcript_labels: np.array,
                 morphology_labels: np.array,
                 batch_size: int = 512):

        super().__init__()
        self.save_hyperparameters()
        self.batch_size = batch_size

    def update_labels(self, transcript_labels, morphology_labels):
        """Re define labels dataset with the newly computed labels

        Args:
            x_labels (_type_): _description_
            y_labels (_type_): _description_
        """

        # Create new iterator for the updated labels
        self.labels_dataset = MUSELabelsDataset(
            transcript_labels, morphology_labels)

    def setup(self, stage: Optional[str] = None):
        self.features_dataset = MUSEFeaturesDataset(
            self.hparams.transcript_features, self.hparams.morphology_features)
        self.labels_dataset = MUSELabelsDataset(
            self.hparams.transcript_labels, self.hparams.morphology_labels)

    def train_dataloader(self):
        # only load features dataloader when
        features_loader = DataLoader(
            self.features_dataset, batch_size=self.batch_size, num_workers=6, drop_last=False, shuffle=False)

        labels_loader = DataLoader(
            self.labels_dataset, batch_size=self.batch_size, num_workers=6, drop_last=False, shuffle=False)

        loaders = {"features": features_loader, "labels": labels_loader}
        return loaders

    def predict_dataloader(self):
        # only load features dataloader when
        features_loader = DataLoader(
            self.features_dataset, batch_size=self.batch_size, num_workers=6)

        return features_loader
