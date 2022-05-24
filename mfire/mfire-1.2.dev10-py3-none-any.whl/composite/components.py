"""
    Module d'interprétation de la configuration métronome
"""
import os
import json

import numpy as np
import xarray as xr
from enum import Enum
from pydantic import validator
from pydantic import Field as PydanticField
from typing import List, Optional, Union

from mfire.settings import get_logger
from mfire.utils.date import Datetime
from mfire.utils.xr_utils import Loader, special_merge, replace_middle
from mfire.composite.periods import Period
from mfire.composite.operators import ComparisonOperator
from mfire.composite.base import BaseComposite
from mfire.composite.levels import LevelComposite
from mfire.composite.weather import WeatherComposite

# Logging
LOGGER = get_logger(name="components.mod", bind="components")


def update_next_critical(dico1: dict, dico2: dict, variable: str, kind: str = "plain"):
    """
    Cette fonction update le dictionnaire qu'on envoit ensuite vers le module de texte.
    Il permet de rajouter une info (next_critical) à savoir l'information
    sur le seuil du niveau supérieur.
    Si une valeur next_critical existe, on regarde si la valeur de ce niveau là est
    moins critique.

    Args:
        dico1 (dict): Le dictionnaire du niveau de risque à mettre à jour
        dico2 (dict): Le dictionnaire d'un niveau de risque supérieur
        variable (str): La variable qui nous intéresse
        kind (str, optional): Le type ("plain"/"mountain"). Defaults to "plain".
    """
    var1 = dico1[variable]
    var2 = dico2[variable]

    if kind not in var2:
        return None

    operator1 = ComparisonOperator(var1[kind]["comparison_op"])
    operator2 = ComparisonOperator(var2[kind]["comparison_op"])

    if operator1 in list(ComparisonOperator)[:4] and operator1 == operator2:
        # Dans ce cas, on va vérifier que la valeur est plus
        # critique que celle de base et moins critique que la suivante
        this_critical = float(var1[kind].get("threshold"))
        next_critical = float(var2[kind].get("threshold"))
        # On verifie que la valeur est plus critique que celle actuelle
        if operator1(next_critical, this_critical):
            LOGGER.debug("The next critical value is more critical")
            if "next_critical" in var1[kind]:
                LOGGER.debug("A critical value is already set")
                current_critical = float(var1[kind].get("next_critical"))
                # S'il existe deja une valeur next_critical.
                # Si la nouvelle valeur critique est moins critique.
                if operator1(next_critical, current_critical):
                    dico1[variable][kind]["next_critical"] = next_critical
            else:
                dico1[variable][kind]["next_critical"] = next_critical


class TypeComponent(str, Enum):
    """Création d'une classe d'énumération contenant le type
    de componant
    """

    RISK = "risk"
    TEXT = "text"


class AbstractComponentComposite(BaseComposite):
    """ Cette classe Abstraite permet de mettre en place le design pattern
    "ComponentComposite" qui permettra de faire des composants de type texte
    ou risque

    Inheritance : BaseComposite
    """

    period: Period
    id: str
    type: TypeComponent
    name: str
    customer: Optional[str]
    customer_name: Optional[str]
    geos: Optional[List[str]]
    production_id: str
    production_name: str
    production_datetime: Datetime
    configuration_datetime: Optional[Datetime] = Datetime()
    time_dimension: Optional[str] = "valid_time"

    @validator("production_datetime", "configuration_datetime", pre=True)
    def init_dates(cls, date_config: str) -> Datetime:
        return Datetime(date_config)


class TextComponentComposite(AbstractComponentComposite):
    """ Cette classe permet de créer un objet component de type texte

    Inheritance : AbstractComponentComposite

    Returns:
        baseModel : objet Component
    """

    type: TypeComponent = PydanticField(TypeComponent.TEXT, const=True)
    product_comment: bool
    weathers: List[WeatherComposite]
    _weathers_ds: xr.Dataset = xr.Dataset()

    def _compute(self) -> xr.Dataset:
        weathers_ds = xr.merge([weather.compute() for weather in self.weathers])
        self._weathers_ds = weathers_ds
        return weathers_ds

    @property
    def weathers_ds(self) -> xr.Dataset:
        return self._weathers_ds

    def get_geo_name(self, geo_id: str) -> str:
        return str(self.weathers_ds.sel(id=geo_id)["areaName"].values)


