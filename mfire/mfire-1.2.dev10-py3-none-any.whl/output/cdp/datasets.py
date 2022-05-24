"""
Module gérant les données calculées par la librairie
"""
from __future__ import annotations

from typing import List, Optional

import xarray as xr
from pydantic import BaseModel, validator

from mfire.settings import get_logger
from mfire.utils.date import Datetime
from mfire.composite.components import RiskComponentComposite

LOGGER = get_logger(name="cdp.datasets.mod", bind="cdp.datesets")


class CDPParam(BaseModel):
    """Création d'un objet Param contenant la configuration du Param

    Args:
        baseModel : modèle de la librairie pydantic

    Returns:
        baseModel : objet Param
    """

    Name: str
    Stepsize: Optional[int]


class CDPValueParam(BaseModel):
    """Création d'un objet ValuesWithParam contenant la configuration du ValuesWithParam

    Args:
        baseModel : modèle de la librairie pydantic

    Returns:
        baseModel : objet ValuesWithParam
    """

    ValueType: str
    Unit: str
    Value: float
    Param: Optional[CDPParam]

    @classmethod
    def from_composite(
        cls, evt_only_ds: xr.Dataset, stepsize: int = None
    ) -> List[CDPValueParam]:
        """Fonction permettant à partir d'un dataset (pour un niveau et une
        zone donnée) d'extraire les informations extrayable (vis à vis des
        specs) pour le CDP.

        Args:
            ds (xr.dataset): Dataset with only 'evt' as dimension.
            stepsize (int) : model stepsize pour ce paramètre à cette échéance.
        """
        # On va maintenant vérifier que dst n'a que evt
        if set(evt_only_ds.dims) != {"evt"}:
            raise ValueError(
                "In CDPValueParam.from_composite we expect ds to have only "
                f"'evt' as dimension. However we get {evt_only_ds.dims}."
            )

        # On commence par virer les évènement nul
        # Ces évènements sont possibles car le dataset comprend, pour chaque niveau,
        # autant d'évènement qu'il y a pour le niveau contenant le plus d'évènement.
        my_ds = evt_only_ds.dropna("evt", how="all")

        # On va regarder les variables vide
        # Il est possible que certaines varaibles soient vide
        # (si par ex. à un niveau on a pas la définition de cette variable)
        empty = {var for var in my_ds if my_ds[var].count() == 0}
        # Parmis les variables certaines ne doivent pas apparaitre dans la sortie
        useless = {
            "areaName",
            "areaType",
            "units",
            "occurrence_event",
            "weatherVarName",
            "risk_density",
            "risk_summarized_density",
        }
        # On recupere le set de variable pouvant apparaitre dans la sortie
        variables = sorted(set(my_ds.data_vars).difference(empty).difference(useless))
        values_list = []
        for var in variables:
            if my_ds[var].size > 1:
                LOGGER.debug(
                    f"Too many information to go the CDP for this variable {var}",
                    var=var,
                    func="CDPValueParam.from_composite",
                )
                continue

            if var in (
                "occurrence",
                "density",
                "summarized_density",
                "risk_density",
                "risk_summarized_density",
            ):
                unit = "1"
                param = None

            else:
                # Cas des valeurs sur les plaines/montagnes etc...
                # Les retours sont effectués dans les unités qui
                # nous ont été spécifiées pour le seuil.
                unit = "unknown"
                if "units" in my_ds:
                    unit = my_ds["units"].values.tolist()[0]
                param = CDPParam(
                    Name=my_ds["weatherVarName"].values.tolist()[0], Stepsize=stepsize,
                )

            values_list.append(
                cls(
                    ValueType=var,
                    Value=round(float(my_ds[var]), 2),
                    Unit=unit,
                    Param=param,
                )
            )

        return values_list


