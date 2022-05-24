# -*- coding: utf-8 -*-

from __future__ import annotations

from collections.abc import Callable, Sequence
from typing import TYPE_CHECKING, Any, Dict, List, Optional, Tuple, Type

import torch
from ignite.utils import convert_tensor
from torch import nn
from torchcrf import CRF
from torchlight.masking import length_to_mask
from torchlight.preprocessing import LabelEncoder
from torchlight.rnn import LSTM
from torchlight.utils.file import plm_path
from torchlight.utils.phase import ModeKeys
from transformers import BertModel

from texi.tagger.sequence_labeling import SequeceLabelingTagger, Tagged

if TYPE_CHECKING:
    from transformers.tokenization_utils import PreTrainedTokenizer

BatchInput = Dict[str, torch.Tensor]
Batch = Tuple[BatchInput, torch.Tensor]
BatchId = List[List[int]]


class BiLstmCrf(nn.Module):
    def __init__(
        self,
        vocab_size: int,
        num_labels: int,
        embedded_size: int = 100,
        hidden_size: int = 100,
        num_layers: int = 2,
        char_embedding: Optional[nn.Embedding] = None,
        dropout: float = 0.0,
    ) -> None:
        super().__init__()
        self.vocab_size = vocab_size
        self.num_labels = num_labels
        if char_embedding is None:
            char_embedding = nn.Embedding(vocab_size, embedded_size)
        self.char_embedding = char_embedding
        self.embedding_dropout = nn.Dropout(dropout)
        self.encoder = LSTM(
            embedded_size,
            hidden_size,
            num_layers=num_layers,
            dropout=dropout,
            bidirectional=True,
        )
        self.fc = nn.Linear(2 * hidden_size, num_labels)

    def forward(self, inputs: BatchInput) -> torch.Tensor:
        x = inputs["token"]
        lengths = inputs["length"]

        embedded = self.char_embedding(x)
        embedded = self.embedding_dropout(embedded)
        hidden, _ = self.encoder(embedded, lengths)
        logits = self.fc(hidden)

        return logits


class BertForSequenceLabeling(nn.Module):
    def __init__(self, pretrained_model: str, **kwargs) -> None:
        super().__init__()
        num_labels = kwargs.get("num_labels")
        if num_labels is None:
            raise KeyError("Required key `num_labels` not give.")

        if isinstance(pretrained_model, str):
            self.bert = BertModel.from_pretrained(
                plm_path(pretrained_model), num_labels=num_labels
            )
        else:
            self.bert = pretrained_model

        self.output = nn.Linear(self.bert.config.hidden_size, num_labels)

    def forward(self, inputs: BatchInput) -> torch.Tensor:
        inputs = {
            key: value
            for key, value in inputs.items()
            if key not in {"offset_mapping", "label_mask"}
        }

        outputs = self.bert(**inputs)
        logits = self.output(outputs[0])

        return logits


class SequenceCrossEntropyLoss(nn.Module):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__()
        self.loss = nn.CrossEntropyLoss(*args, **kwargs)

    def forward(
        self, input_: torch.Tensor, target: torch.Tensor, length: torch.Tensor
    ) -> torch.Tensor:
        label_mask = length_to_mask(length, batch_first=True)
        assert input_.size()[:-1] == label_mask.size()
        assert target.size() == label_mask.size()

        label_mask = label_mask.view(-1).bool()
        input_ = input_.view(-1, input_.size()[-1])[label_mask]
        target = target.view(-1)[label_mask]

        return self.loss(input_, target)


class CRFForPreTraining(nn.Module):
    def __init__(self, num_labels: int, batch_first: bool = True) -> None:
        super().__init__()
        self.crf = CRF(num_labels, batch_first=batch_first)

    def forward(
        self,
        emissions: torch.Tensor,
        labels: torch.Tensor,
        mask: torch.Tensor,
        reduction: str = "sum",
    ) -> torch.Tensor:
        emissions = emissions[:, 1:, :]
        labels = labels[:, 1:]
        mask = mask[:, 1:].bool()

        return -self.crf(emissions, labels, mask, reduction=reduction)

    def decode(self, emissions: torch.Tensor, mask: torch.ByteTensor) -> BatchId:
        return self.crf.decode(emissions, mask)


class CRFDecoder(object):
    def __init__(self, tokenizer: Any, label_encoder: LabelEncoder, crf: CRF) -> None:
        self.tokenizer = tokenizer
        self.label_encoder = label_encoder
        self.crf = crf

    def decode_tokens(self, x: BatchInput) -> BatchId:
        tokens = self.tokenizer.batch_decode(x["token"], x["length"])
        tokens = [x[:length] for x, length in zip(tokens, x["length"])]

        return tokens

    def decode_labels(self, x: BatchInput, y: torch.Tensor) -> BatchId:
        if y.dim() > 2:
            labels = self.crf.decode(y, length_to_mask(x["length"], batch_first=True))
        else:
            labels = y.detach().cpu()
        labels = self.label_encoder.decode(labels)

        return [x[:length] for x, length in zip(labels, x["length"])]

    def decode(self, batch: Batch) -> tuple[BatchId, BatchId]:
        x, y = batch

        tokens = self.decode_tokens(x)
        labels = self.decode_labels(x, y)

        assert len(tokens) == len(labels)
        assert all(
            len(sample_tokens) == len(sample_labels)
            for sample_tokens, sample_labels in zip(tokens, labels)
        )

        return tokens, labels


