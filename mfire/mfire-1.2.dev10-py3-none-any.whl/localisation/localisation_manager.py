from __future__ import annotations

import os
import re
import numpy as np
import xarray as xr
from typing import Tuple

from mfire.localisation.spatial_localisation import (
    SpatialLocalisation,
    LocalisationError,
)
from mfire.localisation.temporal_localisation import TemporalLocalisation
from mfire.localisation.table import SummarizedTable
from mfire.settings import get_logger, Settings
from mfire.utils.date import Period
from mfire.utils import JsonFile
from mfire.composite.components import RiskComponentComposite


# Logging
LOGGER = get_logger(name="localisation", bind="localisation")


class Localisation:
    """
    Classe permettant de gérer la localisation.
    """

    _repo = os.path.join(Settings().cache_dirname, "Localisation")
    _nc_spatial_table = "spatial_table.nc"
    _json_compo = "component.json"
    _json_loca = "LocalisationInfo.json"

    def __init__(
        self,
        component: RiskComponentComposite,
        risk_level: int,
        geo_id: str,
        period: set,
        reload: bool = False,
        repo: str = None,
    ):
        """
        Args:
            component (RiskComponentComposite): [description]
            risk_level ([type]): [description]
            geo_id ([type]): [description]
            period ([type]): [description]
        """
        self.component = component
        self.risk_level = risk_level
        self.geo_id = geo_id
        self.period = period
        self.full_risk = xr.Dataset()
        if not reload:
            self._compute_summarized_handler()
            if Settings().save_cache:
                LOGGER.warning(f"Saving Localisation for training staff {self._repo}")
                self.auto_save()
        else:
            self._reload(repo)

    def _reload(self, repo=None):
        """
        Permet de recharger a partir d'un dossier.
        Si le dossier n'est pas spécifié on recharge à partir du dossier de base.
        """
        if repo is None:
            rep = self._repo
        else:
            rep = repo
        LOGGER.info(f"Reading from {rep + self._nc_spatial_table}")
        self.spatial_table = xr.open_dataset(
            os.path.join(rep, self._nc_spatial_table)
        ).sel(risk_level=self.risk_level)
        self.spatial_table = self.spatial_table.expand_dims("risk_level")
        self.summarized_handler = SummarizedTable.load(rep)

    def _compute_summarized_handler(self):
        """
        Define the summarized_handler
        """
        self.perform_spatial_localisation()
        # On va introduire un test

        if "risk_density" in self.spatial_table:
            LOGGER.debug(
                f"On va changer les occurences {self.spatial_table['risk_density']}"
            )
            LOGGER.debug(f"Les noms sont {self.spatial_table['risk_density'].areaName}")
            occurence = self.spatial_table["occurrence"].squeeze(
                "risk_level"
            ) * self.mask_occurence(
                self.spatial_table["risk_density"].squeeze("risk_level")
            )
        else:
            LOGGER.debug("Nothing could be done for density")
            occurence = self.spatial_table["occurrence"].squeeze("risk_level")

        occurence = occurence.dropna("id")
        if occurence.size == 0:
            raise LocalisationError("Spatialy localised occurrence is empty.")

        # On va maintenant faire l'aggregation temporelle
        try:
            tempo_handler = TemporalLocalisation(
                occurence, area_dimension="id", time_dimension="valid_time",
            )
            table_3p = (
                tempo_handler.new_division()
            )  # Permet de prendre des pas de temps
            # Pour l'instant n'est pas utilisee par le summarizer.
            period = Period(
                self.spatial_table.valid_time.min().values,
                self.spatial_table.valid_time.max().values,
            )
            request_time = self.component.production_datetime
            self.summarized_handler = SummarizedTable(
                table_3p,
                spatial_ingredient=self.spatial_ingredient,
                request_time=request_time,
                full_period=period,
            )
        except Exception as excpt:
            raise LocalisationError("Failed to summarize localisation") from excpt

    @staticmethod
    def mask_occurence(density: xr.DataArray) -> xr.DataArray:
        """Cette fonction permet de changer les masquer les occurences faibles
        devant celles plus importantes.

        Lorsque la densité maximum est supérieur à 30%, on va masquer les
        densités inférieur à densité_max /5.

        Pour ce faire, on va renvoyer un tableau de 1 et de 0 (à multiplier
        avec le tableau d'occurence).

        Il faut néanmoins que la densité existe ...

        Args:
            density (xr.DataArray): La résumé de la densité
        """
        res = xr.ones_like(density)
        if density.max() > 0.3:
            seuil = density.max() / 5
            res = density > seuil
        else:
            seuil = density.max() / 20
            res = density > seuil
        return res

    def get_unique_name(self):
        """
        Retourne la clé permettant l'identification du template
        """
        return self.summarized_handler.get_unique_name()

    def get_unique_table(self):
        """
        Retourne le tableau résumé
        """
        return self.summarized_handler.get_unique_table()

    def get_summarized_info(self):
        """Retourne un tuple avec le tableau et le nom unique

        Returns:
            (tuple): (tableau_unique, nom_unique)
        """
        return (
            self.summarized_handler.get_unique_table(),
            self.summarized_handler.get_unique_name(),
        )

    def get_spatial_table(self):
        """
        Retourne le tableau heure par heure pour chacune des zones.
        """
        return self.spatial_table

    def get_localised_area(self):
        """
        Retourne les zones localisées
        """
        return self.spatial_ingredient.localised_area

    def get_full_risk(self):
        """
        Return le risk non localisé.
        Si on a défini le localisation manager sans passer par la localisation
        il n'existe pas.
        """
        return self.full_risk

    @staticmethod
    def extract_critical_values(da: xr.DataArray, operator: str) -> Tuple[float, str]:
        """
        Get the most critical values over time

        Args:
            da (xr.DataArray): The dataArray to look at
            operator (str): The comparison operator

        Raises:
            ValueError: If the comparison operator is not among
            [>,<,>=,<=,"inf","sup","supegal","infegal"]

        Returns:
            (float, str): The critical values as well as the impacted area.
        """

        if operator in [">", "sup", ">=", "supegal"]:
            value = float(da.max(["valid_time", "id"]).values)
            area_id = str(da.isel(id=da.max("valid_time").argmax("id"))["id"].values[0])
            date = da.isel(valid_time=da.max("id").argmax("valid_time"))[
                "valid_time"
            ].values[0]
        elif operator in ["<", "inf", "<=", "infegal"]:
            value = float(da.min(["valid_time", "id"]).values)
            area_id = str(da.isel(id=da.min("valid_time").argmin("id"))["id"].values[0])
            date = da.isel(valid_time=da.min("id").argmin("valid_time"))[
                "valid_time"
            ].values[0]

        else:
            raise ValueError(
                "Operator is not understood when trying "
                "to find the critical representative_values."
            )
        return (value, area_id, date)

    def get_level_type(self, risk_level=None):
        """
        risk_level : Le niveau pour lequel on veut le type.

        Retourne le type de risque (pour les templates).
        Pour cela se base sur les variables rencontrées au niveau donné.
        On ne prend pas en comptes les variables à d'autres niveaux.
        """
        res = "GENERIC"
        if risk_level is None:
            risk_level = self.spatial_table.risk_level

            # Atttention le level doit existé.
        level = self.component.select_risk_level(level=risk_level)
        dict_comparison = level[0].get_comparison()
        l_prefix = []

        for variable in dict_comparison.keys():
            prefix = variable.split("_")[0]
            pattern = r"[0-9]"
            l_prefix.append(re.sub(pattern, "", prefix))

        variable_set = set(l_prefix)

        if len(variable_set) == 1:
            variable = list(variable_set)[0]
            if variable in ["PRECIP", "EAU"]:
                res = "PRECIP"
            elif variable in ["NEIPOT"]:
                res = "SNOW"
        return res

    def get_critical_values(self):
        """
        Retourne les valeurs critiques
        """
        dout = {}
        if not hasattr(self, "spatial_table"):
            LOGGER.warning("There is no spatial table, therefore no critical values")
            return dout
        risk_level = self.spatial_table.risk_level
        dict_comparison = self.component.get_comparison(level=risk_level.values)
        # Pour chaque evenement on va ensuite identifier les choses.
        for evt in self.spatial_table.evt:
            variable = self.spatial_table.weatherVarName.sel(evt=evt).values[0]
            if variable not in dict_comparison:
                if variable != "":
                    LOGGER.warning(
                        f"Variable '{variable}' not in comparison dictionnary. "
                        f"Key among {set(dict_comparison)} expected."
                    )
                continue
            dtmp = {}

            # Il faut vérifier que l'évenement ai bien une condition sur  la montagne.
            if (
                "rep_value_mountain" in self.spatial_table
                and "mountain" in dict_comparison[variable]
                and not np.isnan(
                    self.spatial_table.sel(evt=evt)["rep_value_mountain"]
                ).all()
            ):
                value, area, date = self.extract_critical_values(
                    self.spatial_table.sel(evt=evt)["rep_value_mountain"],
                    dict_comparison[variable]["mountain"]["comparison_op"],
                )
                dtmp["mountain"] = {
                    "id": area,
                    "operator": dict_comparison[variable]["mountain"]["comparison_op"],
                    "threshold": dict_comparison[variable]["mountain"]["threshold"],
                    "next_critical": dict_comparison[variable]["mountain"].get(
                        "next_critical", None
                    ),
                    "value": value,
                    "units": self.spatial_table.sel(evt=evt)[
                        "rep_value_mountain"
                    ].attrs.get("units", None),
                    "critical_hour": date,
                }
            if (
                "rep_value_plain" in self.spatial_table
                and "plain" in dict_comparison[variable]
                and not np.isnan(
                    self.spatial_table.sel(evt=evt)["rep_value_plain"]
                ).all()
            ):
                value, area, date = self.extract_critical_values(
                    self.spatial_table.sel(evt=evt)["rep_value_plain"],
                    dict_comparison[variable]["plain"]["comparison_op"],
                )

                dtmp["plain"] = {
                    "id": area,
                    "operator": dict_comparison[variable]["plain"]["comparison_op"],
                    "threshold": dict_comparison[variable]["plain"]["threshold"],
                    "next_critical": dict_comparison[variable]["plain"].get(
                        "next_critical", None
                    ),
                    "value": value,
                    "units": self.spatial_table.sel(evt=evt)[
                        "rep_value_plain"
                    ].attrs.get("units", None),
                    "critical_hour": date,
                }

            # Faire attention au fait que la variable ne doit pas etre deja dans le
            # dictionnaire
            if bool(dtmp) and variable not in dout.keys():
                dout[variable] = dtmp
            elif bool(dtmp):
                LOGGER.warning("Case not yet implemented. Don't know which case it is.")

        return dout

    def perform_spatial_localisation(self):
        """
        This function is responsible of the spatial aggregation.

        Args:
            risk_level ([type]): [description]
            geo_id ([type]): [description]
            period ([type]): [description]
        """
        spatial_handler = SpatialLocalisation(self.component, geo_id=self.geo_id)
        self.spatial_ingredient = spatial_handler.localise(
            risk_level=self.risk_level, risk_period=self.period
        )
        self.full_risk = spatial_handler.full_risk

        self.spatial_table = spatial_handler.compute_information_on_area(
            risk_level=self.risk_level, da_area=self.spatial_ingredient.localised_area
        )

    def auto_save(self, **kwargs):
        """
        Permet la sauvegarde des informations de l'objets.
        Dans kwargs on peut avoir "repo" qui correspond au repertoire
        dans lequel on va sauver.
        """
        os.makedirs(kwargs.get("repo", self._repo), exist_ok=True)
        self.spatial_table.to_netcdf(
            kwargs.get("repo", self._repo) + self._nc_spatial_table
        )
        self.summarized_handler.auto_save(kwargs.get("repo", self._repo))
        JsonFile(kwargs.get("repo", self._repo) + self._json_compo).dump(self.component)
        LocaInfo = {}
        LocaInfo["geo_id"] = self.geo_id
        LocaInfo["period"] = list(np.datetime_as_string(list(self.period)))
        LocaInfo["risk_level"] = self.risk_level
        JsonFile(kwargs.get("repo", self._repo) + self._json_loca).dump(LocaInfo)

    @classmethod
    def load(cls, **kwargs):
        """
        Pour l'instant on ne prevoit d'en sauver qu'un seul...
        """
        component = RiskComponentComposite(
            **JsonFile(
                os.path.join(kwargs.get("repo", cls._repo), cls._json_compo)
            ).load()
        )

        loca_info = JsonFile(
            os.path.join(kwargs.get("repo", cls._repo), cls._json_loca)
        ).load()
        loca_info["period"] = [np.datetime64(x) for x in loca_info["period"]]
        loca_info["repo"] = kwargs.get("repo", cls._repo)
        return cls(component, **loca_info, reload=True)

    @classmethod
    def define_without_spatial(
        cls, component: RiskComponentComposite, table: xr.DataArray
    ) -> Localisation:
        """Use it only for test.
        Should be obsolete quickly (because of spatial information)

        Args:
            component (RiskComponentComposite): RiskComponentComposite to use
            table (xr.DataArray): Given table

        Returns:
            Localisation: new object
        """
        obj = super().__new__(cls)
        obj.component = component
        obj.risk_level = -99
        obj.geo_id = "NoArea"
        obj.period = [np.datetime64("2020021206")]
        obj.summarized_handler = SummarizedTable(
            table,
            request_time="20200212T06",
            full_period=Period("20200212T00", "20200212T20"),
        )
        return obj


if __name__ == "__main__":
    Loca_Handler = Localisation.load()
    Loca_Handler.auto_save(repo="/scratch/labia/chabotv/tmp/test_save/")
    loca_bis = Localisation.load(repo="/scratch/labia/chabotv/tmp/test_save/")
#   print(loca_handler.get_unique_table())
#   print("Valeurs critiques :",loca_bis.get_critical_values())
#   print(loca_bis.get_unique_table())