class CDPSummary(BaseModel):
    """Création d'un objet ShortSummary contenant la configuration du ShortSummary

    Args:
        baseModel : modèle de la librairie pydantic

    Returns:
        baseModel : objet ShortSummary
    """

    ValidityDate: Optional[Datetime]
    Level: int
    Values: List[CDPValueParam]

    @validator("ValidityDate", pre=True)
    def init_dates(cls, v: str) -> Datetime:
        if v is None:
            return v
        return Datetime(v)

    @classmethod
    def from_composite(
        cls, component: RiskComponentComposite, geo_id: str
    ) -> CDPSummary:
        """Returns a Short Summary (not on every steps but on the whole period)

        Args:
            RiskComponentComposite to summarize.
            geo_id (str): Geographical's id of the area to summarize.

        Raises:
            excpt: [description]
            ValueError: [description]
            e: [description]

        Returns:
            CDPSummary: CDPSummary of the whole component.

        History :
           23/02/2021 : Adding values of first level even if activated level is 0.
           June 2021 :  'risk_density' is replaced by 'density'.
        """
        tmp_ds = component.risks_ds.sel(id=geo_id)
        time_dim = component.time_dimension
        final_level_da = component.final_risk_da.sel(id=geo_id)
        level = final_level_da.max()

        # Permet de selectionner le plus petit niveau et ce même si aucun niveau
        # n'est activé.
        if level > 0:
            summary_level = level
            dmax, _ = xr.align(
                tmp_ds.sel(risk_level=summary_level),
                final_level_da.where(final_level_da == summary_level, drop=True),
            )
        else:
            summary_level = tmp_ds.risk_level.min()
            dmax = tmp_ds.sel(risk_level=summary_level)

        # On va differencier les varaible pour savoir quoi retrourner
        # De base on prend la moyenne pour toutes les variables
        level_ds = dmax.mean(time_dim)
        # On va changer pour certaines variables
        for var in dmax.data_vars:
            if "max" in var:
                level_ds[var] = dmax[var].max(time_dim)
            if "min" in var:
                level_ds[var] = dmax[var].min(time_dim)

        # On va faire quelque chose de très spécifique
        # pour les valeurs représentatives :
        # prendre la plus critique
        risk_level = component.select_risk_level(level=summary_level)
        dict_comparison = risk_level[0].get_singleEvt_comparison()
        if dict_comparison is not None:
            for key in dict_comparison:
                rep_key = "rep_value_" + key
                if rep_key in level_ds and dict_comparison.get("category") in (
                    "quantitative",
                    "restrictedQuantitative",
                ):
                    level_ds[rep_key] = component.get_critical_value(
                        dmax[rep_key], dict_comparison[key]["comparison_op"],
                    )

        LOGGER.debug(f"The comparison dictionnary is {dict_comparison}")

        for var in ("summarized_density", "risk_summarized_density"):
            if var in dmax.data_vars:
                level_ds["density"] = dmax[var]
                level_ds = level_ds.drop_vars(var)

        LOGGER.debug(
            f"Variables de sortie {level_ds.data_vars}",
            func="CDPSummary.from_composite",
            geo_id=geo_id,
        )
        if "units" in dmax:
            level_ds["units"] = dmax["units"]
        level_ds["weatherVarName"] = dmax["weatherVarName"]
        # On s'assure que l'occurrence est bien True
        if level > 0:
            level_ds["occurrence"] = True
        return CDPSummary(Level=level, Values=CDPValueParam.from_composite(level_ds))

    @classmethod
    def long_from_composite(
        cls, component: RiskComponentComposite, geo_id: str
    ) -> List[CDPSummary]:
        """Returns a summary of all computed values at every steps of the given
        component.

        Args:
            component (RiskComponentComposite): RiskComponentComposite to summarize.
            geo_id (str): Geographical's id of the area to summarize.

        Returns:
            List[CDPSummary]: List of CDPSummary for each step.

        History :
           23/02/2021 : Adding values of first level even if activated level is 0
            (ie no risk is activated).
        """
        tmp_ds = component.risks_ds.sel(id=geo_id).drop_vars(
            ("summarized_density", "risk_summarized_density"), errors="ignore"
        )
        time_dim = component.time_dimension
        stepsize_da = component.get_stepsize(tmp_ds).stepsize
        data_list = []
        for step in tmp_ds[time_dim]:
            level = component.final_risk_da.sel({"id": geo_id, time_dim: step}).values
            summary_level = level
            if level == 0:
                summary_level = tmp_ds.risk_level.min().values

            data_list.append(
                cls(
                    ValidityDate=step,
                    Level=level,
                    Values=CDPValueParam.from_composite(
                        tmp_ds.sel({time_dim: step, "risk_level": summary_level}),
                        stepsize=int(stepsize_da.sel({time_dim: step}).values),
                    ),
                )
            )
        return data_list


class CDPDataset(BaseModel):
    """Création d'un objet DataSet contenant la configuration du Dataset

    Args:
        baseModel : modèle de la librairie pydantic

    Returns:
        baseModel : objet DataSet
    """

    ShortSummary: CDPSummary
    Summary: List[CDPSummary]

    @classmethod
    def from_composite(
        cls, component: RiskComponentComposite, geo_id: str
    ) -> CDPDataset:
        if component.is_risks_empty():
            return CDPDataset(ShortSummary=CDPSummary(Level=0, Values=[]), Summary=[])

        return CDPDataset(
            ShortSummary=CDPSummary.from_composite(component=component, geo_id=geo_id),
            Summary=CDPSummary.long_from_composite(component=component, geo_id=geo_id),
        )
