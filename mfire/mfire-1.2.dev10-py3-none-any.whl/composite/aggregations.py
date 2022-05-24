"""
    Module d'interprétation de la configuration des geos
"""
from __future__ import annotations

from pydantic import BaseModel, validator

from typing import Optional
from enum import Enum

from mfire.composite.geos import GeoComposite
from mfire.data.aggregator import AggregationMethod


class AggregationType(str, Enum):
    """Création d'une classe d'énumération contenant les differents
    types d'aggregation
    """

    UP_STREAM = "upStream"
    DOWN_STREAM = "downStream"


class AggregationKwargs(BaseModel):
    """Création d'un objet Kwards contenant la configuration des méthode d'agrégation

    Args:
        BaseModel : Kwargs
    """

    dr: float
    # deprecated
    central_weight: Optional[int]
    # deprecated
    outer_weight: Optional[int]
    central_mask_id: Optional[GeoComposite]


class Aggregation(BaseModel):
    """Création d'un objet Agrégation contenant la configuration des méthodes d'agrégations
    de la tâche de production promethee

    Args:
        baseModel : modèle de la librairie pydantic

    Returns:
        baseModel : objet Aggregation
    """

    kwargs: Optional[AggregationKwargs]
    method: AggregationMethod

    @validator("method")
    def check_method_kwargs(cls, method, values):
        if method == AggregationMethod.MEAN:
            if values["kwargs"] is not None:
                raise ValueError("erreur aggregation kwargs 2")
        else:
            dic_kwargs = values["kwargs"].dict()

            keys_missing = dict()
            keys_unexpecting = dict()

            keys_missing[AggregationMethod.RDENSITY] = ["dr"]
            keys_unexpecting[AggregationMethod.RDENSITY] = (
                "central_weight",
                "outer_weight",
                "central_mask_id",
            )

            keys_missing[AggregationMethod.RDENSITY_CONDITIONAL] = (
                "dr",
                "central_mask_id",
            )
            keys_unexpecting[AggregationMethod.RDENSITY_CONDITIONAL] = (
                "central_weight",
                "outer_weight",
            )

            keys_missing[AggregationMethod.RDENSITY_WEIGHTED] = (
                "dr",
                "central_mask_id",
                "central_weight",
                "outer_weight",
            )
            keys_unexpecting[AggregationMethod.RDENSITY_WEIGHTED] = ()

            missing = [key for key in keys_missing[method] if dic_kwargs[key] is None]
            if missing:
                raise ValueError(f"Missing expected values {missing}")

            not_missing = [
                key for key in keys_unexpecting[method] if dic_kwargs[key] is not None
            ]
            if not_missing:
                raise ValueError(f"unexpected values {not_missing}")

        return method
