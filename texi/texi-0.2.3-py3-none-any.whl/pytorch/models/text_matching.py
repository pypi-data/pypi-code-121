# -*- coding: utf-8 -*-

from __future__ import annotations

from typing import Optional, Union, cast

import torch
from torch import nn
from torch.nn.utils.rnn import pack_padded_sequence, pad_packed_sequence
from torchlight.attention import BidirectionalAttention
from torchlight.losses import ManhattanSimilarity
from torchlight.masking import length_to_mask
from torchlight.pooling import get_pooling
from torchlight.utils.file import plm_path
from transformers import BertModel


class SiameseLSTM(nn.Module):
    def __init__(
        self,
        embedded_size: int,
        hidden_size: int,
        num_layers: int = 2,
        batch_first: bool = True,
        dropout: float = 0.5,
        embedding: Optional[nn.Embedding] = None,
        vocab_size: Optional[int] = None,
        padding_idx: Optional[int] = 0,
    ) -> None:
        super().__init__()
        self.embedded_size = embedded_size
        self.hidden_size = hidden_size
        self.num_layers = num_layers
        self.batch_first = batch_first
        self.dropout = dropout
        self.rnn_dropout = dropout if num_layers > 1 else 0
        if embedding is None:
            if vocab_size is None:
                raise ValueError("`vocab_size` must be given if `embedding` is None")

            embedding = nn.Embedding(
                cast(int, vocab_size), embedded_size, padding_idx=padding_idx
            )
        self.embedding = embedding
        self.vocab_size = vocab_size

        self.input_encoder = nn.LSTM(
            self.embedded_size,
            self.hidden_size,
            num_layers=self.num_layers,
            batch_first=self.batch_first,
            bidirectional=True,
            dropout=self.rnn_dropout,
        )
        self.manhattan_similarity = ManhattanSimilarity()

    def _lstm_encode(self, lstm: nn.LSTM, inputs: torch.Tensor, lengths: torch.Tensor):
        packed = pack_padded_sequence(
            inputs, lengths, enforce_sorted=False, batch_first=self.batch_first
        )
        _, (hidden, _) = lstm(packed)
        hidden = hidden.view(self.num_layers, 2, -1, self.hidden_size)
        last_hidden = hidden[-1].transpose(0, 1)
        last_hidden = last_hidden.reshape(last_hidden.size()[0], -1)

        return last_hidden

    def _input_encoding(
        self,
        sentence1: torch.Tensor,
        sentence2: torch.Tensor,
        length1: torch.Tensor,
        length2: torch.Tensor,
    ):
        return (
            self._lstm_encode(self.input_encoder, sentence1, length1),
            self._lstm_encode(self.input_encoder, sentence2, length2),
        )

    def forward(self, inputs: dict[str, torch.Tensor]):
        sentence1, sentence2 = inputs["sentence1"], inputs["sentence2"]
        length1, length2 = inputs["length1"], inputs["length2"]

        # Token representation.
        sentence1_embedded = self.embedding(sentence1)
        sentence2_embedded = self.embedding(sentence2)

        # Input encoding.
        sentence1_encoded, sentence2_encoded = self._input_encoding(
            sentence1_embedded, sentence2_embedded, length1, length2
        )

        # Scoring.
        logits = self.manhattan_similarity(sentence1_encoded, sentence2_encoded)

        return logits


