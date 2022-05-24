"""
    Module d'interprétation de la configuration des geos
"""

from pydantic import validator
from typing import Optional, Dict

import xarray as xr

from mfire.settings import get_logger, TEXT_ALGO
from mfire.utils.xr_utils import Loader, mask_set_up
from mfire.composite.base import BaseComposite
from mfire.composite.events import EventComposite
from mfire.composite.levels import LocalisationConfig
from mfire.composite.fields import FieldComposite
from mfire.composite.geos import GeoComposite, AltitudeComposite


# Logging
LOGGER = get_logger(name="weather.mod", bind="weather")


class WeatherComposite(BaseComposite):
    """Création d'un objet weather contenant la configuration des weathers
    de la tâche de production promethee

    Args:
        baseModel : modèle de la librairie pydantic

    Returns:
        baseModel : objet Weather
    """

    id: str
    condition: EventComposite
    params: Dict[str, FieldComposite]
    altitude: Optional[AltitudeComposite]
    geos: Optional[GeoComposite]
    localisation: LocalisationConfig

    @validator("params")
    def validate_params(cls, v, values):
        """ validate param's keys
        """

        params_expected = TEXT_ALGO[values["id"]][values.get("algo", "generic")][
            "params"
        ].keys()

        if v.keys() != params_expected:
            raise ValueError(f"Wrong field : {v.keys()}, expected {params_expected}")
        return v

    @property
    def _cached_attrs(self) -> dict:
        return {"data": Loader}

    def verify_condition(self) -> bool:
        event_da = self.condition.compute()

        return bool(event_da.sum().values == event_da.count().values)

    def _compute(self) -> xr.Dataset:
        if not self.verify_condition():
            output_ds = xr.Dataset()

        # 1. initialisation des fields
        fields_ds = xr.Dataset(
            {name: field.compute() for name, field in self.params.items()}
        )

        # 2. ajout du champs altitude et création d'un masque altitude
        alt_mask_da = None
        if self.altitude is not None:
            fields_ds["altitude"] = mask_set_up(self.altitude.compute(), fields_ds)
            alt_mask_da = fields_ds["altitude"] >= self.altitude.alt_min

        # 3. création du masque geo
        geo_mask_da = None
        if self.geos is not None:
            geo_mask_da = mask_set_up(self.geos.compute(), fields_ds)
        if geo_mask_da is None:
            if alt_mask_da is None:
                output_ds = fields_ds
            output_ds = fields_ds * alt_mask_da
        elif alt_mask_da is None:
            output_ds = fields_ds * geo_mask_da
        else:
            output_ds = fields_ds * (geo_mask_da * alt_mask_da)

        # On check que les variables sont bien presentes.

        if hasattr(geo_mask_da, "areaName"):
            output_ds["areaName"] = geo_mask_da["areaName"]
        elif hasattr(geo_mask_da, "label"):
            output_ds["areaName"] = geo_mask_da["label"]
        else:
            output_ds["areaName"] = (
                "id",
                ["unknown" for _ in range(geo_mask_da.id.size)],
            )

        if hasattr(geo_mask_da, "areaType"):
            output_ds["areaType"] = geo_mask_da["areaType"]
        elif hasattr(geo_mask_da, "type"):
            output_ds["areaType"] = geo_mask_da["type"]
        else:
            output_ds["areaType"] = (
                "id",
                ["unknown" for _ in range(geo_mask_da.id.size)],
            )

        return output_ds
