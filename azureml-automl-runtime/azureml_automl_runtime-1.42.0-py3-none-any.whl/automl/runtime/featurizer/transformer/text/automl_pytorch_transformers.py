# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
# Copyright 2018 The Google AI Language Team Authors and The HuggingFace Inc. team.
# Copyright (c) 2018, NVIDIA CORPORATION.  All rights reserved.
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

torch_present = False
try:
    import torch
    from pytorch_transformers import (
        BertTokenizer,
        XLNetConfig,
        XLNetForSequenceClassification,
        XLNetModel,
        XLNetTokenizer,
    )
    from pytorch_transformers.modeling_xlnet import SequenceSummary, XLNetPreTrainedModel
    from pytorch_transformers.modeling_xlnet import gelu as xlnet_gelu
    from torch import nn
    from torch.nn import CrossEntropyLoss, MSELoss
    from torch.utils.data import DataLoader, RandomSampler, SequentialSampler, TensorDataset

    from .modeling_bert_no_apex import BertConfig, BertForSequenceClassification, BertModel, BertPreTrainedModel
    from .modeling_bert_no_apex import gelu as bert_gelu

    MODEL_CLASSES = {
        "bert": (BertConfig, BertForSequenceClassification, BertTokenizer),
        "xlnet": (XLNetConfig, XLNetForSequenceClassification, XLNetTokenizer),
    }
    torch_present = True

    from azureml.training.tabular.featurization.text._pytorch_transformers import (
        BertTransformerLinear,
        BertTransformerLowerDim,
        XLNetTransformerLinear,
        XLNetTransformerLowerDim,
    )
except ImportError:
    torch_present = False
