# -*- coding: utf-8 -*-

from __future__ import annotations

from typing import Optional, Union

import torch
from torch import nn
from torchlight.pooling import get_pooling
from torchlight.rnn import get_rnn
from torchlight.utils.file import plm_path
from transformers import BertModel


class TextRNN(nn.Module):
    def __init__(
        self,
        num_labels: int,
        input_size: int,
        embedding: Optional[nn.Embedding] = None,
        vocab_size: Optional[int] = None,
        hidden_size: int = 256,
        num_layers: int = 2,
        bidirectional: bool = True,
        dropout: float = 0.1,
        embedding_dropout: float = 0.1,
        cell="lstm",
        **kwargs
    ) -> None:
        super().__init__()

        if embedding is None:
            if vocab_size is None:
                raise ValueError("`vocab_size` must be given when `embedding` is None")
            embedding = nn.Embedding(vocab_size, input_size)
        else:
            if vocab_size is not None:
                raise ValueError("`vocab_size` must be None when `embedding` is given")
        self.embedding = embedding
        self.embedding_dropout = nn.Dropout(embedding_dropout)

        self.encoder = get_rnn(cell)(
            input_size=input_size,
            hidden_size=hidden_size,
            num_layers=num_layers,
            bidirectional=bidirectional,
            dropout=dropout,
            **kwargs
        )
        if cell == "lstm":

            def get_last_hidden_state(state):
                state = state[0]
                return state.transpose(0, 1).flatten(1)

        else:

            def get_last_hidden_state(state):
                return state.transpose(0, 1).flatten(1)

        self.get_last_hidden_state = get_last_hidden_state
        self.dropout = nn.Dropout(dropout)

        num_hiddens = (1 + bidirectional) * num_layers * hidden_size
        num_outputs = 1 if num_labels == 2 else num_labels
        self.classifier = nn.Linear(num_hiddens, num_outputs)

    def forward(
        self, input_ids: torch.LongTensor, length: torch.LongTensor
    ) -> torch.Tensor:
        embedded = self.embedding(input_ids)
        _, state = self.encoder(embedded, length, batch_first=True)
        last_hidden_state = self.get_last_hidden_state(state)
        last_hidden_state = self.dropout(last_hidden_state)
        logit = self.classifier(last_hidden_state)

        return logit


class BertForSequenceClassification(nn.Module):
    def __init__(
        self,
        bert: Union[BertModel, str],
        dropout: float = 0.1,
        pooling: str = "cls",
        num_labels: int = 2,
    ) -> None:
        super().__init__()
        if isinstance(bert, str):
            bert = BertModel.from_pretrained(plm_path(bert), add_pooling_layer=False)
        self.bert = bert

        self.pooling = get_pooling(pooling)
        self.dropout = nn.Dropout(dropout)
        self.classifier = nn.Linear(
            bert.config.hidden_size, 1 if num_labels == 2 else num_labels
        )

        self.num_labels = num_labels

    def forward(
        self,
        input_ids: torch.LongTensor,
        attention_mask: torch.LongTensor,
        token_type_ids: torch.LongTensor,
    ) -> torch.Tensor:
        bert_output = self.bert(
            input_ids=input_ids,
            attention_mask=attention_mask,
            token_type_ids=token_type_ids,
        )

        pooled = self.pooling(bert_output, attention_mask)
        drop = self.dropout(pooled)
        logit = self.classifier(drop)

        if self.num_labels == 2:
            logit = logit.squeeze(dim=-1)

        return logit