class ESIM(nn.Module):
    def __init__(
        self,
        embedded_size: int,
        hidden_size: int,
        num_layers: int = 2,
        batch_first: bool = True,
        bidirectional: bool = True,
        dropout: float = 0.5,
        embedding: Optional[nn.Embedding] = None,
        vocab_size: Optional[int] = None,
        padding_idx: Optional[int] = 0,
    ) -> None:
        super().__init__()
        self.embedded_size = embedded_size
        self.hidden_size = hidden_size
        self.num_layers = num_layers
        self.batch_first = batch_first
        self.bidirectional = bidirectional
        self.dropout = dropout
        self.rnn_dropout = dropout if num_layers > 1 else 0
        if embedding is None:
            if vocab_size is None:
                raise ValueError("`vocab_size` must be given if `embedding` is None")

            embedding = nn.Embedding(
                cast(int, vocab_size), embedded_size, padding_idx=padding_idx
            )
        self.embedding = embedding
        self.vocab_size = vocab_size

        self.input_encoder = nn.LSTM(
            self.embedded_size,
            self.hidden_size,
            num_layers=self.num_layers,
            batch_first=self.batch_first,
            bidirectional=self.bidirectional,
            dropout=self.rnn_dropout,
        )
        self.bidirectional_attention = BidirectionalAttention()
        self.composition_projection = nn.Sequential(
            nn.Linear(8 * self.hidden_size, self.hidden_size), nn.ReLU()
        )
        self.composition_encoder = nn.LSTM(
            self.hidden_size,
            self.hidden_size,
            num_layers=self.num_layers,
            batch_first=self.batch_first,
            bidirectional=self.bidirectional,
            dropout=self.rnn_dropout,
        )
        self.before_output = nn.Sequential(
            nn.Linear(8 * self.hidden_size, self.hidden_size),
            nn.Tanh(),
            nn.Dropout(dropout),
        )
        self.output = nn.Linear(self.hidden_size, 1)

    def _lstm_encode(self, lstm: nn.LSTM, inputs: torch.Tensor, lengths: torch.Tensor):
        packed = pack_padded_sequence(
            inputs, lengths, enforce_sorted=False, batch_first=self.batch_first
        )
        encoded, _ = lstm(packed)
        encoded, _ = pad_packed_sequence(encoded, batch_first=self.batch_first)

        return encoded

    def _input_encoding(
        self,
        sentence1: torch.Tensor,
        sentence2: torch.Tensor,
        length1: torch.Tensor,
        length2: torch.Tensor,
    ):
        return (
            self._lstm_encode(self.input_encoder, sentence1, length1),
            self._lstm_encode(self.input_encoder, sentence2, length2),
        )

    def _local_inference(
        self,
        sentence1_encoded: torch.Tensor,
        sentence2_encoded: torch.Tensor,
        length1: torch.Tensor,
        length2: torch.Tensor,
    ):
        sentence1_semantics, sentence2_semantics = self.bidirectional_attention(
            sentence1_encoded,
            ~length_to_mask(length1, batch_first=self.batch_first),
            sentence2_encoded,
            ~length_to_mask(length2, batch_first=self.batch_first),
        )

        sentence1_semantics = self._enhance_local_inference_features(
            sentence1_encoded, sentence1_semantics
        )
        sentence2_semantics = self._enhance_local_inference_features(
            sentence2_encoded, sentence2_semantics
        )

        return sentence1_semantics, sentence2_semantics

    def _enhance_local_inference_features(
        self, encodded: torch.Tensor, local_relevance: torch.Tensor
    ):
        return torch.cat(
            [
                encodded,
                local_relevance,
                encodded - local_relevance,
                encodded * local_relevance,
            ],
            dim=-1,
        )

    def _inference_composition(
        self,
        sentence1_information: torch.Tensor,
        sentence2_information: torch.Tensor,
        length1: torch.Tensor,
        length2: torch.Tensor,
    ):

        return (
            self._lstm_encode(
                self.composition_encoder,
                self.composition_projection(sentence1_information),
                length1,
            ),
            self._lstm_encode(
                self.composition_encoder,
                self.composition_projection(sentence2_information),
                length2,
            ),
        )

    def _pooling(
        self,
        sentence1_composited: torch.Tensor,
        sentence2_composited: torch.Tensor,
        length1: torch.Tensor,
        length2: torch.Tensor,
    ):
        def _avg_pooling(tensor, mask):
            return torch.sum(tensor * mask, dim=int(self.batch_first))

        def _max_pooling(tensor, mask):
            return tensor.masked_fill(~mask, float("-inf")).max(
                dim=int(self.batch_first)
            )[0]

        sentence1_mask = length_to_mask(
            length1, batch_first=self.batch_first
        ).unsqueeze(dim=-1)
        sentence2_mask = length_to_mask(
            length2, batch_first=self.batch_first
        ).unsqueeze(dim=-1)

        return torch.cat(
            [
                _avg_pooling(sentence1_composited, sentence1_mask),
                _max_pooling(sentence1_composited, sentence1_mask),
                _avg_pooling(sentence2_composited, sentence2_mask),
                _max_pooling(sentence2_composited, sentence2_mask),
            ],
            dim=-1,
        )

    def forward(self, inputs: dict[str, torch.Tensor]):
        sentence1, sentence2 = inputs["sentence1"], inputs["sentence2"]
        length1, length2 = inputs["length1"], inputs["length2"]

        # Token representation.
        sentence1_embedded = self.embedding(sentence1)
        sentence2_embedded = self.embedding(sentence2)

        # Input encoding.
        sentence1_encoded, sentence2_encoded = self._input_encoding(
            sentence1_embedded, sentence2_embedded, length1, length2
        )

        # Local inference.
        sentence1_information, sentence2_information = self._local_inference(
            sentence1_encoded, sentence2_encoded, length1, length2
        )

        # Inference composition.
        sentence1_composited, sentence2_composited = self._inference_composition(
            sentence1_information, sentence2_information, length1, length2
        )

        # Pooling.
        hidden = self._pooling(
            sentence1_composited, sentence2_composited, length1, length2
        )

        # Projection.
        before_output = self.before_output(hidden)
        logits = self.output(before_output)

        return logits


