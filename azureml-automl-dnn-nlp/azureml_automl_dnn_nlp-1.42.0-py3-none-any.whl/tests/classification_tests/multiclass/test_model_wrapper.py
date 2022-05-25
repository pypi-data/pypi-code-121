from unittest.mock import patch

import numpy as np
import pandas as pd
import pytest
import unittest

from azureml.automl.dnn.nlp.classification.common.constants import MultiClassParameters
from azureml.automl.dnn.nlp.classification.multiclass.model_wrapper import ModelWrapper

try:
    import torch
    has_torch = True
except ImportError:
    has_torch = False


class MockTextDataset(torch.utils.data.Dataset):
    def __init__(self, size, num_labels):
        # Inputs created using BertTokenizer('this is a sentence')
        self.inputs = {'input_ids': [101, 2023, 2003, 1037, 6251, 102],
                       'token_type_ids': [0, 0, 0, 0, 0, 0],
                       'attention_mask': [1, 1, 1, 1, 1, 1]}
        self.dataset_size = size
        self.num_labels = num_labels

    def __len__(self):
        return self.dataset_size

    def __getitem__(self, index):
        return {
            'input_ids': torch.tensor(self.inputs['input_ids'], dtype=torch.long),
            'attention_mask': torch.tensor(self.inputs['attention_mask'], dtype=torch.long),
            'token_type_ids': torch.tensor(self.inputs['token_type_ids'], dtype=torch.long),
        }


class MockModel(torch.nn.Module):
    def __init__(self, num_labels):
        super(MockModel, self).__init__()
        self.num_labels = num_labels
        self.n_forward_called = 0

    def forward(self, input_ids, attention_mask, token_type_ids):
        self.n_forward_called = self.n_forward_called + 1
        return torch.rand(input_ids.shape[0], self.num_labels)


@unittest.skipIf(not has_torch, "torch not installed")
@pytest.mark.usefixtures('MulticlassTokenizer')
def test_predict(MulticlassTokenizer):
    data = pd.DataFrame({"text": ["some data input"]})
    model = MockModel(2)
    wrapper = ModelWrapper(model, ["label1", "label2"], MulticlassTokenizer,
                           MultiClassParameters.MAX_SEQ_LENGTH_128)
    datawrapper = "azureml.automl.dnn.nlp.classification.multiclass.model_wrapper.PyTorchMulticlassDatasetWrapper"
    with patch(datawrapper, return_value=MockTextDataset(5, 2)):
        output = wrapper.predict(data)
    assert len(output) == 5


@unittest.skipIf(not has_torch, "torch not installed")
def test_predict_proba():
    data = pd.DataFrame({"Quote": ["Debugging is like being the detective in a crime movie "
                                   "where you’re also the murderer."]})
    model = MockModel(2)
    wrapper = ModelWrapper(model, ["Funny", "Not Funny"], "eng", 128)
    torch.random.manual_seed(712)  # Get consistent results from our MockModel object.
    with patch("azureml.automl.dnn.nlp.classification.multiclass.model_wrapper.PyTorchMulticlassDatasetWrapper",
               return_value=MockTextDataset(5, 2)):
        output = wrapper.predict_proba(data)
    # Explicit check here good for guaranteeing outputs are valid probabilities.
    expected_output = np.array([[0.35975167, 0.6402482],
                                [0.44758153, 0.5524185],
                                [0.3688697, 0.6311303],
                                [0.6915948, 0.30840525],
                                [0.5844379, 0.41556212]])
    assert model.n_forward_called == 1
    np.testing.assert_allclose(output, expected_output,
                               rtol=1e-3, atol=1e-5)


@unittest.skipIf(not has_torch, "torch not installed")
@pytest.mark.usefixtures('MulticlassTokenizer')
def test_predict_proba_batched(MulticlassTokenizer):
    text_dataset = MockTextDataset(16, 2)
    model = MockModel(2)
    wrapper = ModelWrapper(model, ["label1", "label2"], MulticlassTokenizer,
                           MultiClassParameters.MAX_SEQ_LENGTH_128)
    with patch('azureml.automl.dnn.nlp.classification.multiclass.model_wrapper.PyTorchMulticlassDatasetWrapper',
               return_value=text_dataset):
        output = wrapper.predict_proba(text_dataset)

    assert model.n_forward_called == 2, "inference was not batched correctly"
    assert len(output) == 16