class RiskComponentComposite(AbstractComponentComposite):
    """Création d'un objet Component contenant la configuration
    de la tâche de production promethee

    Args:
        baseModel : modèle de la librairie pydantic

    Returns:
        baseModel : objet Component
    """

    type: TypeComponent = PydanticField(TypeComponent.RISK, const=True)
    levels: List[LevelComposite]
    hazard: str
    hazard_name: str
    product_comment: bool
    other_names: Optional[Union[str, List[str]]]
    _risks_ds: xr.Dataset = xr.Dataset()
    _final_risk_da: xr.DataArray = xr.DataArray()

    @property
    def risks_ds(self) -> xr.Dataset:
        return self._risks_ds

    @property
    def final_risk_da(self) -> xr.DataArray:
        return self._final_risk_da

    @property
    def _cached_attrs(self) -> dict:
        return {
            "data": Loader,
            "risks_ds": Loader,
            "final_risk_da": Loader,
        }

    def _compute(self) -> xr.Dataset:
        if self.hazard is not None or self.production_id is not None:
            LOGGER.debug(
                "Computing hazard",
                hazard=self.hazard,
                bulletin=self.production_id,
                func="Component.compute",
            )

        risks_ds = xr.Dataset()
        for level in self.levels:
            aggregate_dim = ["latitude", "longitude"]
            level_risk_da = level.compute()
            level_risk_da.attrs["level"] = int(level.level)
            for dim in aggregate_dim:
                if hasattr(level_risk_da, dim):
                    level_risk_da = level_risk_da.reset_coords(dim, drop=True)
            level_risk_da = level_risk_da.expand_dims(dim="risk_level").assign_coords(
                risk_level=[int(level.level)]
            )
            try:
                # Faire quelque chose de specifique pour la densite resumee...
                risks_ds = special_merge(risks_ds, level_risk_da)
            except Exception as excpt:
                LOGGER.exception(
                    "Error in merging dataset",
                    hazard=self.hazard,
                    bulletin=self.production_id,
                    func="Component.compute",
                    exc_info=True,
                )
                raise ValueError from excpt

        for var in ("areaType", "areaName"):
            if var in risks_ds.data_vars:
                risks_ds[var] = risks_ds[var].isel(risk_level=0)

        self._risks_ds = risks_ds

        # calcul du DataArray qui compile les niveaux de risques atteints
        self._final_risk_da = self.compute_final_risk_level()
        return risks_ds

    def compute_final_risk_level(self) -> xr.DataArray:
        """compute_risk_level : Computes the maximum risk levels out of the
        previously computed self.risks_ds Fait en sorte de lisser un peu le niveau
        de risque (en remplaçant les descente remonté trop brutales). Utilise
        la fonction replace_middle.

        Returns:
            xarray.DataArray (time_dimension, id) -- Maximum risk level DataArray
        """
        final_risk_da = xr.DataArray(
            dims=(self.time_dimension, "id"),
            coords={self.time_dimension: [], "id": []},
        )
        if not self.is_risks_empty():
            # pour gagner de la memoire, remplacement des variables
            # précédentes par un unique pipe.
            final_risk_da = (
                (self.risks_ds["occurrence"] * self.risks_ds.risk_level)
                .max(dim="risk_level", skipna=True)
                .rolling({self.time_dimension: 3}, center=True, min_periods=1)
                .reduce(replace_middle)
            )
        else:
            LOGGER.warning(
                "Computed risks are empty. "
                "self.final_risk_da kept as an empty xr.DataArray.",
                func="compute_final_risk_level",
            )
        return final_risk_da

    def load_risk(self, ds: xr.Dataset):
        """load_risk
        This function enable to initialise an Hazard with already computed hazard

        Args:
            ds (xr.Dataset): The hazard
        """
        self._risks_ds = ds
        self._final_risk_da = self.compute_final_risk_level()

    def select_risk_level(self, level: int = 1) -> List[LevelComposite]:
        """select_risk_level

        Retourne une liste de Levels.
        Les éléments de cette liste correspondent tous au niveau demandé
        (plusieurs définition sont possible quand on utilise différents fichiers).

        Args:
            level (int, optional): Le niveau de risque requis. Defaults to 1.

        Returns:
            [list]: Liste de Levels.
        """
        res_list = [lvl for lvl in self.levels if lvl.level == level]
        if len(res_list) == 0:
            level_values = {lvl.level for lvl in self.levels}
            raise ValueError(
                f"Level '{level}' not found. Possible values : {level_values}"
            )
        return res_list

    def get_comparison(self, level: int = 1) -> dict:
        """
        On va chercher le dictionnaire de comparaison.

        Args:
            level (int, optional): [description]. Defaults to 1.
        """
        this_level = self.select_risk_level(level=level)
        levels = sorted({lvl.level for lvl in self.levels if lvl.level > level})

        # On recupere le dictionnaire de comparaison du niveau qui nous intéresse
        dict_comparison = this_level[0].get_comparison()

        # Ensuite on va boucler sur chacune des variables et
        # voir si on trouve des variables identiques à la notre
        for variable in dict_comparison:
            for elt in levels:
                other_level = self.select_risk_level(level=elt)
                d2_comparison = other_level[0].get_comparison()
                if variable in dict_comparison and variable in d2_comparison:
                    if "plain" in dict_comparison[variable]:
                        update_next_critical(
                            dict_comparison,
                            d2_comparison,
                            variable=variable,
                            kind="plain",
                        )
                    if "mountain" in dict_comparison[variable]:
                        update_next_critical(
                            dict_comparison,
                            d2_comparison,
                            variable=variable,
                            kind="mountain",
                        )
        return dict_comparison

    def get_threshold(self, risk_level: int, idx: int, var: str) -> int:
        """Method which retrieves the threshold of the given element of the given
        level, on the given var.
        ! specific to the monozone comment module

        Args:
            risk_level (int): Risk_level
            idx (int): element index
            var (str): 'plain' or 'mountain'

        Returns:
            int: expected threshold value.
        """
        return next(
            (
                level.elements_event[idx].dict()[var]["threshold"]
                for level in self.levels
                if level.level == risk_level
            ),
            -9999,  # ! c'est pas top les magic numbers
        )

    def is_risks_empty(self) -> bool:
        return not bool(self.risks_ds)

    def convert_risk_level_to_potential_occurrence(
        self, da: xr.DataArray
    ) -> xr.DataArray:
        """Method used to load specific occurrence dataarray in the tests
        ! used in tests only

        Args:
            da (xr.DataArray): dataarray to use

        Returns:
            xr.DataArray: Equivalent occurence dataarray
        """
        levels = set(np.unique(da.values)).difference({0})
        ds = xr.merge(
            [
                (da == level)
                .expand_dims("risk_level")
                .assign_coords(risk_level=[level])
                for level in levels
            ]
        )
        return ds.rename({da.name: "occurrence"})["occurrence"]

    def get_period_for_level(
        self, my_id: str, level: int, coord: str = None
    ) -> xr.DataArray:
        """
        get_period_for_level Return the period for which a given level is activated

        The period is either the time_dimension (in this module)
        or any other coordinate (indexed with the time_dimension)

        Args:
            my_id ([str]): An information for the area selection
            level ([int]): An integer telling which is the level of interest
            coord ([type], optional): The coordinate of interest.
                Defaults to None (so self.time_dimension)

        Returns:
            [xr.DataArray]: The coordinate selected for the given period
        """

        if coord is None:
            coord = self.time_dimension
        if self.is_risks_empty():
            return xr.DataArray({coord: [], "id": None})
        risk_area = self.final_risk_da.sel(id=my_id)
        if coord not in self.final_risk_da.coords:
            raise AttributeError(
                f"Dimension {coord} is not part of coordinates. "
                f"Coordinates list is {self.final_risk_da.coords}."
            )
        period = risk_area[risk_area == level][coord]
        return period

    def get_final_max_risk_period(self, my_id: str, coord: str = None) -> xr.DataArray:
        """
        Return, for a given id, the maximum of the risk as well as the step where
        it occured
        ! specific for the monozone
        """
        if coord is None:
            coord = self.time_dimension
        risk_max = self.get_final_risk_max_level(my_id)
        period = self.get_period_for_level(my_id, level=risk_max, coord=coord)
        return period

    def get_period_for_risk(self, my_id: str, coord: str = None) -> xr.DataArray:
        """get_period_with_risk

        Return the period when a risk is raised (i-e risk is not 0)

        Args:
            my_id (str): Id of the area
            coord (str) : [Optional]. Can be any coordinates.
                If None, set to self.time_dimension
        Return:
            [np.ndarray] : The period of risk. The type is the one of
                self.time_dimension
        """
        if coord is None:
            coord = self.time_dimension
        risk_area = self.final_risk_da.sel(id=my_id)
        return risk_area[risk_area != 0][coord]

    def get_final_risk_max_level(self, my_id: str) -> int:
        """get_final_risk_max_level

        Return maximum level for a given area

        Args:
            my_id ([str]): The area id

        Returns:
            [int]: The maximum
        """
        if self.is_risks_empty():
            return 0
        return max(self.final_risk_da.sel(id=my_id).values)

    def get_final_risk_min_level(self, my_id: str) -> int:
        """get_final_risk_max_level

        Return minimum level for a given area
        Args:
            my_id ([str]): The area id
        Returns:
            [int]: The minimum
        """
        if self.is_risks_empty():
            return 0
        return min(self.final_risk_da.sel(id=my_id).values)

    def get_risk_period(self) -> dict:
        """get_risk_period : Permet d'acceder à la période couverte par le risque

        Returns:
            [dictionnaire]: Le dictionnaire comprend la date de début
                et de fin de période;
        """
        if self.is_risks_empty():
            return self.period

        start = self.risks_ds[self.time_dimension].min().values
        stop = self.risks_ds[self.time_dimension].max().values
        if self.time_dimension == "step":
            start += self.risks_ds.time.values
            stop += self.risks_ds.time.values

        return Period(id=self.period.id, start=start, stop=stop,)

    def get_geo_name(self, geo_id: str) -> str:
        if not self.is_risks_empty():
            return str(self.risks_ds.sel(id=geo_id)["areaName"].values)
        return "N.A"

    def get_critical_value(self, da: xr.DataArray, operator: str) -> xr.DataArray:
        """
        Get the most critical values over time

        Args:
            da (xr.DataArray): The dataArray to look at
            operator (str): The comparison operator

        Raises:
            ValueError: If the comparison operator is not among
            [>,<,>=,<=,"inf","sup","supegal","infegal"]

        Returns:
            xr.DataArray: The critical value.
        """
        res = None
        if operator in [">", "sup", ">=", "supegal"]:
            res = da.max(self.time_dimension)
        elif operator in ["<", "inf", "<=", "infegal"]:
            res = da.min(self.time_dimension)
        else:
            raise ValueError(
                "Operator is not understood when trying to find the critical "
                f"representative_values {operator}"
            )
        return res

    def get_stepsize(self, ds_in: xr.Dataset) -> xr.DataArray:
        """Permet de récupérer le pas de temps du modèle (pour chaque
        échéance). La récupération de ce pas de temps permet ensuite de savoir
        "de combien sont écartés les échéances". On suppose que le dernier pas
        de temps (non renseigné) et le même que l'avant dernier.

        Args:
            ds_in (xr.dataset) : Le dataset pour lequel on doit recuperer la stepsize

        ToDo : Bouger cette fonction ailleurs ?
               On risque d'en avoir besoin dans le module de prétraitement...
        """
        time_da = ds_in[self.time_dimension]
        if len(time_da) <= 1:
            # specific case when ds_in is empty or single-stepped.
            LOGGER.warning(
                "Dataset too small to return a correct stepsize.",
                ds_size=len(time_da),
                production_id=self.production_id,
                component_id=self.id,
                component_name=self.name,
                hazard=self.hazard_name,
            )
            data = [1]
            return xr.Dataset(
                {
                    "stepsize": xr.DataArray(
                        data,
                        coords={self.time_dimension: time_da},
                        dims=(self.time_dimension),
                    ).astype(np.int)
                }
            )

        stepsize = (
            time_da.diff(self.time_dimension, label="lower").dt.seconds / 3600
        ).astype(np.int)
        stepsize.name = "stepsize"
        stepsize.attrs["units"] = "hours"
        step_comp = (
            stepsize.broadcast_like(time_da)
            .shift({self.time_dimension: 1})
            .isel({self.time_dimension: -1})
            .expand_dims(self.time_dimension)
        )
        stepout = xr.merge([stepsize, step_comp]).astype(np.int)
        return stepout

    def get_nb_evts(self, risk_levels: List[int]) -> List[int]:
        """ Methode qui renvoie le nombre de d'events dans chaque level passé en
        en argument.
        TODO : A faire disparaitre
        """
        nb_evt_list = []
        for level_value in risk_levels:
            level = next(lvl for lvl in self.levels if lvl.level == level_value)
            nb_evt_list.append(len(level.elements_event))
        return list(set(nb_evt_list))


if __name__ == "__main__":
    file_path = os.path.join(os.path.dirname(__file__), "conf_test.json")
    with open(file_path, "r") as fic:
        data = json.load(fic)
        for id_prod, data_prod in data.items():
            for i, component in enumerate(data_prod["components"]):
                compo = RiskComponentComposite(**component)
