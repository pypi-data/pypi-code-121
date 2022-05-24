import json
import os
from typing import List

import xarray as xr

from mfire.localisation.core_spatial import (
    get_n_area,
    LocalisationError,
)
from mfire.settings import get_logger
from mfire.utils.xr_utils import MaskLoader
from mfire.composite import GeoComposite, LevelComposite, RiskComponentComposite

# Logging
LOGGER = get_logger(name="localisation", bind="localisation")


class SpatialIngredient:
    """
    Object to store several information on spatial localisation.
    Can be saved and loaded.
    """

    def __init__(
        self,
        domain: xr.DataArray,
        full_area_list: xr.DataArray,
        localised_area: xr.DataArray,
        grid_name: str,
    ):
        self.domain = domain
        self.full_area_list = full_area_list
        self.localised_area = localised_area
        self.grid_name = grid_name

    @classmethod
    def load(cls, basename: str):
        """
        Enable to load "SpatialIngredient" from an autosaved.

        Args:
            basename (str): Base du nom de fichier de sauvegarde
                (incluant le path) sans extension

        Returns:
            [type]: [description]
        """
        LOGGER.info(f"In spatial ingredient, basename is '{basename}'")
        with open(basename + ".json", "r") as fp:
            geodict = json.load(fp)
        grid_name = geodict["geos"]["grid_name"]
        mask_a = MaskLoader(
            filename=geodict["geos"]["file"], grid_name=geodict["geos"]["grid_name"]
        ).load()
        domain = mask_a.sel(id=geodict["geos"]["domain_id"])
        full_area_list = mask_a.sel(id=geodict["geos"]["full_list_id"])
        localised_area = MaskLoader(
            filename=geodict["localized"]["file"],
            grid_name=geodict["localized"]["grid_name"],
        ).load()
        return cls(domain, full_area_list, localised_area, grid_name)

    def auto_save(self, basename: str):
        """

        Args:
            basename (str): Base du nom de fichier de sauvegarde
                (incluant le path) sans extension
        """
        LOGGER.info(f"Basename is {basename}")
        fname = basename + ".nc"
        loca_fname = basename + "localized.nc"
        geodict = {}
        geodict["geos"] = {
            "file": fname,
            "grid_name": self.grid_name,
            "domain_id": self.domain.id.values.tolist(),
            "full_list_id": self.full_area_list.id.values.tolist(),
        }
        geodict["localized"] = {
            "file": loca_fname,
            "grid_name": self.grid_name,
        }
        dmerged = xr.concat([self.domain, self.full_area_list], dim="id")
        if os.path.exists(fname):
            os.remove(fname)
        dmerged.to_netcdf(fname)
        if os.path.exists(loca_fname):
            os.remove(loca_fname)
        self.localised_area.to_netcdf(loca_fname)
        with open(basename + ".json", "w") as fp:
            json.dump(geodict, fp)


