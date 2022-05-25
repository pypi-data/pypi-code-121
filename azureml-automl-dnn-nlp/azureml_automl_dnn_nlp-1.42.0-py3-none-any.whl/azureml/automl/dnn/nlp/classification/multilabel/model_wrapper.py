# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""Model Wrapper class to encapsulate automl model functionality"""

from sklearn.preprocessing import MultiLabelBinarizer
from torch.utils.data import DataLoader, Dataset
from transformers.models.bert.tokenization_bert import BertTokenizer

import torch
import pandas as pd

from azureml.automl.dnn.nlp.classification.common.constants import MultiLabelParameters
from azureml.automl.dnn.nlp.classification.io.read.pytorch_dataset_wrapper import PyTorchDatasetWrapper


class ModelWrapper:
    """Class to wrap AutoML NLP models in the AutoMLTransformer interface"""

    def __init__(self,
                 model: torch.nn.Module,
                 tokenizer: BertTokenizer,
                 dataset_language: str,
                 y_transformer: MultiLabelBinarizer,
                 label_column_name: str):
        """
        Transform the input data into outputs tensors from model

        :param model: Trained model
        :param tokenizer: Tokenizer used to tokenize text data during training
        :param dataset_language: Language code of dataset
        :param y_transformer: Fitted MultiLabelBinarizer
        :param label_column_name: Name/title of the label column used during training
        """
        super().__init__()
        self.model = model.to(torch.device("cpu"))
        self.tokenizer = tokenizer
        self.dataset_language = dataset_language
        self.y_transformer = y_transformer
        self.label_column_name = label_column_name

    def _transform(self,
                   dataset: Dataset,
                   batch_size: int):
        """
        Helper function for transforming the input data into outputs tensors using model

        :param dataset: Pytorch dataset object which returns items in the format {'ids', 'mask', 'token_type_ids'}
        :param batch_size: The batch size with which we should process the data
        :return: List of arrays representing outputs
        """
        fin_outputs = []
        device = 'cuda' if torch.cuda.is_available() else 'cpu'
        self.model.to(device)
        data = DataLoader(dataset, batch_size=batch_size)

        for _, sample in enumerate(data, 0):
            input_ids = sample['ids'].to(device, dtype=torch.long)
            attention_mask = sample['mask'].to(device, dtype=torch.long)
            token_type_ids = sample['token_type_ids'].to(device, dtype=torch.long)

            output = self.model(input_ids, attention_mask, token_type_ids)
            fin_outputs.extend(torch.sigmoid(output).cpu().detach().numpy())

        return fin_outputs

    def predict(self,
                X: pd.DataFrame,
                threshold: int = 0.5,
                batch_size: int = MultiLabelParameters.INFERENCE_BATCH_SIZE):
        """
        Predict output labels for text datasets

        :param context: The PythonModelContext, automatically loaded and used by MLFlow
        :param X: pandas dataframe in the same format as training data, without label columns
        :param threshold: model output threshold at which labels are selected
        :return: list of output labels equal to the size of X
        """
        dataset = PyTorchDatasetWrapper(X, self.dataset_language)
        fin_outputs = self._transform(dataset, batch_size=batch_size)
        fin_labels = []
        for output in fin_outputs:
            selected = output > threshold
            selected = selected.reshape(1, -1)
            labels = self.y_transformer.inverse_transform(selected)
            fin_labels.extend(labels)
        return fin_labels
