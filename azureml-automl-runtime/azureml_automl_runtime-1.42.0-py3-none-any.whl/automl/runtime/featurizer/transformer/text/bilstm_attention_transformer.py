# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Bi-LSTM with Attention transformer"""
from azureml.training.tabular.featurization.text.bilstm_attention_transformer import BiLSTMAttentionTransformer

pkg_dependencies_satisfied = False
try:
    import en_core_web_sm
    import spacy
    import torch
    import torch.nn.functional as func
    from torch.nn.utils.rnn import pack_padded_sequence, pad_packed_sequence, pad_sequence

    pkg_dependencies_satisfied = True

    from azureml.training.tabular.featurization.text.bilstm_attention_transformer import (
        BaseModel,
        Batch,
        CharEmbed,
        EarlyStopping,
        Eval,
        EvalResult,
        TextAttentionModel,
        TextDataset,
        TextUtils,
        Utils,
        WordEmbed,
        en_tokenize,
    )
except ImportError:
    pass