class SequenceDecoderForPreTraining(object):
    def __init__(
        self, tokenizer: PreTrainedTokenizer, label_encoder: LabelEncoder
    ) -> None:
        self.tokenizer = tokenizer
        self.label_encoder = label_encoder

    def decode_tokens(
        self, x: BatchInput, token_transform: Callable[[list[str]], str]
    ) -> list[list[str]]:
        tokens = []
        for input_ids, offsets in zip(x["input_ids"], x["offset_mapping"]):
            # Decode token ids.
            sample_tokens, token_ids = [], []  # type: ignore
            # Loop over all subwords.
            for i, offset in enumerate(offsets):
                # Ignore special tokens.
                if offset.sum() == 0:
                    continue

                # Found all tokens of a word.
                if offset[0] == 0 and token_ids:
                    sample_tokens += [self.tokenizer.convert_ids_to_tokens(token_ids)]
                    token_ids = []

                # Accumulate subwords of current word.
                token_ids += [input_ids[i]]

            if token_ids:
                sample_tokens += [self.tokenizer.convert_ids_to_tokens(token_ids)]
                token_ids = []
            tokens += [[*map(token_transform, sample_tokens)]]

        return tokens

    def decode_labels(self, x: BatchInput, y: torch.Tensor) -> list[list[str]]:
        labels = []
        for label_mask, label_ids in zip(x["label_mask"], y):
            # Decode label ids.
            if label_ids.dim() > 1:  # logit
                label_ids = label_ids.argmax(dim=-1)
            label_ids = label_ids[label_mask > 0].tolist()
            labels += [label_ids]

        decoded = [self.label_encoder.decode(x) for x in labels]

        return decoded

    def decode(
        self,
        batch: Batch,
        token_transform: Callable[[list[str]], str] = lambda x: "".join(
            w.replace("##", "") for w in x
        ),
    ):
        x, y = batch

        tokens = self.decode_tokens(x, token_transform)
        labels = self.decode_labels(x, y)

        assert len(tokens) == len(labels)
        assert all(
            len(sample_tokens) == len(sample_labels)
            for sample_tokens, sample_labels in zip(tokens, labels)
        )

        return tokens, labels


class CRFDecoderForPreTraining(SequenceDecoderForPreTraining):
    def __init__(
        self, tokenizer: PreTrainedTokenizer, label_encoder: LabelEncoder, crf: CRF
    ) -> None:
        super().__init__(tokenizer, label_encoder)
        self.crf = crf

    def decode_labels(self, x: BatchInput, y: torch.Tensor) -> list[list[str]]:
        if y.dim() == 2:
            return super().decode_labels(x, y)

        labels = self.crf.decode(y[:, 1:, :], x["label_mask"][:, 1:])
        labels = self.label_encoder.decode(labels)

        return labels


class SequenceLabeler(object):
    def __init__(
        self,
        net: nn.Module,
        tokenizer: Any,
        label_encoder: LabelEncoder,
        dataset_class: Type,
        tagger: SequeceLabelingTagger,
    ) -> None:
        self.net = net
        self.tokenizer = tokenizer
        self.label_encoder = label_encoder
        self.dataset_class = dataset_class
        self.tagger = tagger

    def predict(
        self,
        tokens: Sequence[Sequence[str]],
        device: torch.device = torch.device("cpu"),
        non_blocking: bool = False,
        batch_size: int = 32,
    ) -> list[dict]:
        dummy_label = self.label_encoder.labels[0]

        examples = [
            {"tokens": sample_tokens, "labels": [dummy_label] * len(sample_tokens)}
            for sample_tokens in tokens
        ]
        dataset = self.dataset_class(
            examples,
            tokenizer=self.tokenizer,
            label_encoder=self.label_encoder,
            mode=ModeKeys.PREDICT,
        )
        data_loader = dataset.get_dataloader(sampler_kwargs={"batch_size": batch_size})

        outputs = []  # type: list[Tagged]
        self.net.eval()
        with torch.no_grad():
            for batch in data_loader:
                batch = convert_tensor(batch, device=device, non_blocking=non_blocking)
                x = batch[0]
                logit = self.net(x)
                y_pred = logit.argmax(dim=-1)
                outputs += [
                    {"tokens": tokens, "labels": labels}
                    for tokens, labels in zip(*dataset.decode_seq((x, y_pred)))
                ]
        decoded = [*map(self.tagger.decode, outputs)]

        return decoded
