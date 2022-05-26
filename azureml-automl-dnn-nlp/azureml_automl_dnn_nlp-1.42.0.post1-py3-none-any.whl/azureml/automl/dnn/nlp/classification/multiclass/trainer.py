# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
# Copyright 2020 The HuggingFace Inc. team. All rights reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# ---------------------------------------------------------
""" Finetuning the library models for multi-class classification."""

import logging
import numpy as np
import os
from transformers import (
    AutoConfig,
    AutoModelForSequenceClassification,
    AutoTokenizer,
    Trainer,
    TrainingArguments,
    default_data_collator,
)

from azureml.automl.core.shared import constants, logging_utilities as log_utils
from azureml.automl.dnn.nlp.classification.common.constants import MultiClassParameters
from azureml.automl.dnn.nlp.classification.io.read.pytorch_dataset_wrapper import PyTorchMulticlassDatasetWrapper
from azureml.automl.dnn.nlp.common._model_selector import get_model_from_language
from azureml.automl.dnn.nlp.common._utils import _convert_memory_exceptions
from azureml.automl.dnn.nlp.common.constants import OutputLiterals, SystemSettings
from azureml.automl.dnn.nlp.common.distributed_trainer import DistributedTrainer


_logger = logging.getLogger(__name__)


class TextClassificationTrainer:
    """Class to perform training on a text classification model given a dataset"""

    def __init__(self, train_label_list: np.ndarray, dataset_language: str, enable_distributed: bool = False):
        """
        Function to initialize text-classification trainer

        :param train_label_list: List of labels coming from the training data
        :param dataset_language: Language code of dataset
        :param enable_distributed: Enable distributed training on multiple gpus and machines
        """
        self.train_label_list = train_label_list
        self.num_labels = len(train_label_list)
        self.enable_distributed = enable_distributed
        self.model_name_or_path, download_dir = get_model_from_language(dataset_language, need_path=True)

        config = AutoConfig.from_pretrained(
            self.model_name_or_path,
            num_labels=self.num_labels,
        )
        self.tokenizer = AutoTokenizer.from_pretrained(
            self.model_name_or_path,
            use_fast=True,
        )
        # Load model
        self.model = AutoModelForSequenceClassification.from_pretrained(
            download_dir,
            from_tf=False,
            config=config,
        )
        self.trainer = None

        # Padding strategy
        pad_to_max_length = MultiClassParameters.PAD_TO_MAX_LENGTH
        # TODO: look at fp16 when the right time comes
        if pad_to_max_length:
            self.data_collator = default_data_collator
        else:
            self.data_collator = None

    @_convert_memory_exceptions
    def train(self, train_dataset: PyTorchMulticlassDatasetWrapper):
        """
        Function to perform training on the model given a training dataset

        :param training_set: PyTorchDataset object containing training data
        """
        with log_utils.log_activity(
                _logger,
                activity_name=constants.TelemetryConstants.TRAINING
        ):
            # max_seq_length_multiplier is the ratio of current max seq len to the default max seq len
            max_seq_length_multiplier =\
                int(train_dataset.max_seq_length / MultiClassParameters.MAX_SEQ_LENGTH_128)
            # Higher max seq len requires larger GPU memory to fit the larger model, and hence we reduce
            # train batch size by the same ratio (by which max seq len increased). Increasing the gradient accum.
            # steps by this ratio allows us to preserve the effective train batch size compared to the defaults.
            train_batch_size = int(MultiClassParameters.TRAIN_BATCH_SIZE / max_seq_length_multiplier)
            gradient_accum_steps = int(MultiClassParameters.GRADIENT_ACCUMULATION_STEPS * max_seq_length_multiplier)
            _logger.info("Train Batch Size = {}\nGradient Accumulation Steps = {}".format(train_batch_size,
                                                                                          gradient_accum_steps))
            self.training_args = TrainingArguments(
                output_dir=OutputLiterals.OUTPUT_DIR,
                per_device_train_batch_size=train_batch_size,
                per_device_eval_batch_size=MultiClassParameters.VALID_BATCH_SIZE,
                num_train_epochs=MultiClassParameters.EPOCHS,
                save_strategy=MultiClassParameters.SAVE_STRATEGY,
                gradient_accumulation_steps=gradient_accum_steps,
                logging_strategy=SystemSettings.LOGGING_STRATEGY,
                report_to=SystemSettings.REPORT_TO
            )
            if self.enable_distributed:
                self.trainer = DistributedTrainer(
                    model=self.model,
                    args=self.training_args,
                    train_dataset=train_dataset,
                    tokenizer=self.tokenizer,
                    data_collator=self.data_collator,
                )
            else:
                self.trainer = Trainer(
                    model=self.model,
                    args=self.training_args,
                    train_dataset=train_dataset,
                    tokenizer=self.tokenizer,
                    data_collator=self.data_collator,
                )

            train_result = self.trainer.train()
            metrics = train_result.metrics

            self.trainer.save_model()  # Saves the tokenizer too for easy upload
            self.trainer.save_metrics("train", metrics)
            self.trainer.save_state()
            if not os.path.exists(OutputLiterals.OUTPUT_DIR):
                os.mkdir(OutputLiterals.OUTPUT_DIR)
            np.save(OutputLiterals.OUTPUT_DIR + '/' + OutputLiterals.LABEL_LIST_FILE_NAME, self.train_label_list)

    @_convert_memory_exceptions
    def validate(self, eval_dataset: PyTorchMulticlassDatasetWrapper) -> np.ndarray:
        """
        Function to perform evaluate on the model given the trainer object and validation dataset

        :param eval_dataset: PyTorchDataset object containing validation data
        :return resulting predictions for the val dataset (from the cross entropy loss)
        """
        with log_utils.log_activity(
                _logger,
                activity_name=constants.TelemetryConstants.VALIDATION
        ):
            return self.trainer.predict(test_dataset=eval_dataset).predictions
