"""
    Module d'interprétation de la configuration des geos
"""

from typing import List, Union, Optional

import xarray as xr
from pydantic import validator

from mfire.settings import get_logger, Settings
from mfire.utils.xr_utils import MaskLoader
from mfire.composite.base import BaseComposite


# Logging
LOGGER = get_logger(name="geos.mod", bind="geos")


class GeoComposite(BaseComposite):
    """Création d'un objet Geo contenant la configuration des périodes
    de la tâche de production promethee

    Args:
        baseModel : modèle de la librairie pydantic

    Returns:
        baseModel : objet Geo
    """

    file: str
    mask_id: Optional[Union[List[str], str]]
    grid_name: Optional[str]

    def _compute(self) -> xr.DataArray:
        return MaskLoader(filename=self.file, grid_name=self.grid_name).load(
            ids_list=self.mask_id
        )


class AltitudeComposite(BaseComposite):
    """Création d'un objet Field contenant la configuration des champs
    de la tâche de production promethee

    Args:
        baseModel : modèle de la librairie pydantic

    Returns:
        baseModel : objet Field
    """

    filename: str = Settings().altitudes_filename
    grid_name: Optional[str]
    alt_min: Optional[int] = -100
    alt_max: Optional[int] = 10000

    @validator("alt_min")
    def init_alt_min(cls, v: int) -> int:
        if v is None:
            return -100
        return v

    @validator("alt_max")
    def init_alt_max(cls, v: int) -> int:
        if v is None:
            return 10000
        return v

    @validator("filename")
    def init_filename(cls, v: str) -> str:
        if v is None:
            return Settings().altitudes_filename
        return v

    def _compute(self) -> xr.DataArray:
        # on load le fichier d'altitude
        field_da = MaskLoader(filename=self.filename, grid_name=self.grid_name).load()
        # on applique les restrictions d'alt min et alt max
        return field_da.where(field_da >= self.alt_min).where(field_da <= self.alt_max)
