# -*- coding: utf-8 -*-

from __future__ import annotations

import abc
import itertools
from collections.abc import Mapping, Sequence
from typing import Any, Optional

import torch
from carton.collections import collate
from torchlight.dataset import Collator
from torchlight.preprocessing import LabelEncoder
from torchlight.utils.phase import ModeKeys
from transformers.tokenization_utils import PreTrainedTokenizer


class PreTrainedCollator(Collator, metaclass=abc.ABCMeta):
    def __init__(
        self,
        tokenizer: PreTrainedTokenizer,
        label_encoder: Optional[LabelEncoder] = None,
        mode: ModeKeys = ModeKeys.TRAIN,
    ) -> None:
        super().__init__(mode=mode)
        self.tokenizer = tokenizer
        if label_encoder is None:
            label_encoder = LabelEncoder()
        self.label_encoder = label_encoder

    def collate_fn(self, batch: Sequence) -> Any:
        return self._collate(batch)


class TextClassificationCollator(PreTrainedCollator):
    def collate_train(
        self, batch: Sequence
    ) -> tuple[dict[str, torch.Tensor], torch.Tensor]:
        collated = collate(batch)

        x = self.tokenizer(
            collated["text"],
            padding=True,
            truncation=True,
            return_tensors="pt",
        )
        y = self.label_encoder.encode(collated["label"], return_tensors="pt")

        return x, y


class TextMatchingCollator(PreTrainedCollator):
    def __init__(
        self,
        tokenizer: PreTrainedTokenizer,
        label_encoder: Optional[LabelEncoder] = None,
        join_texts: bool = False,
        mode: ModeKeys = ModeKeys.TRAIN,
    ) -> None:
        super().__init__(tokenizer, label_encoder=label_encoder, mode=mode)
        self.join_texts = join_texts

    def collate_train(
        self, batch: Sequence
    ) -> tuple[dict[str, torch.Tensor], torch.Tensor]:
        # {
        #     "texts": ["sentence1", "sentence2", ...]
        #     "label": 1
        # }
        collated = collate(batch)

        if self.join_texts:
            x = self.tokenizer(
                collated["texts"],
                padding=True,
                truncation=True,
                return_tensors="pt",
            )
        else:
            batch_size = len(batch)
            texts = list(itertools.chain.from_iterable(zip(*collated["texts"])))
            assert (
                len(texts) % batch_size == 0
            ), 'All exmaples should have size of "texts" fields'

            x = self.tokenizer(
                texts,
                padding=True,
                truncation=True,
                return_tensors="pt",
            )
            chunks = len(texts) // batch_size

            def _stack(t):
                return torch.stack(t.chunk(chunks, dim=0), dim=0)

            x = {k: _stack(v) for k, v in x.items()}

        y = self.label_encoder.encode(collated["label"], return_tensors="pt")

        return x, y


class MaskedLMCollator(PreTrainedCollator):
    def __init__(
        self,
        tokenizer: PreTrainedTokenizer,
        mlm_probability: float = 0.15,
        max_length: int = 512,
        ignore_index: int = -100,
        mode: ModeKeys = ModeKeys.TRAIN,
    ) -> None:
        super().__init__(tokenizer=tokenizer, mode=mode)
        self.mlm_probability = torch.tensor(mlm_probability)
        self.max_length = max_length
        self.ignore_index = ignore_index

    def _whole_word_mask(self, tokens):
        masks = []
        for word_tokens in tokens:
            if (
                len(word_tokens) == 1
                and word_tokens[0] in self.tokenizer.all_special_tokens
            ):
                masks += [0]
            elif torch.rand(1) < self.mlm_probability:
                masks += [1] * len(word_tokens)
            else:
                masks += [0] * len(word_tokens)

        return masks

    def collate_train(self, batch: Sequence[Mapping]) -> Any:
        collated = collate(batch)  # type: ignore
        collated = [
            [self.tokenizer.cls_token] + x + [self.tokenizer.sep_token]
            for x in collated
        ]

        def _truncate(tokens):
            cls, *tokens, sep = tokens
            truncated = []
            length = self.max_length - 2
            for token in tokens:
                if len(token) <= length:
                    truncated += [token]
                    length -= len(token)
                else:
                    break

            return [cls] + truncated + [sep]

        keys = ["input_ids", "token_type_ids", "attention_mask"]
        input_lists = dict(zip(keys, [[], [], []]))  # type: ignore
        whole_word_masks = []
        for words in collated:
            encoded_inputs = self.tokenizer(words, add_special_tokens=False)
            encoded_inputs = {key: _truncate(encoded_inputs[key]) for key in keys}
            whole_word_masks += [self._whole_word_mask(encoded_inputs["input_ids"])]

            for key in keys:
                input_lists[key] += [
                    list(itertools.chain.from_iterable(encoded_inputs[key]))
                ]

        inputs = self.tokenizer.pad(input_lists, padding=True, return_tensors="pt")
        input_id: torch.Tensor = inputs["input_ids"]

        max_length = input_id.size(1)
        whole_word_mask = torch.tensor(
            [x + [0] * (max_length - len(x)) for x in whole_word_masks],
            dtype=torch.bool,
        )

        label = input_id.clone()
        label[~whole_word_mask] = self.ignore_index

        replace_mask = (
            torch.bernoulli(torch.full(input_id.size(), 0.8)).bool() & whole_word_mask
        )
        input_id[replace_mask] = self.tokenizer.mask_token_id

        random_mask = (
            torch.bernoulli(torch.full(input_id.size(), 0.1)).bool()
            & whole_word_mask
            & ~replace_mask
        )
        random_words = torch.randint(len(self.tokenizer), input_id.size())
        input_id[random_mask] = random_words[random_mask]

        inputs["input_ids"] = input_id
        inputs["mlm_mask"] = whole_word_mask.long()

        return inputs, label

    def collate_predict(self, batch: Sequence) -> Any:
        return self.collate_train(batch)