class BertSimilarity(nn.Module):
    def __init__(
        self,
        pretrained_model: str,
        pooling: str = "cls",
        num_labels: int = 2,
        dropout: float = 0.0,
    ) -> None:
        super().__init__()
        if isinstance(pretrained_model, str):
            self.bert = BertModel.from_pretrained(
                plm_path(pretrained_model),
                num_labels=2,
                output_hidden_states=True,
            )
        else:
            self.bert = pretrained_model
        self.pooling = get_pooling(pooling)
        self.num_labels = num_labels
        self.dropout = nn.Dropout(dropout)
        self.output = nn.Linear(
            self.bert.config.hidden_size, 1 if num_labels == 2 else num_labels
        )

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
        hidden = self.dropout(pooled)
        logit = self.output(hidden)

        if self.num_labels == 2:
            logit = logit.squeeze(dim=-1)

        return logit


class SBertBiEncoder(nn.Module):
    def __init__(self, bert: Union[BertModel, str], pooling: str = "mean") -> None:
        super().__init__()
        if isinstance(bert, str):
            bert = BertModel.from_pretrained(plm_path(bert), add_pooling_layer=False)
        self.bert = bert

        self.pooling = get_pooling(pooling)

    def forward(
        self,
        input_ids: torch.LongTensor,
        attention_mask: torch.LongTensor,
        token_type_ids: torch.LongTensor,
    ) -> torch.Tensor:
        n, batch_size, max_length = input_ids.size()

        def _flatten(t):
            return t.view(-1, max_length)

        # input_ids, attention_mask, token_type_ids: [N, B, L] -> [NB, L]
        input_ids = _flatten(input_ids)
        attention_mask = _flatten(attention_mask)
        token_type_ids = _flatten(token_type_ids)

        bert_output = self.bert(
            input_ids=input_ids,
            attention_mask=attention_mask,
            token_type_ids=token_type_ids,
        )
        pooled = self.pooling(bert_output, attention_mask)
        pooled = pooled.view(n, batch_size, -1)

        return pooled


class SBertForClassification(nn.Module):
    def __init__(
        self,
        bert: Union[BertModel, str],
        pooling: str = "mean",
        num_labels: int = 2,
        dropout: float = 0.1,
    ) -> None:
        super().__init__()
        self.sbert_encoder = SBertBiEncoder(bert, pooling=pooling)
        self.dropout = nn.Dropout(dropout)
        self.classifier = nn.Linear(
            3 * self.sbert_encoder.bert.config.hidden_size,
            1 if num_labels == 2 else num_labels,
        )
        self.num_labels = num_labels

    def forward(
        self,
        input_ids: torch.LongTensor,
        attention_mask: torch.LongTensor,
        token_type_ids: torch.LongTensor,
    ) -> torch.Tensor:
        def _check_size(t):
            if t.ndim != 3 or t.size()[0] != 2:
                raise ValueError(
                    "`input_ids`, `attention_mask`, `token_type_ids` should all"
                    " have size: [2, batch_size, max_length]"
                )

        _check_size(input_ids)
        _check_size(attention_mask)
        _check_size(token_type_ids)

        hidden = self.sbert_encoder(input_ids, attention_mask, token_type_ids)

        u, v = hidden
        feature = torch.cat([u, v, torch.abs(u - v)], dim=-1)

        logit = self.classifier(feature)
        if self.num_labels == 2:
            logit = logit.squeeze(dim=-1)

        return logit


class SBertForRegression(nn.Module):
    def __init__(
        self,
        bert: Union[BertModel, str],
        pooling: str = "mean",
    ) -> None:
        super().__init__()
        self.sbert_encoder = SBertBiEncoder(bert, pooling=pooling)
        self.cosine_similarity = nn.CosineSimilarity()

    def forward(
        self,
        input_ids: torch.LongTensor,
        attention_mask: torch.LongTensor,
        token_type_ids: torch.LongTensor,
    ) -> torch.Tensor:
        def _check_size(t):
            if t.ndim != 3 or t.size()[0] != 2:
                raise ValueError(
                    "Input tensor should have size: [2, batch_size, max_length]"
                )

        _check_size(input_ids)
        _check_size(attention_mask)
        _check_size(token_type_ids)

        hidden = self.sbert_encoder(input_ids, attention_mask, token_type_ids)

        u, v = hidden
        score = self.cosine_similarity(u, v)

        return score
