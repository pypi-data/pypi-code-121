# -*- coding: utf-8 -*-

from __future__ import annotations

import collections
import itertools
import os
import re
from collections.abc import Mapping, Sequence
from typing import Any, Union

import ahocorasick
import pandas as pd
import plotly.figure_factory as ff
import plotly.io as io


class NERDataReport(object):
    def __init__(
        self, examples: Sequence[Mapping], seps: str = "。", k: int = 10
    ) -> None:
        # TODO: 2019-09-27 Accept list of tokens inputs of `text` field.
        self.examples = list(examples)
        self.seps = seps
        self.k = k

    def _group_entities(self, entities, unique=True):
        agg = set if unique else list

        return [
            (key, agg(x[1] for x in agg(group)))
            for key, group in itertools.groupby(
                sorted(entities, key=lambda x: x[0]), key=lambda x: x[0]
            )
        ]

    def _split_sentence(self, text):
        if not self.seps:
            return [text]

        text = re.sub(rf"{re.escape(self.seps)}$", "", text)
        sentences = re.split(rf"{re.escape(self.seps)}", text)

        return sentences

    @property
    def entities(self) -> list[tuple[str, str]]:
        return [
            (x["tag"], x["token"]) for sample in self.examples for x in sample["chunks"]
        ]

    @property
    def sentences(self) -> list[str]:
        return [
            *itertools.chain.from_iterable(
                self._split_sentence(x["tokens"]) for x in self.examples
            )
        ]

    @property
    def sample_size(self) -> int:
        return len(self.examples)

    @property
    def annotation_consistency(self) -> float:
        passes = 0
        for example in self.examples:
            text = example["tokens"]
            for entity in example["chunks"]:
                if text[entity["start"] : entity["end"]] != entity["token"]:
                    break
            else:
                passes += 1
        consistency = passes / len(self.examples)

        return consistency

    @property
    def annotation_rate(self) -> float:
        def _tag(text, entities):
            tags = ["O"] * len(text)
            for entity in entities:
                tags[entity["start"] : entity["end"]] = ["N"] * (
                    entity["end"] - entity["start"]
                )

            return tags

        def _split(text, tags):
            split_tags = []
            sample_tags = []
            for i, (char, tag) in enumerate(zip(text, tags)):
                sample_tags += [tag]
                if (char in self.seps or i == len(text) - 1) and sample_tags:
                    split_tags += [sample_tags]
                    sample_tags = []

            return split_tags

        tagged = [(x["tokens"], _tag(x["tokens"], x["chunks"])) for x in self.examples]
        tags = [*itertools.chain.from_iterable(_split(*x) for x in tagged)]

        annotated = {i for i, x in enumerate(tags) if set(x) == {"O"}}
        annotation_rate = len(annotated) / len(tags)

        return annotation_rate

    @property
    def annotation_missing_rate(self) -> float:
        actree = ahocorasick.Automaton()
        counts = {x["token"]: 0 for example in self.examples for x in example["chunks"]}
        for word in counts.keys():
            actree.add_word(word, word)
        actree.make_automaton()

        for example in self.examples:
            text = example["tokens"]
            entities = list(
                sorted(example["chunks"], key=lambda x: (x["start"], x["end"]))
            )
            for i, entity in enumerate(entities):
                if i == 0:
                    span = text[: entity["start"]]
                elif i == len(entities) - 1:
                    span = text[entity["end"] :]
                else:
                    span = text[entities[i - 1]["end"] : entity["start"]]

                for _, match in actree.iter(span):
                    counts[match] += 1

        missing_counts = len(
            {i for i, count in enumerate(counts.values()) if count > 0}
        )
        missing_rate = missing_counts / len(counts)

        return missing_rate

    @property
    def text_length(self) -> float:
        average_length = sum(len(x["tokens"]) for x in self.examples) / len(
            self.examples
        )

        return average_length

    @property
    def sentence_average_length(self) -> float:
        average_length = sum(len(x) for x in self.sentences) / len(self.sentences)

        return average_length

    @property
    def sentence_average_count(self) -> float:
        average_count = len(self.sentences) / len(self.examples)

        return average_count

    @property
    def sentence_overlapping_rate(self) -> float:
        counter = collections.Counter(self.sentences)
        overlaps = {key: value for key, value in counter.items() if value > 1}
        overlapping_rate = len(overlaps) / len(counter)

        return overlapping_rate

    @property
    def entity_singleton_size(self) -> int:
        counter = collections.Counter(self.entities)
        singletons = {key for key, value in counter.items() if value < 2}

        return len(singletons)

    @property
    def entity_imbalance(self) -> float:
        counts = dict(collections.Counter([key for key, _ in self.entities]))
        total = sum(counts.values())
        dists = {key: value / total for key, value in counts.items()}
        imbalance = max(dists.values()) / min(dists.values())

        return imbalance

    @property
    def entity_size(self) -> dict[str, int]:
        entities = self._group_entities(self.entities, unique=False)
        sizes = {key: len(value) for key, value in entities}

        return sizes

    @property
    def entity_frequence(self) -> dict[str, float]:
        entities = self._group_entities(self.entities, unique=False)
        counters = {
            key: collections.Counter(value) for key, value in entities
        }  # type: dict[str, collections.Counter[str]]
        freqs = {
            key: sum(value.values()) / len(value) for key, value in counters.items()
        }

        return freqs

    @property
    def entity_uniques(self) -> dict[str, int]:
        entities = self._group_entities(self.entities, unique=True)
        uniques = {key: len(value) for key, value in entities}

        return uniques

    @property
    def entity_overlapping_rate(self) -> dict[tuple[str, str], float]:
        entities = self._group_entities(self.entities, unique=True)
        overlaps = {}
        for k1, v1 in entities:
            for k2, v2 in entities:
                overlaps[(k1, k2)] = len(v1 & v2) / min(len(v1), len(v2))

        return overlaps

    @property
    def top_entities(self) -> dict[str, tuple[str, int, float, float]]:
        def _top_k(entities):
            counter = collections.Counter(entities)
            total = sum(counter.values())
            top_k = counter.most_common(self.k)

            return [x + (x[1] / total, x[1] / len(counter)) for x in top_k]

        return {
            type_: _top_k(entities)
            for type_, entities in self._group_entities(self.entities, unique=False)
        }

    def describe(self) -> dict[str, Any]:
        indicators = [
            "sample_size",
            "annotation_consistency",
            "annotation_rate",
            "annotation_missing_rate",
            "text_length",
            "sentence_average_count",
            "sentence_average_length",
            "sentence_overlapping_rate",
            "entity_singleton_size",
            "entity_imbalance",
            "entity_size",
            "entity_uniques",
            "entity_frequence",
            "entity_overlapping_rate",
            "top_entities",
        ]

        return {indicator: getattr(self, indicator) for indicator in indicators}

    def to_html(self, filename: Union[str, os.PathLike]) -> None:
        border = pd.options.display.html.border
        pd.options.display.html.border = 0

        report = self.describe()

        # Overview
        body = ["<h1>Overview</h1>"]
        overview_index = [
            "sample_size",
            "annotation_consistency",
            "annotation_rate",
            "annotation_missing_rate",
            "text_length",
            "sentence_average_count",
            "sentence_average_length",
            "sentence_overlapping_rate",
            "entity_singleton_size",
            "entity_imbalance",
        ]
        overview = pd.Series(
            {k: report[k] for k in overview_index}, index=overview_index, name="value"
        )
        body += [overview.to_frame().to_html()]

        body += ["<h1>Entity</h1>"]
        entity_report_columns = ["entity_size", "entity_uniques", "entity_frequence"]
        entity_report = pd.DataFrame(
            {k: report[k] for k in entity_report_columns}, columns=entity_report_columns
        )
        entity_report.loc["#SUM"] = entity_report.sum(axis=0)
        body += [entity_report.to_html()]
        body += ["<h2>Overlapping</h2>"]
        entity_overlapping_rate = (
            pd.Series(
                report["entity_overlapping_rate"].values(),
                index=pd.MultiIndex.from_tuples(
                    report["entity_overlapping_rate"].keys()
                ),
            )
            .round(2)
            .unstack()
        )
        fig_entity_overlapping_rate = ff.create_annotated_heatmap(
            z=entity_overlapping_rate.values,
            x=entity_overlapping_rate.index.tolist(),
            y=entity_overlapping_rate.columns.tolist(),
            zmin=0,
            zmax=1,
            showscale=True,
            colorscale="Blues",
        )
        body += [io.to_html(fig_entity_overlapping_rate)]

        body += ["<h2>Top Entities</h2>"]
        for type_, top_k in report["top_entities"].items():
            body += [f"<h3>{type_}</h3>"]
            df_top = pd.DataFrame.from_records(
                top_k, columns=["entity", "count", "frequency", "frequency-unique"]
            ).set_index("entity")
            df_top.loc["#SUM"] = df_top.sum(axis=0)
            body += [df_top.to_html()]

        title = "NER Report"
        body = "".join(body)  # type: ignore
        html = f"""<html>
        <head>
            <title>{title}</title>
            <link rel="stylesheet" href="https://cdn.jsdelivr.net/gh/kognise/water.css@latest/dist/light.min.css">
        </head>
        <body>{body}</body>
    </html>"""

        with open(filename, mode="w") as f:
            f.writelines(html)

        pd.options.display.html.border = border
