# -*- coding: utf-8 -*-

from __future__ import annotations

import logging
import os
from collections.abc import Iterable, Mapping, Sequence
from typing import Optional, Union

from carton.palette import Colors
from carton.random import random_colors

from texi.apps.ner.utils import NerExample, texify_example
from texi.metrics import prf1

logger = logging.getLogger(__name__)


def spacy_visual_ner(
    examples: Sequence[NerExample],
    filename: Optional[Union[str, os.PathLike]] = None,
    colors: Optional[Mapping[str, str]] = None,
    token_sep: str = " ",
) -> None:
    # pylint: disable=import-outside-toplevel
    from spacy import displacy

    # Generate spacy inputs.
    examples = [texify_example(x, token_sep) for x in examples]  # type: ignore
    spacy_data = [
        {
            "text": example["tokens"],
            "ents": [
                {"start": x["start"], "end": x["end"], "label": x["type"]}
                for x in example["entities"]
            ],
            "title": example.get("id", f"#{i}"),
        }
        for i, example in enumerate(examples)
    ]

    # Give each type a color.
    if not colors:
        types = set(x["type"] for example in examples for x in example["entities"])
        colors = dict(zip(types, random_colors(Colors.PRESETS, num=len(types))))

    if filename:
        html = displacy.render(
            spacy_data, style="ent", manual=True, options={"colors": colors}, page=True
        )
        with open(filename, mode="w") as f:
            f.writelines(html)
        return

    displacy.serve(
        spacy_data, style="ent", manual=True, options={"colors": colors}, page=True
    )


class NerReVisualizer(object):
    # Reference: https://github.com/markus-eberts/spert

    def __init__(self, delimiter: str = " ") -> None:
        self.delimiter = delimiter

        dirname = os.path.join(os.path.dirname(__file__), "templates")

        self.entity_template = self._load_template(
            os.path.join(dirname, "entity_examples.html")
        )
        self.relation_template = self._load_template(
            os.path.join(dirname, "relation_examples.html")
        )

    def _load_template(self, filename):
        # pylint: disable=no-self-use, import-outside-toplevel
        import jinja2

        with open(filename) as f:
            template = jinja2.Template(f.read())

        return template

    def _entity_to_html(self, entity, tokens):
        tag_start = ' <span class="entity">'
        tag_start += '<span class="type">%s</span>' % entity["type"]

        ctx_before = self.delimiter.join(tokens[: entity["start"]])
        e1 = self.delimiter.join(tokens[entity["start"] : entity["end"]])
        ctx_after = self.delimiter.join(tokens[entity["end"] :])

        html = ctx_before + tag_start + e1 + "</span> " + ctx_after

        return html

    def _relation_to_html(self, relation, tokens):
        head, tail = relation["head"], relation["tail"]

        if not (head["end"] <= tail["start"] or tail["end"] <= head["start"]):
            logger.warning(
                "Detected relation with overlapped entities: %s - %s.", head, tail
            )

        if head["start"] > tail["start"]:
            head, tail = tail, head

        head_tag = ' <span class="head"><span class="type">%s</span>'
        tail_tag = ' <span class="tail"><span class="type">%s</span>'

        ctx_before = self.delimiter.join(tokens[: head["start"]])
        e1 = self.delimiter.join(tokens[head["start"] : head["end"]])
        ctx_between = self.delimiter.join(tokens[head["end"] : tail["start"]])
        e2 = self.delimiter.join(tokens[tail["start"] : tail["end"]])
        ctx_after = self.delimiter.join(tokens[tail["end"] :])

        html = (
            ctx_before
            + head_tag % head["type"]
            + e1
            + "</span> "
            + ctx_between
            + tail_tag % tail["type"]
            + e2
            + "</span> "
            + ctx_after
        )

        return html

    def _compute_metrics(self, tp, fp, fn):
        # pylint: disable=no-self-use

        return {key: value * 100 for key, value in prf1(tp, fp, fn).items()}

    def _export(self, examples, filename, key, to_html_fn, template):
        def _format(x):
            groups = {-1: [], 0: [], 1: []}
            for xi, type_, score in x[key]:
                item = (
                    to_html_fn(xi, x["tokens"]),
                    xi["type"],
                    score,
                )
                groups[type_] += [item]

            tp, fp, fn = groups[0], groups[1], groups[-1]

            tp = sorted(tp, key=lambda x: -x[-1])
            fp = sorted(fp, key=lambda x: -x[-1])

            return {
                "text": self.delimiter.join(x["tokens"]),
                "length": len(x["tokens"]),
                "tp": tp,
                "fp": fp,
                "fn": fn,
                **self._compute_metrics(len(tp), len(fp), len(fn)),
            }

        examples = sorted(map(_format, examples), key=lambda x: -x["f1"])
        template.stream(examples=examples).dump(filename)

    def export_entities(
        self, examples: Iterable[Mapping], filename: Union[str, os.PathLike]
    ) -> None:
        """
        Input format:

        type: 0: tp, 1: fp, -1: fn
        score: [0, 1]

        {
            "tokens": ["Bill", "was", "born", "in", "USA", "."],
            "entities": [
                ({"type": "per", "start": 0, "end": 1}, 0, 0.99999),
                ({"type": "loc", "start": 4, "end": 5}, -1, -1),
            ]
        }
        """
        return self._export(
            examples,
            filename,
            "entities",
            self._entity_to_html,
            self.entity_template,
        )

    def export_relations(
        self, examples: Iterable[Mapping], filename: Union[str, os.PathLike]
    ) -> None:
        """
        Input format:

        type: 0: tp, 1: fp, -1: fn
        score: [0, 1]

        {
            "tokens": ["Bill", "was", "born", "in", "USA", "."],
            "relations": [
                ({"type": "fake", "head": 1, "tail": 0}, 0, 0.75)
            ]
        }
        """
        return self._export(
            examples,
            filename,
            "relations",
            self._relation_to_html,
            self.relation_template,
        )
