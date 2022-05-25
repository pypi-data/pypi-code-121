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
"""pytorch-transformers BERT model code without apex dependency removed for stability."""
try:
    import torch
    from pytorch_transformers.modeling_utils import (
        CONFIG_NAME,
        WEIGHTS_NAME,
        PretrainedConfig,
        PreTrainedModel,
        add_start_docstrings,
        prune_linear_layer,
    )
    from torch import nn
    from torch.nn import CrossEntropyLoss, MSELoss

    from azureml.training.tabular.featurization.text._modeling_bert_no_apex import (
        ACT2FN,
        BERT_INPUTS_DOCSTRING,
        BERT_PRETRAINED_CONFIG_ARCHIVE_MAP,
        BERT_PRETRAINED_MODEL_ARCHIVE_MAP,
        BERT_START_DOCSTRING,
        BertAttention,
        BertConfig,
        BertEmbeddings,
        BertEncoder,
        BertForMaskedLM,
        BertForMultipleChoice,
        BertForNextSentencePrediction,
        BertForPreTraining,
        BertForQuestionAnswering,
        BertForSequenceClassification,
        BertForTokenClassification,
        BertIntermediate,
        BertLayer,
        BertLayerNorm,
        BertLMPredictionHead,
        BertModel,
        BertOnlyMLMHead,
        BertOnlyNSPHead,
        BertOutput,
        BertPooler,
        BertPredictionHeadTransform,
        BertPreTrainedModel,
        BertPreTrainingHeads,
        BertSelfAttention,
        BertSelfOutput,
        gelu,
        load_tf_weights_in_bert,
        swish,
    )

    torch_present = True
except ImportError:
    torch_present = False
