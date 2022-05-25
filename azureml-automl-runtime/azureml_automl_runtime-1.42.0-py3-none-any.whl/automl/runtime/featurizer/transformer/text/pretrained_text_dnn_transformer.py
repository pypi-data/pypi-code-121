# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""
BERT-esque finetuning+Transformer
"""
try:
    import horovod.torch as hvd
    import torch
    from pytorch_transformers import AdamW, WarmupLinearSchedule
    from torch.utils.data import DataLoader, RandomSampler, SequentialSampler, TensorDataset
    from torch.utils.data.distributed import DistributedSampler

    from .automl_pytorch_transformers import (
        MODEL_CLASSES,
        BertTransformerLinear,
        BertTransformerLowerDim,
        XLNetTransformerLinear,
        XLNetTransformerLowerDim,
    )
except Exception:
    pass


from azureml.training.tabular.featurization.text.pretrained_text_dnn_transformer import (
    InputExample,
    InputFeatures,
    PretrainedTextDNNTransformer,
    _truncate_seq_pair,
    convert_examples_to_features,
    create_examples_in_memory,
    featurize_dataset_in_memory,
)
