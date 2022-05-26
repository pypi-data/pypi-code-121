# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""Class for training Pytorch Models"""

import logging
import numpy as np
import time
import torch
from torch.utils.data import DataLoader, RandomSampler
from typing import Dict, List, Tuple

from azureml.automl.core.shared import constants, logging_utilities as log_utils
from azureml.automl.dnn.nlp.classification.common.constants import MultiLabelParameters
from azureml.automl.dnn.nlp.classification.multilabel.utils import compute_threshold_metrics
from azureml.automl.dnn.nlp.common._utils import _convert_memory_exceptions
from azureml.automl.dnn.nlp.common.constants import Warnings, Split
from azureml.automl.runtime.shared.score import scoring
from azureml.automl.runtime.shared.score.constants import CLASSIFICATION_SCALAR_SET

_logger = logging.getLogger(__name__)


class PytorchTrainer:
    """Class to perform training on a model given a dataset"""

    def __init__(self,
                 model_class,
                 dataset_language,
                 num_label_cols,
                 is_gpu=True):
        """
        Function to initialize pytorch trainer

        :param model_class: Class to use for model initialization
        :param dataset_language: language code of dataset
        :param num_label_cols: Number of unique classes in label column
        :param is_gpu: Setting to allow for gpu training
        """
        self.device = self._get_device()
        self.model = model_class(dataset_language, num_label_cols)
        self.model.to(self.device)
        self.loss_fn = torch.nn.BCEWithLogitsLoss
        _logger.info("Learning_rate: {}".format(self._get_learning_rate()))
        self.optimizer = torch.optim.Adam(params=self.model.parameters(), lr=self._get_learning_rate())
        self.sampler = RandomSampler

    def _get_learning_rate(self):
        return MultiLabelParameters.LEARNING_RATE

    def _data_sampler(self, dataset, mode=Split.train):
        return RandomSampler(dataset)

    def _get_device(self, is_gpu=True):
        """
        Device can differ based on trainer. This function is used to get device based on what the trainer needs
        """
        device = 'cuda' if (torch.cuda.is_available() and is_gpu) else 'cpu'
        if is_gpu and device == "cpu":
            _logger.warning(Warnings.CPU_DEVICE_WARNING)
        return device

    @_convert_memory_exceptions
    def train(self, training_set):
        """
        Function to perform training on the model given a training dataset

        :param training_set: pytorch dataset object containing information of training data
        """
        with log_utils.log_activity(
            _logger,
            activity_name=constants.TelemetryConstants.TRAINING
        ):
            train_sampler = self._data_sampler(training_set, mode=Split.train)
            training_loader = DataLoader(training_set,
                                         sampler=train_sampler,
                                         batch_size=MultiLabelParameters.TRAIN_BATCH_SIZE)
            for epoch in range(MultiLabelParameters.EPOCHS):
                start_time_epoch = time.time()

                self.model.train()
                optimizer = self.optimizer
                for step_idx, data in enumerate(training_loader, 0):
                    ids = data['ids'].to(self.device, dtype=torch.long)
                    mask = data['mask'].to(self.device, dtype=torch.long)
                    token_type_ids = data['token_type_ids'].to(self.device, dtype=torch.long)
                    targets = data['targets'].to(self.device, dtype=torch.float)

                    outputs = self.model(ids, mask, token_type_ids)

                    optimizer.zero_grad()
                    loss = self.loss_fn()(outputs, targets)
                    if step_idx % MultiLabelParameters.OUTPUT_EPOCHS_COUNT == 0:
                        _logger.info('Epoch: {}, Step: {}, Loss:  {}'.format(epoch, step_idx, loss.item()))

                    loss.backward()
                    optimizer.step()

                _logger.info("Time for epoch {}: {}".format(epoch, time.time() - start_time_epoch))
            return self.model

    @_convert_memory_exceptions
    def validate(self, valid_set):
        """
        Function to perform validation on the model given a validation dataset

        :param valid_set: pytorch dataset object to run validation on
        """
        with log_utils.log_activity(
            _logger,
            activity_name=constants.TelemetryConstants.VALIDATION
        ):
            valid_sampler = self._data_sampler(valid_set, mode=Split.test)
            valid_loader = DataLoader(valid_set,
                                      sampler=valid_sampler,
                                      batch_size=MultiLabelParameters.VALID_BATCH_SIZE)
            self.model.eval()
            fin_targets = []
            fin_outputs = []
            with torch.no_grad():
                for _, data in enumerate(valid_loader, 0):
                    ids = data['ids'].to(self.device, dtype=torch.long)
                    mask = data['mask'].to(self.device, dtype=torch.long)
                    token_type_ids = data['token_type_ids'].to(self.device, dtype=torch.long)
                    targets = data['targets'].to(self.device, dtype=torch.long)
                    outputs = self.model(ids, mask, token_type_ids)
                    fin_targets.extend(targets.cpu().detach().numpy().tolist())
                    fin_outputs.extend(torch.sigmoid(outputs).cpu().detach().numpy().tolist())
            return fin_outputs, fin_targets

    def compute_metrics(self, valid_set, y_transformer) -> Tuple[Dict[str, float], Dict[str, List]]:
        """
        Function to compute metrics given a validation set. Currently computes accuracy, f1_score micro and macro

        :param valid_set: Pytorch dataset used for validation to get metrics from
        :param y_transformer: MultiLabelBinarizer to encode/decode labels/vectors
        :return Dictionary of multi-label metrics, Dict of multi-label metrics for range of thresholds
        """
        outputs, targets = self.validate(valid_set)

        metrics_dict_with_thresholds = compute_threshold_metrics(outputs, targets)

        L = len(y_transformer.classes_)
        metrics_dict = scoring.score_classification(
            y_test=np.array(targets),
            y_pred_probs=np.array(outputs),
            metrics=CLASSIFICATION_SCALAR_SET,
            class_labels=np.arange(L),
            train_labels=np.arange(L),
            y_transformer=y_transformer,
            multilabel=True
        )

        return metrics_dict, metrics_dict_with_thresholds
