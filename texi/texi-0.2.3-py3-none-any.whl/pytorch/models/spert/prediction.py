# -*- coding: utf-8 -*-

from typing import List, Tuple, Union, cast

import torch
from torchlight.preprocessing import LabelEncoder

from texi.apps.ner.utils import Entity, Relation

Entities = List[List[Entity]]
Relations = List[List[Relation]]
Scores = List[List[float]]
EntityWithScores = Tuple[Entities, Scores]
RelationWithScores = Tuple[Relations, Scores]


def predict_entities(
    entity_logit: torch.Tensor,
    entity_sample_mask: torch.LongTensor,
    entity_span: torch.LongTensor,
    entity_label_encoder: LabelEncoder,
    return_scores: bool = False,
) -> Union[Entities, EntityWithScores]:
    if entity_logit.ndim == 3:
        entity_label = entity_logit.argmax(dim=-1)
        entity_probas = torch.softmax(entity_logit, dim=-1).tolist()
    elif entity_logit.ndim == 2:
        if return_scores:
            raise ValueError(
                "`return_score` must be False when entity targets are given"
            )
        entity_label = entity_logit
    else:
        raise ValueError("`entity_logit` should have 2 or 3 dimensions")

    entity_label = entity_label.masked_fill(~entity_sample_mask.bool(), -1).long()

    # Decode entities.
    entity_labels = entity_label.tolist()
    entity_spans = entity_span.tolist()

    entities, scores = [], []
    for i, labels in enumerate(entity_labels):
        sample_entities, sample_scores = [], []
        for j, label in enumerate(labels):
            if label >= 0:
                entity: Entity = {
                    "type": entity_label_encoder.decode_label(label),
                    "start": entity_spans[i][j][0],
                    "end": entity_spans[i][j][1],
                }
                sample_entities += [entity]

                if return_scores:
                    sample_scores += [entity_probas[i][j][label]]

        entities += [sample_entities]
        scores += [sample_scores]

    if return_scores:
        return entities, scores

    return entities


def predict_relations(
    relation_logit: torch.Tensor,
    relation_pair: torch.LongTensor,
    relation_sample_mask: torch.LongTensor,
    relation_label_encoder: LabelEncoder,
    relation_filter_threshold: float,
    return_scores: bool = False,
) -> Union[Relations, RelationWithScores]:
    if relation_logit.dtype == torch.float32:
        relation_proba = torch.sigmoid(relation_logit)
    elif relation_logit.dtype == torch.int64:
        if return_scores:
            raise ValueError(
                "`return_score` must be False when entity targets are given"
            )
        relation_proba = relation_logit
    else:
        raise TypeError(
            "`relation_logit` should `torch.int64` dtype when target is passed"
            " or `torch.float32` dtype when logit is passed"
        )

    if relation_pair.size(1) < 1:
        if return_scores:
            return (
                [[] for _ in range(len(relation_pair))],  # type: ignore
                [[] for _ in range(len(relation_pair))],  # type: ignore
            )

        return [[] for _ in range(len(relation_pair))]  # type: ignore

    filter_mask = relation_proba < relation_filter_threshold
    sample_mask = relation_sample_mask.unsqueeze(dim=-1).bool()
    relation_proba = relation_proba.masked_fill(~sample_mask | filter_mask, -1)

    pairs = relation_pair.tolist()
    relations, scores = [], []
    for i, sample_labels in enumerate(relation_proba.tolist()):
        sample_relations, sample_scores = [], []
        for j, labels in enumerate(sample_labels):
            for k, label in enumerate(labels):
                if label >= 0:
                    relation: Relation = {
                        "type": relation_label_encoder.decode_label(k),
                        "head": pairs[i][j][0],
                        "tail": pairs[i][j][1],
                    }
                    sample_relations += [relation]

                    if return_scores:
                        sample_scores += [label]

        relations += [sample_relations]
        scores += [sample_scores]

    if return_scores:
        return relations, scores

    return relations


def predict(
    entity_logit: torch.Tensor,
    entity_mask: torch.LongTensor,
    entity_span: torch.LongTensor,
    entity_label_encoder: LabelEncoder,
    negative_entity_index: int,
    relation_logit: torch.FloatTensor,
    relation_pair: torch.LongTensor,
    relation_sample_mask: torch.LongTensor,
    relation_label_encoder: LabelEncoder,
    negative_relation_index: int,
    relation_filter_threshold: float,
    return_scores: bool = False,
) -> Union[Tuple[Entities, Relations], Tuple[Entities, Scores, Relations, Scores]]:
    # pylint: disable=too-many-arguments

    if relation_pair.size(1) > 0:
        assert relation_pair.max() < entity_logit.size(1)

    # Predict entities.
    entity_outputs = predict_entities(
        entity_logit,
        entity_mask,
        entity_span,
        entity_label_encoder,
        return_scores=return_scores,
    )

    # Predict relation.
    relation_outputs = predict_relations(
        relation_logit,
        relation_pair,
        relation_sample_mask,
        relation_label_encoder,
        relation_filter_threshold,
        return_scores=return_scores,
    )

    negative_entity_label = entity_label_encoder.decode_label(negative_entity_index)
    negative_relation_label = relation_label_encoder.decode_label(
        negative_relation_index
    )

    def _normalize(entities, relations):
        new_entities = []
        entity_indices = {}
        for i, entity in enumerate(entities):
            if entity["type"] != negative_entity_label:
                entity_indices[i] = len(entity_indices)
                new_entities += [entity]

        new_relations = [
            {
                "type": r["type"],
                "head": entity_indices[r["head"]],
                "tail": entity_indices[r["tail"]],
            }
            for r in relations
            if r["type"] != negative_relation_label
        ]

        assert all(x["type"] != negative_entity_label for x in new_entities)
        assert all(
            x["type"] != negative_relation_label
            and new_entities[x["head"]]["type"] != negative_entity_label
            and new_entities[x["tail"]]["type"] != negative_entity_label
            for x in new_relations
        )

        return new_entities, new_relations

    if return_scores:
        entities, entity_scores = cast(EntityWithScores, entity_outputs)
        relations, relation_scores = cast(RelationWithScores, relation_outputs)
    else:
        entities = cast(Entities, entity_outputs)
        relations = cast(Relations, relation_outputs)

    normalized_entities, normalized_relations = zip(
        *[_normalize(e, r) for e, r in zip(entities, relations)]
    )
    entities = list(normalized_entities)
    relations = list(normalized_relations)

    if return_scores:
        return entities, entity_scores, relations, relation_scores

    return entities, relations
