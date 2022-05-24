"""
    Module d'interprétation de la configuration, objet fields
"""

from typing import Iterable, Optional, Any

import xarray as xr
from pydantic import BaseModel, root_validator, validator

from mfire.settings import get_logger
from mfire.utils.date import Datetime
from mfire.utils.xr_utils import ArrayLoader
from mfire.composite.base import BaseComposite


# Logging
LOGGER = get_logger(name="composite.fields.mod", bind="composite.fields")


class Selection(BaseModel):
    """Création d'un objet Selection

    Args:
        baseModel : modèle de la librairie pydantic

    Returns:
        baseModel : objet Selection
    """

    sel: Optional[dict] = dict()
    slice: Optional[dict] = dict()
    isel: Optional[dict] = dict()
    islice: Optional[dict] = dict()

    @root_validator(pre=True)
    def check_all_keys(cls, values: dict):
        _ = dict(
            **values.get("sel", dict()),
            **values.get("slice", dict()),
            **values.get("isel", dict()),
            **values.get("islice", dict()),
        )
        return values

    @validator("sel", "slice", pre=True)
    def check_valid_times(cls, value: dict):
        if isinstance(value.get("valid_time"), Iterable):
            value["valid_time"] = [
                Datetime(dt).as_np_datetime64() for dt in value["valid_time"]
            ]
        return value

    @validator("slice", "islice")
    def init_slices(cls, value: dict) -> dict:
        dico = dict()
        for key, val in value.items():
            if isinstance(val, Iterable):
                dico[key] = slice(*val)
            else:
                dico[key] = val
        return dico

    def select(self, da: xr.DataArray) -> xr.DataArray:
        return da.isel(**self.isel, **self.islice).sel(**self.sel, **self.slice)

    def get_all(self) -> dict:
        return dict(**self.sel, **self.slice, **self.isel, **self.islice)

    def update(
        self,
        sel: dict = dict(),
        slice: dict = dict(),
        isel: dict = dict(),
        islice: dict = dict(),
    ):
        """Method for updating the current selection dict with new ones

        Args:
            sel (dict, optional): Dictionary sel. Defaults to None.
            slice (dict, optional): Dictionary slice. Defaults to None.
            isel (dict, optional): Dictionary isel. Defaults to None.
            islice (dict, optional): Dictionary islice. Defaults to {}.
        """
        # creating new selection
        new_sel = Selection(sel=sel, slice=slice, isel=isel, islice=islice)
        # dropping updated keys in self
        for dico in (self.sel, self.slice, self.isel, self.islice):
            _ = [dico.pop(key, None) for key in set(new_sel.get_all())]
        # updating old self selection
        self.sel.update(new_sel.sel)
        self.slice.update(new_sel.slice)
        self.isel.update(new_sel.isel)
        self.islice.update(new_sel.islice)


class FieldComposite(BaseComposite):
    """Création d'un objet Field contenant la configuration des champs
    de la tâche de production promethee

    Args:
        baseModel : modèle de la librairie pydantic

    Returns:
        baseModel : objet Field
    """

    file: str
    selection: Optional[Selection] = None
    grid_name: str
    name: str

    @validator("selection", always=True)
    def check_selection(cls, v):
        if v is None:
            return Selection()
        return v

    def _compute(self) -> xr.DataArray:
        field_da = ArrayLoader(filename=self.file).load()
        field_da = self.selection.select(field_da)
        LOGGER.debug(
            "Opening Field file",
            filename=self.file,
            da_name=field_da.name,
            da_grid_name=field_da.attrs.get("PROMETHEE_z_ref"),
            shape=field_da.shape,
            dims=field_da.dims,
        )
        return field_da

    def get_coord(self, coord_name: str) -> Any:
        if self._data is None:
            with xr.open_dataarray(self.file) as tmp_da:
                return tmp_da[coord_name].load()
        return self._data[coord_name]
