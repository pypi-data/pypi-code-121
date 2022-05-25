# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""Model Wrapper class to encapsulate automl model functionality"""

from scipy.special import softmax
from transformers import AutoTokenizer, default_data_collator, Trainer

import pandas as pd
import numpy as np
import torch

from azureml.automl.dnn.nlp.classification.io.read.pytorch_dataset_wrapper import PyTorchMulticlassDatasetWrapper


class ModelWrapper:
    """Class to wrap AutoML NLP models in the AutoMLTransformer interface"""

    def __init__(self,
                 model: torch.nn.Module,
                 train_label_list: np.ndarray,
                 tokenizer: AutoTokenizer,
                 max_seq_length: int):
        """
        Transform the input data into outputs tensors from model

        :param trainer: Trained HuggingFace trainer
        :param dataset_language: language for tokenization
        """
        super().__init__()
        self.model = model.to("cpu")
        self.tokenizer = tokenizer
        self.classes_ = train_label_list
        self.max_seq_length = max_seq_length

    def predict(self, X: pd.DataFrame):
        """
        Predict output labels for text datasets

        :param X: pandas dataframe in the same format as training data, without label columns
        :return: list of output labels equal to the size of X
        """
        pred_probas = self.predict_proba(X)
        preds = np.argmax(pred_probas, axis=1)
        predicted_labels = [self.classes_[cls_idx] for cls_idx in preds]
        return predicted_labels

    def predict_proba(self,
                      X: pd.DataFrame):
        """
        Output prediction probabilities for input text dataset.

        :param X: Pandas DataFrame in the same format as training data, without label columns.
        :return: Class-wise prediction probabilities.
        """
        dataset = PyTorchMulticlassDatasetWrapper(X,
                                                  self.classes_,
                                                  self.tokenizer,
                                                  self.max_seq_length,
                                                  label_column_name=None)
        trainer = Trainer(model=self.model, data_collator=default_data_collator)
        predictions = trainer.predict(test_dataset=dataset).predictions
        return softmax(predictions, axis=1)
