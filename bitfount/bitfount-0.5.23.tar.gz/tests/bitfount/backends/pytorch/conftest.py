"""PyTorch backend test config settings."""
import inspect

from _pytest.monkeypatch import MonkeyPatch
from pytest import fixture

import bitfount.config


@fixture(autouse=True)
def env_fix(monkeypatch: MonkeyPatch) -> None:
    """Fix the environment into a known state for tests."""
    # Overrides the default fixture in tests/conftest.py
    monkeypatch.setenv("BITFOUNT_ENGINE", bitfount.config._PYTORCH_ENGINE)
    monkeypatch.setattr(
        "bitfount.config.BITFOUNT_ENGINE", bitfount.config._PYTORCH_ENGINE
    )


@fixture
def pytorch_bitfount_model_correct_structure() -> str:
    """Example good PytorchBitfountModel."""
    return inspect.cleandoc(
        """
        from torchmetrics.functional import accuracy
        import torch
        from torch import nn as nn
        from torch.nn import functional as F

        from bitfount.backends.pytorch.models.bitfount_model import (
            PyTorchBitfountModel,
        )
        from bitfount.backends.pytorch.models.base_models import (
            PyTorchClassifierMixIn,
        )

        class DummyModel(PyTorchClassifierMixIn, PyTorchBitfountModel):

            def __init__(self, epochs=5, **kwargs):
                super().__init__(epochs=epochs, **kwargs)
                self.learning_rate=0.01

            def create_model(self):
                self.input_size = self.datastructure.input_size

                return nn.Sequential(
                    nn.Linear(self.input_size, 500),
                    nn.ReLU(),
                    nn.Dropout(0.1),
                    nn.Linear(500, self.n_classes),
                )

            def forward(self, x):
                x, sup = x
                x = self._model(x.float())
                return x

            def training_step(self, batch, batch_idx):
                x, y = batch
                return F.cross_entropy(self(x), y)

            def validation_step(self, batch, batch_idx):
                x, y = batch
                preds = self(x)
                loss = F.cross_entropy(preds, y)
                preds = F.softmax(preds, dim=1)
                acc = accuracy(preds, y)

                # Calling self.log will surface up scalars for you in TensorBoard
                # self.log("val_loss", loss, prog_bar=True)
                # self.log("val_acc", acc, prog_bar=True)

                return {
                    "val_loss": loss,
                    "val_acc": acc,
                }

            def test_step(self, batch, batch_idx):
                x, y = batch
                preds = self(x)
                loss = F.cross_entropy(preds, y)
                self.targs.extend(y.tolist())
                self.preds.extend(F.softmax(preds, dim=1).tolist())
                return loss

            def configure_optimizers(self):
                optimizer = torch.optim.AdamW(self.parameters(), lr=self.learning_rate)
                return optimizer
        """
    )


@fixture
def pytorch_bitfount_model_tab_image_data() -> str:
    """Pytorch Model which handles both tabular and image data."""
    return inspect.cleandoc(
        """
        from collections import defaultdict
        from torchmetrics.functional import accuracy
        import torch
        from torch import nn as nn
        from torch.nn import functional as F

        from bitfount.backends.pytorch.models.bitfount_model import (
            PyTorchBitfountModel,
        )
        from bitfount.backends.pytorch.models.base_models import (
            PyTorchClassifierMixIn,
        )

        class DummyModelTabImg(PyTorchClassifierMixIn, PyTorchBitfountModel):

            def __init__(self, epochs=50, **kwargs):
                super().__init__(epochs=epochs, **kwargs)
                self.batch_size = 32
                self.learning_rate = 0.01
                self.num_workers = 0

            def create_model(self):

                class TabImg(nn.Module):

                    def __init__(self):
                        super().__init__()
                        self.conv1 = nn.Sequential(
                            nn.Conv2d(3, 16, (3, 3)),
                            nn.ReLU(),
                            nn.BatchNorm2d(16),
                            nn.MaxPool2d((2, 2)),
                        )
                        self.conv2 = nn.Sequential(
                            nn.Conv2d(16, 32, (3, 3)),
                            nn.ReLU(),
                            nn.BatchNorm2d(32),
                            nn.MaxPool2d((2, 2)),
                        )
                        self.conv3 = nn.Sequential(
                            nn.Conv2d(32, 64, (3, 3)),
                            nn.ReLU(),
                            nn.BatchNorm2d(64),
                            nn.MaxPool2d((2, 2)),
                        )
                        self.ln1 = nn.Linear(64 * 26 * 26, 16)
                        self.relu = nn.ReLU()
                        self.batchnorm = nn.BatchNorm1d(16)
                        self.dropout = nn.Dropout2d(0.5)
                        self.ln2 = nn.Linear(16, 5)

                        self.ln4 = nn.Linear(13, 10) #tabular input size
                        self.ln5 = nn.Linear(10, 10)
                        self.ln6 = nn.Linear(10, 5)
                        self.ln7 = nn.Linear(10, 1)

                    def forward(self, img, tab):
                        img = self.conv1(img)
                        img = self.conv2(img)
                        img = self.conv3(img)
                        img = img.reshape(img.shape[0], -1)
                        img = self.ln1(img)
                        img = self.relu(img)
                        img = self.batchnorm(img)
                        img = self.dropout(img)
                        img = self.ln2(img)
                        img = self.relu(img)

                        tab = self.ln4(tab)
                        tab = self.relu(tab)
                        tab = self.ln5(tab)
                        tab = self.relu(tab)
                        tab = self.ln6(tab)
                        tab = self.relu(tab)

                        x = torch.cat((img, tab), dim=1)
                        x = self.relu(x)

                        return self.ln7(x)

                return TabImg()

            def forward(self, img, tab):
                return self._model(img, tab)

            def training_step(self, batch, batch_idx):
                x, y = batch
                tabular, image, *support = self.split_dataloader_output(x)
                criterion = torch.nn.L1Loss()

                y_pred = torch.flatten(self(image, tabular))

                y_pred = y_pred.double()

                loss = criterion(y_pred, y)

                return loss

            def validation_step(self, batch, batch_idx):
                x, y = batch
                tabular, image, *support = self.split_dataloader_output(x)
                criterion = torch.nn.L1Loss()
                y_pred = torch.flatten(self(image, tabular))
                y_pred = y_pred.double()
                acc = accuracy(y_pred, y)
                val_loss = criterion(y_pred, y)

                return {
                    "validation_loss": val_loss,
                    "validation_accuracy": acc
                }

            def test_step(self, batch, batch_idx):
                x, y = batch
                tabular, image, *support = self.split_dataloader_output(x)
                criterion = torch.nn.L1Loss()
                y_pred = torch.flatten(self(image, tabular))
                y_pred = y_pred.double()
                loss = criterion(y_pred, y)
                return loss

            def split_dataloader_output(self, data):
                tab, images, sup = data
                weights = sup[:, 0].float()
                if sup.shape[1] > 2:
                    category = sup[:, -1].long()
                else:
                    category = None
                return tab.float(), images, weights, category

            def configure_optimizers(self):
                return torch.optim.Adam(self.parameters(), lr=(self.learning_rate))
        """
    )
