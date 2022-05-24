# -*- coding: utf-8 -*-

from __future__ import annotations

from collections.abc import Callable

import torch
from carton.collections import collate
from torchlight.dataset import Collator
from torchlight.preprocessing import LabelEncoder
from torchlight.utils.phase import ModeKeys
from torchlight.utils.tensor import pad_stack_1d


class TextClassificationCollator(Collator):
    def __init__(
        self,
        tokenizer: Callable,
        label_encoder: LabelEncoder,
        mode: ModeKeys = ModeKeys.TRAIN,
    ) -> None:
        super().__init__(mode=mode)
        self.tokenizer = tokenizer
        self.label_encoder = label_encoder

    def encode(self, example):
        return {
            "text": self.tokenizer(example["text"]),
            "label": self.label_encoder.encode_label(example["label"]),
        }

    def collate_train(self, batch):
        batch = self.encode_batch(batch)

        batch = collate(batch)
        text, length = pad_stack_1d(batch["text"], return_lengths=True)
        label = torch.stack(batch["label"])

        x = {
            "text": text,
            "length": length,
        }
        y = label

        return x, y


class TextMatchingCollator(Collator):
    def __init__(
        self,
        tokenizer: Callable,
        label_encoder: LabelEncoder,
        mode: ModeKeys = ModeKeys.TRAIN,
    ) -> None:
        super().__init__(mode=mode)
        self.tokenizer = tokenizer
        self.label_encoder = label_encoder

    def encode(self, example):
        return {
            "sentence1": self.tokenizer(example["sentence1"]),
            "sentence2": self.tokenizer(example["sentence2"]),
            "label": self.label_encoder.encode(example["label"]),
        }

    def collate_train(self, batch):
        batch = self.encode_batch(batch)

        batch = collate(batch)
        sentence1, length1 = pad_stack_1d(batch["sentence1"], return_lengths=True)
        sentence2, length2 = pad_stack_1d(batch["sentence2"], return_lengths=True)

        x = {
            "sentence1": sentence1,
            "sentence2": sentence2,
            "length1": length1,
            "length2": length2,
        }
        y = torch.tensor(batch["label"], dtype=torch.int64)

        return x, y


class QuestionAnsweringCollator(Collator):
    def __init__(self, tokenizer: Callable, mode: ModeKeys = ModeKeys.TRAIN) -> None:
        super().__init__(mode=mode)
        self.tokenizer = tokenizer

    def encode(self, example):
        def _encode_answers(context, answers):
            encoded = {
                "start": torch.zeros(len(context)),
                "end": torch.zeros(len(context)),
            }
            indices = torch.arange(len(answers), dtype=torch.float32) + 1
            encoded["start"][[x["start"] for x in answers]] = indices
            encoded["end"][[x["end"] - 1 for x in answers]] = indices

            return encoded

        return {
            "context": self.tokenizer(example["context"]),
            "question": self.tokenizer(example["question"]),
            "answers": _encode_answers(example["context"], example["answers"]),
        }

    def collate_train(self, batch):
        batch = self.encode(batch)

        batch = collate(batch)
        contexts, context_lengths = pad_stack_1d(batch["context"], return_lengths=True)
        questions, question_lengths = pad_stack_1d(
            batch["question"], return_lengths=True
        )

        answers = collate(batch["answers"])
        starts = pad_stack_1d(answers["start"])
        ends = pad_stack_1d(answers["end"])

        x = {
            "question": questions,
            "query_length": question_lengths,
            "context": contexts,
            "context_length": context_lengths,
        }
        y = torch.stack([starts, ends]).type(torch.int64)

        return x, y