class SpatialLocalisation:
    """
    This module is responsible of the spatial localisation.

    Usage :
    1. Init
    2. Localise :
        After initialisation, you can use the localise() function.
        This require to know which risk_level is of interest and which
        is the period of the risk.
    3. compute_information_on_area
    """

    def __init__(
        self,
        component: RiskComponentComposite,
        geo_id: str,
        between_authorized: bool = False,
    ):
        """
        Initialisation

        Args:
            component (RiskComponentComposite): The component
            geo_id (str): The id of the area to consider.
               This "id" should be present in the mask configuration.
            between_authorized (bool, optional):
                This say if we let the spatialLoclaisation alogrithm choose the.
                    Defaults to False.

        Others variables initialised :
           - full_risk (DataArray): A 3D (lat/lon/time) DataArray of the current
                level of risk
        """
        self.component = component
        self.geo_id = geo_id
        self.between_authorized = between_authorized

        # On initialise avec une coquille vide
        self.full_risk = xr.DataArray()

    def localise(self, risk_level: int, risk_period: set) -> SpatialIngredient:
        """
        This functionnality enable to localise a risk.

        Args:
            risk_level (int): The risk_level wanted for localisation.
                This level should exist in the configuration.
            risk_period (set): This set indicate which timestep should be used
                for the localisation.

        Raises:
            LocalisationError: If the geo_id is not present in LevelComposite.
            LocalisationError: If the risk is upstream

        Returns:
            [xr.DataArray]: The localisedArea.
        """

        # On recupere une liste de risque pour un niveau donné
        level_list = self.component.select_risk_level(level=risk_level)
        # On recupere le periodes couverte par chaque niveau
        best_level, common_period = self._find_best_conf_match(level_list, risk_period)
        agg = best_level.aggregation_type
        if agg != "downStream":
            raise LocalisationError(
                f"We are able to localise only downStream risk. Get {agg}"
            )
        # ==========================
        # On va filtrer pour mettre seulement ceux de la zone qui nous intéresse
        # ! ici plutôt que de faire une copie du geo du best_level, on pourrait
        # ! tout simplement faire une boucle sur les geos des events en leur
        # ! assignant de nouveaux mask_id à chaque fois
        best_level.compute_list = []
        for event in best_level.elements_event:
            if self.geo_id in event.geos.mask_id:
                event.geos.mask_id = [self.geo_id]
                event.compute_list = []
            else:
                raise LocalisationError(
                    f"mask_id '{self.geo_id}' not available "
                    f"(among {best_level.event.geos.mask_id})."
                )
        # ==========================
        # On va réadapter la periode.
        # Cela permettra de calculer le risque que sur la période précisée.
        # On va faire cela sauf pour les risques de type Bertrand.
        # Ces derniers requièrent d'avoir l'ensemble du dataset pour être calculés
        # par contre ensuite on va revenir sur la période courte.
        if best_level.is_bertrand():
            LOGGER.info("Risk is bertrand kind. So we compute all and select after")
        else:
            best_level.update_selection(
                sel={self.component.time_dimension: common_period}
            )

        # ==========================
        # On va cacluler le risk
        _ = best_level.compute()
        self.full_risk = best_level.spatial_risk_da
        if best_level.is_bertrand():
            self.full_risk = self.full_risk.sel(
                {self.component.time_dimension: common_period}
            )

        # log.error(f"Full risk values {self.full_risk.max().values}")
        # ==========================
        # On va maintenant "localiser ce risque", c'est à dire recupérer les
        # "bests zones"
        domain, localisation_area = self._get_poss_localisation_area(best_level)
        domain_no_id = domain.reset_coords("id", drop=True)
        self.full_risk = self.full_risk.squeeze("id").reset_coords("id", drop=True)
        localised_area = get_n_area(
            self.full_risk,
            domain_no_id,
            localisation_area,
            n=2,
            cdt=0.001,
            between_authorized=self.between_authorized,
        )

        ingredient = SpatialIngredient(
            domain, localisation_area, localised_area, best_level.get_grid_name()
        )
        return ingredient

    def compute_information_on_area(
        self, risk_level: int, da_area: xr.DataArray
    ) -> xr.Dataset:
        """
        This enable the computation of the risk (for a given level)
        over the "localised area".
        This computation is performed for the full period


        Args:
            risk_level (int): The wanted level
            da_area (xr.DataArray): The localised_area.
                ! da_area correspond au self.localised_area. Il se trouve que
                ! ce dataarray contient des IDs de zones nouvellement créées
                ! (intersection, difference, complémentaire), donc on ne peut
                ! a priori pas uniquement passer les Ids de zones. Par contre on
                ! pourrait exporter un nouveau masque, et changer les GeoComposite
                ! par la config correspondante à ces masques. #GeoGate

        ToDo :
          Ajouter un moyen d'interpoler entre la grille d'entrée
          et de sortie pour différent niveaux.
          Comment passer les infos ?
             => risk.get_grid_name()
             => self.best_level.get_grid_name()

        Returns:
            xr.Dataset: The Dataset containing the component's risks
        """
        new_component = self.component.new()
        level_list = [
            lvl.new() for lvl in self.component.select_risk_level(level=risk_level)
        ]

        for level in level_list:
            # On force les zones géographique et les éléments à calculer
            # TODO : changer les lignes suivantes : ref #GeoGate
            # TODO : on ne doit pas changer le type d'un level.geos
            # ! ici on pourrait changer uniquement les geos des events
            # level.geos = da_area  # ! horrible, à changer : ref #GeoGate
            level.compute_list = ["density", "representative"]
            for event in level.elements_event:
                event.geos = da_area  # ! horrible, à changer : ref #GeoGate
                event.compute_list = ["density", "representative"]  # ! pas beau

        new_component.levels = level_list
        return new_component.compute()

    def _get_poss_localisation_area(self, best_level: LevelComposite):
        """Retourne les localisations possibles.
        Args:
            best_level (LevelComposite): Un element de configuration
                (un peu updater dans localise)
        Raises:
            ValueError: [description]

        Returns:
            [dataArray, DataArray]: Le domain, Les zones de localisation
        """
        # geo = best_level.geos  # ! ici on pourrait deepcopy
        for event in best_level.elements_event:
            geo = event.geos
            break

        if isinstance(geo, GeoComposite):  # ! temporary #GeoGate
            geo = geo.new()
            # Chargement des masques en précisant la grille
            geo.grid_name = best_level.get_grid_name()
            geo.mask_id = None
            full_list = geo.compute()
        elif isinstance(geo, xr.DataArray):  # ! temporary #GeoGate
            full_list = geo

        domain = full_list.sel(id=self.geo_id)
        # On va ensuite selectionner les id commençant par geo_id
        id_list = [
            idi
            for idi in full_list.id.values
            if idi.startswith(self.geo_id) and idi != self.geo_id
        ]
        selected_area = full_list.sel(id=id_list)
        drop_ids = []
        # On va rajouter compass_split et altitude_split
        compass = best_level.localisation.compass_split
        altitude_split = best_level.localisation.altitude_split
        geo_desc = best_level.localisation.geos_descriptive
        if not compass:
            compass_idx = selected_area["areaType"] == "compass"
            drop_ids.extend(selected_area.sel(id=compass_idx).id.values)

        if not altitude_split:
            alt_idx = selected_area["areaType"] == "Altitude"
            drop_ids.extend(selected_area.sel(id=alt_idx).id.values)

        id_list.extend(geo_desc)
        id_list = list(set(id_list).difference(set(drop_ids)))
        if len(id_list) > 0:
            localisation_area = full_list.sel(id=id_list).dropna("id", how="all")
        else:
            raise LocalisationError(
                "There is no area for localisation process. "
                "So no localisation is performed."
            )
        return domain, localisation_area

    @staticmethod
    def _find_best_conf_match(level_list: List[LevelComposite], risk_period: set):
        """Enable to find the best "risk" in the list.
            This is based on common period
        Args:
            level_list (List[LevelComposite]): List of Levels
            risk_period ([type]): Period we are interested in
        Returns:
            [LevelComposite]: The best level of the list for localisation.
            [list] : common period : The list of period to localise for this risk
        """
        input_period = risk_period
        first_time = None
        best_level = None
        for level in level_list:
            level_period = set(level.get_cover_period().values)
            intersect = input_period.intersection(level_period)
            # log.error("Period intersection %s",intersect)
            # Nombre d'élement commun
            nb_common = len(intersect)
            if nb_common > 0 and first_time is None:
                best_level = level.new()
                best_common = nb_common
                l_inter = sorted(intersect)
                first_time = l_inter[0]
                common_period = l_inter
            elif nb_common > 0:
                l_inter = sorted(intersect)
                current_first = l_inter[0]
                # Conditions pour detronner le meilleur actuel
                if current_first < first_time and nb_common >= best_common / 4:
                    # On souhaite l'evt le plus jeune (s'il a un nombre de
                    # correspondance importante)
                    best_common = nb_common
                    best_level = level.new()
                    common_period = l_inter
                elif current_first > first_time and nb_common >= 4 * best_common:
                    # On est aussi d'accord pour prendre un evt
                    # avec une grille moins résolue.
                    # si le nombre d'échéance dépasse un certain seuil.
                    best_common = nb_common
                    best_level = level.new()
                    common_period = l_inter
        if best_level is None:
            raise ValueError("Best conf not found")
        return best_level, common_period
