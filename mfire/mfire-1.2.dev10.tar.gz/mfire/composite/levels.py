"""
    Module de production des Levels
"""
from typing import List, Optional, Union

import xarray as xr
from pydantic import BaseModel, validator

from mfire.settings import get_logger
from mfire.utils.xr_utils import Loader, ArrayLoader
from mfire.data.aggregator import Aggregator
from mfire.composite.base import BaseComposite
from mfire.composite.aggregations import Aggregation, AggregationType
from mfire.composite.operators import LogicalOperator
from mfire.composite.geos import GeoComposite
from mfire.composite.events import EventComposite, EventBertrandComposite


# Logging
LOGGER = get_logger(name="levels.mod", bind="level")


class LocalisationConfig(BaseModel):
    """Classe contenant les informations relatives à la localisation
    """

    compass_split: bool = False
    altitude_split: bool = False
    geos_descriptive: List[str] = []


class LevelComposite(BaseComposite):
    """Création d'un objet level contenant la configuration des levels
    de la tâche de production promethee

    Args:
        baseModel : modèle de la librairie pydantic

    Returns:
        baseModel : objet Level
    """

    level: int
    aggregation_type: AggregationType
    aggregation: Optional[Aggregation]
    logical_op_list: Optional[List[str]]
    probability: str
    elements_event: List[Union[EventBertrandComposite, EventComposite]]
    time_dimension: Optional[str]
    compute_list: Optional[List[str]] = []
    localisation: LocalisationConfig
    _spatial_risk_da: xr.DataArray = xr.DataArray()
    _mask_da: xr.DataArray = None

    @validator("aggregation")
    def check_aggregation(cls, v, values):
        # cohérence aggregation et aggregation_type
        agg_type = values.get("aggregation_type")
        if bool(v) and agg_type == AggregationType.UP_STREAM:
            # là on force le l'aggregation à None
            return None
        if v is None and agg_type == AggregationType.DOWN_STREAM:
            raise ValueError("Missing expected value 'aggregation' in level")
        return v

    @validator("elements_event")
    def check_nb_elements(cls, v, values):
        # coherence len(elements_event) et len(logical_op_list)
        # cas AggregationType.UP_STREAM
        logical_op_list = values.get("logical_op_list", [])
        agg_type = values.get("aggregation_type")
        if agg_type == AggregationType.UP_STREAM:
            if len(logical_op_list) != len(v) - 1:
                raise AttributeError(
                    f"The number of logical operator ({len(logical_op_list)})"
                    " is not consistent with the len of element list"
                    f"(n={len(v)}. Should be {len(v)-1}."
                )
        return v

    @validator("compute_list")
    def check_compute_list(cls, v: Optional[List[str]] = None) -> List[str]:
        if v is None:
            return []
        return v

    @property
    def mask_da(self) -> xr.DataArray:
        if self._mask_da is None:
            mask_list = []
            for i, evt in enumerate(self.elements_event):
                if isinstance(evt.geos, xr.DataArray):  # ! temporary #GeoGate
                    geo_da = evt.geos
                elif isinstance(evt.geos, GeoComposite):  # ! temporary #GeoGate
                    if evt.geos.grid_name is None:
                        evt.field.compute()
                        # ! temporairement on assigne le grid_name comme ça
                        evt.geos.grid_name = evt.field.grid_name
                    geo_da = evt.geos.compute()
                mask_list.append(geo_da.expand_dims("place").assign_coords(place=[i]))
            self._mask_da = xr.concat(mask_list, dim="place").max(dim="place")
        return self._mask_da

    @property
    def spatial_risk_da(self) -> xr.DataArray:
        return self._spatial_risk_da

    @property
    def _cached_attrs(self) -> dict:
        return {
            "data": Loader,
            "spatial_risk_da": ArrayLoader,
            "mask_da": ArrayLoader,
        }

    def _compute(self) -> xr.Dataset:
        global LOGGER
        LOGGER = LOGGER.bind(level=self.level, composite_hash=self.hash)
        LOGGER.debug("Launching level.compute_risk")
        output_ds = self._compute_risk()
        LOGGER.debug("level.compute_risk done")
        LOGGER.try_unbind("level", "composite_hash")
        return output_ds

    def get_singleEvt_comparison(self) -> Union[dict, None]:
        """
        Enable to get, for a single event, the comparison operator

        Returns:
            Union[dict, None]: A list of comparison operator.
                None if there is several event.
        """
        res = None
        if len(self.elements_event) == 1:
            res = self.elements_event[0].get_comparison()
        else:
            #  On verifie que les evenement dans la liste ne sont pas identique,
            # i-e ils différent seulement par les chemins de fichiers.
            evt0 = self.elements_event[0]
            all_the_same = True
            for evt in self.elements_event:
                if evt != evt0:
                    all_the_same = False
            if all_the_same:
                res = self.elements_event[0].get_comparison()
        return res

    def get_comparison(self) -> Union[dict, None]:
        dout = dict()
        for event in self.elements_event:
            field = event.field.name
            comparison = event.get_comparison()
            if field is not None and field not in dout:
                dout[field] = comparison
            elif field in dout and dout[field] != comparison:
                LOGGER.error(
                    f" Current  {dout[field]} is different of new one {comparison}. "
                    "Don't know what to do in this case. "
                )
        return dout

    def get_cover_period(self) -> xr.DataArray:
        return self.elements_event[0].get_cover_period()

    def is_bertrand(self) -> bool:
        """Check if an event of the list is Bertrand Kind."""
        return all(
            isinstance(event, EventBertrandComposite) for event in self.elements_event
        )

    def update_selection(
        self,
        sel: dict = dict(),
        slice: dict = dict(),
        isel: dict = dict(),
        islice: dict = dict(),
    ):
        for element in self.elements_event:
            element.update_selection(sel=sel, slice=slice, isel=isel, islice=islice)

    def get_grid_name(self) -> str:
        """We here make the hypothesis that all file are based on the same grid"""
        return self.elements_event[0].field.grid_name

    def _compute_risk(self) -> xr.Dataset:
        """ Fonction qui calcul un niveau de risque.
        Cette fonction combine différents évènements.
        Le dataset de sortie n'est par contre pas généré. Seul le risque est ici fait.
        """
        output_ds = xr.Dataset()
        # 1. computing all events and retrieving results for output
        events = []
        for i, event in enumerate(self.elements_event):
            events.append(event.compute())
            tmp_ds = event.values_ds.expand_dims(dim="evt").assign_coords(evt=[i])
            output_ds = xr.merge([output_ds, tmp_ds])
        # 2. combining all events using logical operators
        risk_da = LogicalOperator.apply(self.logical_op_list, events)
        self._spatial_risk_da = risk_da * self.mask_da
        # 3. aggregating if necessary
        aggregation = self.aggregation
        if aggregation is not None:
            agg_handler = Aggregator(self._spatial_risk_da)
            # Ajout pour avoir la densite de l'evenement combine en sortie
            if "density" in self.compute_list:
                output_ds["risk_density"] = agg_handler.compute("density")

            if "summary" in self.compute_list:
                agg_handler_time = Aggregator(
                    risk_da, aggregate_dim=self.time_dimension
                )
                max_risk_da = agg_handler_time.compute("max") * self.mask_da
                agg_handler_space = Aggregator(max_risk_da)
                output_ds["risk_summarized_density"] = agg_handler_space.compute(
                    "density"
                )

            # On calcule maintenant l'occurrence du risque
            aggregation_kwargs = dict(aggregation.kwargs or {})
            aggregation_algo = aggregation.method
            risk_da = agg_handler.compute(aggregation_algo, **aggregation_kwargs)

        output_ds["occurrence"] = risk_da
        # On check que les variables sont bien presentes.
        if hasattr(self.mask_da, "label"):
            output_ds["areaName"] = self.mask_da["label"]
        if hasattr(self.mask_da, "areaName"):
            output_ds["areaName"] = self.mask_da["areaName"]
        else:
            output_ds["areaName"] = (
                "id",
                ["unknown" for _ in range(self.mask_da.id.size)],
            )
        if hasattr(self.mask_da, "type"):
            output_ds["areaType"] = self.mask_da["type"]
        if hasattr(self.mask_da, "areaType"):
            output_ds["areaType"] = self.mask_da["areaType"]
        else:
            output_ds["areaType"] = (
                "id",
                ["unknown" for _ in range(self.mask_da.id.size)],
            )
        return output_ds.squeeze("tmp")
