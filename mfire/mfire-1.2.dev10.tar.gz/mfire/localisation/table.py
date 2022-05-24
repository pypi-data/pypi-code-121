"""
This module is for the management of 3x3 tables.
"""
from typing import Optional
import json
import os
import xarray as xr

import baseconvert

import dateutil
from mfire.localisation.area_algebre import get_representative_area_properties
from mfire.localisation.spatial_localisation import SpatialIngredient

from mfire.text.period_describer import PeriodDescriber
from mfire.utils.date import Datetime, Period
from mfire.settings import get_logger

# Logging
LOGGER = get_logger(name="table.mod", bind="table")

xr.set_options(keep_attrs=True)


class InputError(ValueError):
    """To raiseError for input"""


class SummarizedTable:
    """
    Gere les tableaux résumant la situation
    """

    _nc_table = "input_table.nc"
    _spatial_base_name = "SpatialIngredient"
    _json_config = "summarized_table_config.json"

    def __init__(
        self,
        da: xr.DataArray,
        request_time: Datetime,
        full_period: Period,
        spatial_ingredient: Optional[SpatialIngredient] = None,
    ):
        """
        Args:
            da (DataArray): A 3 period dataArray
            request_time (Datetime) : production datetime
            full_period (Period) : periode couverte par le bulletin
                Permettrait de mettre en relief le tableau.

        Raises:
            InputError: [description]
        """
        self.input_table = da
        self.spatial_ingredient = spatial_ingredient
        self.request_time = request_time
        self.full_period = full_period
        # ------------------------------------
        self.period_describer = PeriodDescriber(request_time)

        self.working_table = da.copy()

        self.unique_table = xr.Dataset()
        self.unique_name = "Unknown"
        self.define_unique_table()

    def auto_save(self, fname):
        """Permet la sauvegarde des éléments pour les recharger.

        Args:
            fname (str): Nom de base
        """
        LOGGER.info(
            f"Saving  summarized table to {os.path.join(fname , self._nc_table)}"
        )
        self.input_table.to_netcdf(os.path.join(fname, self._nc_table))
        if self.spatial_ingredient is not None:
            self.spatial_ingredient.auto_save(
                os.path.join(fname, self._spatial_base_name)
            )
        # On va aussi sauver un fichier json contenant request_time et full_period
        dout = {}
        dout["request_time"] = self.request_time
        dout["full_period"] = self.full_period.toJson()
        with open(os.path.join(fname, self._json_config), "w") as fp:
            json.dump(dout, fp)

    @classmethod
    def load(cls, fname):
        """Enable to load a SummarizedTable element saved with auto_save method.

        Args:
            fname (str): The same path/basename [description]

        Returns:
            [type]: [description]
        """
        input_table = xr.open_dataarray(os.path.join(fname, cls._nc_table)).load()
        if os.path.exists(os.path.join(fname, cls._spatial_base_name)):
            spatial_ingredient = SpatialIngredient.load(
                os.path.join(fname, cls._spatial_base_name)
            )
        else:
            spatial_ingredient = None
        with open(os.path.join(fname, cls._json_config), "r") as fp:
            data = json.load(fp)
        request_time = data["request_time"]
        full_period = Period(**data["full_period"])
        return cls(input_table, request_time, full_period, spatial_ingredient)

    def get_unique_table(self):
        """Return table. The table is sorted and in reduced form
        Returns:
            [dataArray]: The table
        """
        return self.unique_table

    def get_unique_name(self):
        """Return the name of the reduced form table

        Returns:
            [str]: The table name
        """
        return self.unique_name

    def get_raw_table(self):
        """Return reduced table as a list

        Returns:
            [list]: The list contain  the number of period
                    as well as the description of each table line.
        """
        return self.raw_table

    def check_unique(self):
        """
        Permet de voir si le tableau est bien sous forme "unique".
        Les règles de permutations doivent être respectées pour les lignes
        Sur les colonnes, les règles doivent aussi être respectées.
        Cependant on ne peut pas vérifier qu'elles sont dans le "bon ordre".
        On peut juste vérifier que :
           - la première et dernière colonne n'est pas vide
        """
        result = True
        code = self.encode_table(self.unique_table)
        l_code = sorted(code)
        if l_code != list(code):
            LOGGER.warning(
                f"Line are not correctly sorted. {code}. Should be ascending order."
            )
            result = False
        if len(set(code)) != len(code):
            LOGGER.warning(f"Redundant line exists {code}.")
            result = False
        if self.unique_table.isel(period=0).sum() == 0:
            LOGGER.warning(f"First column has no risk {self.unique_table}")
            result = False
        if self.unique_table.isel(period=-1).sum() == 0:
            LOGGER.warning(f"Last column has no risk {self.unique_table}")
            result = False
        return result

    @staticmethod
    def define_raw_table_name(raw_table):
        """
        Retourne le nom correspondant à partir d'une liste/tuple
        en base 10 (incluant un string pour la période).Le nom est générique.
        Ainsi les lignes sont triées de la plus petite à la plus grande dans
        la fonction.

        Args:
            raw_table (tuple/list/frozenset): Le tableau à résumé.
                Par exemple ["3",7,2,0]

        Returns:
            str: Le  nom du talbeau
        """
        base = [next(k for k in raw_table if isinstance(k, str))]
        nums = sorted(str(int(k)) for k in raw_table if not isinstance(k, str))
        return f"P{'_'.join(base + nums)}"

    @staticmethod
    def encode_table(ds_table):
        """
        Convertit le tableau de la base 2 à la base 10.
        Chaque ligne étant une succession de 0 et de 1 elle est convertie en base2.

        Args:
           ds_table (dataset): Le tableau à résumé en tuple.

        Returns:
            tuple: le tuple auquel correspond le tableau.
        """
        l_out = list()
        for zone in ds_table["id"]:
            elt = ds_table.sel({"id": zone}).values
            res = baseconvert.base(tuple(elt), 2, 10)
            try:
                l_out.append(res[0])
            except IndexError as excpt:
                LOGGER.error(
                    f"Erreur dans l'encodage de {ds_table}. Ids = {ds_table.id.values}",
                    elt=list(elt),
                    elt_type=type(elt),
                    res=res,
                    res_type=type(res),
                    l_out=l_out,
                    zone=str(zone.values),
                )
                raise excpt
        return tuple(l_out)

    def define_unique_table(self):
        """
        This function perform operation on the input table.
         - Squeeze empty period
         - merge similar period
         - Order and merge area
        This is done while keeping information on AreaName and on PeriodName.
        It enable to define the "unique_table" and the unique_name
        """
        self.squeeze_empty_period()
        self.merge_similar_period()
        self.merge_period_with_same_name()
        self.merge_similar_period()

        # Il va falloir maintenant permuter les lignes
        raw_table = list(self.encode_table(self.working_table))
        self.working_table["raw"] = (("id"), raw_table)
        raw_table.insert(0, str(int(self.working_table.period.size)))
        self.raw_table = raw_table
        self.unique_name = self.define_raw_table_name(frozenset(raw_table))
        # On va permuter et fusionner les lignes en fonction des résultats du tuple
        # On n'a pas besoin de redefinir le nom unique apres
        # (on sait avant de l'envoyer au charbon qu'il y aura fusion)
        self.unique_table = self.order_and_merge_area()[self.input_table.name]

    def squeeze_empty_period(self):
        """
        Supprime les périodes vides en début et fin de talbeau.
        """
        i = 0
        squeeze_list = []
        while self.working_table.isel(period=[i]).sum().values == 0:
            squeeze_list.append(i)
            i += 1
        i = self.working_table.period.size - 1
        while self.working_table.isel(period=[i]).sum().values == 0:
            squeeze_list.append(i)
            i += -1
        select = set([i for i in range(self.working_table.period.size)])
        to_select = sorted(select.difference(set(squeeze_list)))
        self.working_table = self.working_table.isel(period=to_select)

    def merge_similar_period(self):
        """
        Merge similar period.
        Two period are similar if they are adjacent and risk values are the same.

        This function should work for any number of period.
        """
        if self.working_table.period.size > 0:
            index_to_remove = []
            period_name = [self.working_table.period.isel(period=0).values]
            for p in range(1, self.working_table.period.size):
                if (
                    self.working_table.isel(period=[p]).values
                    == self.working_table.isel(period=[p - 1]).values
                ).all():
                    index_to_remove.append(p)
                    # Mettre un nom de period en adequation.
                    period_name[-1] = (
                        str(period_name[-1])
                        + "_+_"
                        + str(self.working_table.isel(period=[p])["period"].values[0])
                    )
                else:
                    period_name.append(self.working_table.period.isel(period=p).values)
        if index_to_remove != []:
            index = set(list(range(self.working_table.period.size)))
            index = index.difference(set(index_to_remove))
            keep_list = sorted(index)
            self.working_table = self.working_table.isel(period=keep_list)
            self.working_table["period"] = period_name

    def merge_period_with_same_name(self):
        """Permet de merger des periodes qui auraient le meme nom.

        Returns:
            None
        """
        # On va commencer par juste afficher les périodes
        array_name = self.working_table.name
        the_names = []
        for period in self.working_table["period"].values:
            time_list = period.split("_to_")
            try:
                period_obj = Period(time_list[0], time_list[-1])
                LOGGER.debug(
                    f"Period = {period_obj} "
                    f"({self.period_describer.describe(period_obj)})"
                )
            except dateutil.parser._parser.ParserError:
                LOGGER.warning(
                    f"At least one period value is not a datetime {period}. "
                    "We will not merge period by name."
                )
                return None
            the_names += [self.period_describer.describe(period_obj)]

        self.working_table["period_name"] = (("period"), the_names)
        # Maintenant on va merger
        # Pour cela on va selectionner les periodes ayant le même nom et on les merge.
        # On suppose que des périodes portent le même nom seulement si elles sont
        # consécutives.
        if len(set(the_names)) != len(the_names):
            LOGGER.info(
                "Différentes périodes ont le même nom. "
                "On va merger ces périodes (en prenant le pire des risques)."
            )
            tmp_list = []
            # LOGGER.info(f"Nom des périodes {the_names}")
            for pname in set(the_names):
                table_to_reduce = self.working_table.where(
                    self.working_table.period_name == pname, drop=True
                )
                if table_to_reduce.period.size > 1:
                    reduced_table = table_to_reduce.max("period")
                    first_period = str(
                        table_to_reduce["period"].isel(period=0).values
                    ).split("_to_")
                    last_period = str(
                        table_to_reduce["period"].isel(period=-1).values
                    ).split("_to_")
                    # On va vérifier
                    reduced_pname = self.period_describer.describe(
                        Period(first_period[0], last_period[-1])
                    )
                    if pname != reduced_pname:
                        LOGGER.info(
                            f"After merging similar period named {pname}, "
                            f"the period_name is different: {reduced_pname}"
                        )
                    reduced_table["period"] = first_period[0] + "_to_" + last_period[-1]
                    reduced_table = reduced_table.expand_dims("period")
                    tmp_list += [reduced_table]
                else:
                    tmp_list += [table_to_reduce]
            self.working_table = xr.merge(tmp_list)[array_name]
        if "period_name" in self.working_table.coords:
            self.working_table = self.working_table.drop_vars("period_name")
        return None

    def merge_zones(self, da):
        """
        Devrait fonctionner avec n'importe quel nombre de zones
        Merge les zones similaires.
        Conserve les autres variables dépendant de l'identificateur de zones

        Devrait être appelé depuis l'exterieur pour merger des zones du talbeau ?

        Args :
            da (DataArray)
        """
        id_list = []
        for ids in da.id.values:
            id_list.extend(ids.split("_+_"))

        if da["id"].size > 1:
            dout = xr.Dataset()
            # Determination du nouvel id
            area_id = "_+_".join(da["id"].values.astype(str))
            dout = da.isel({"id": 1})

            dout = (
                dout.drop_vars("id").expand_dims("id").assign_coords({"id": [area_id]})
            )
            # On va regarder les autres coordonnées.
            # On merge de manière pas bête les noms seulement si on a un
            # spatial_ingredient.
            if "areaName" in da.coords and self.spatial_ingredient is not None:
                (area_name, area_type) = get_representative_area_properties(
                    self.spatial_ingredient.localised_area.sel({"id": id_list}),
                    self.spatial_ingredient.full_area_list,
                    domain=self.spatial_ingredient.domain,
                )
                dout["areaName"] = (("id"), [str(area_name)])
                dout = dout.swap_dims({"id": "areaName"}).swap_dims({"areaName": "id"})
                dout["areaType"] = (("id"), [area_type])
                dout = dout.swap_dims({"id": "areaType"}).swap_dims({"areaType": "id"})
                LOGGER.debug(f"areaName {area_name} ")
            elif "areaName" in da.coords:
                dout["areaName"] = (
                    ("id"),
                    ["_+_".join(da["areaName"].values.astype(str))],
                )
                dout = dout.swap_dims({"id": "areaName"}).swap_dims({"areaName": "id"})
                dout["areaType"] = (("id"), ["mergedArea"])

        else:
            dout = da

        return dout

    def order_and_merge_area(self):
        """
        Ordonne le dataArray pour être en phase avec le modèle unique.
        Fusionne aussi les zones similaires.
        Returns :
           Le dataArray avec les zones mergées et permutées.
        """

        dout = xr.Dataset()
        table = sorted(set(self.working_table["raw"].values))
        final_list = []
        area_list = []  # Permet d'etre sur de l'ordre apres le merge.
        for elt in table:
            db = self.working_table.sel({"id": (self.working_table["raw"] == elt)})
            dtmp = self.merge_zones(db.drop_vars("raw"))
            area_list.append(dtmp["id"].values[0])
            final_list.append(dtmp)

        dout = xr.merge(final_list).sel({"id": area_list})
        if "areaName" in dout.coords:
            dout["areaName"] = dout["areaName"].astype(str)
        return dout

    def update_uniqueTable(self, id_list):
        LOGGER.debug(f"Unique_name before {self.unique_name}")
        # raw_table = self.encode_table(self.working_table)
        # self.working_table["raw"] = (("id"), raw_table)
        area_to_merge = self.working_table.sel(id=id_list)
        merged_area = self.merge_zones(area_to_merge)
        unmerged_id = [
            idi for idi in self.working_table.id.values if idi not in id_list
        ]
        unmerged_area = []
        if unmerged_id != []:
            unmerged_area = self.working_table.sel(id=unmerged_id)
            self.working_table = xr.merge(
                [merged_area.drop_vars("raw"), unmerged_area.drop_vars("raw")]
            )["elt"]
        else:
            self.working_table = merged_area.drop_vars("raw")
        self.define_unique_table()
        LOGGER.debug(f"Unique_name after {self.unique_name}")


if __name__ == "__main__":
    df = xr.Dataset()
    df.coords["period"] = [
        "20190727T06_to_20190727T11",
        "20190727T12_to_20190727T14",
        "20190727T15_to_20190727T16",
    ]
    #   df.coords["zone"] = [f"zone{k+1}" for k in range(3)]
    df.coords["id"] = [
        "4830b20e-e936-4e65-9bf2-737dd451275c",
        "24830b20e-e936-4e65-9bf2-737dd451275cd",
        "34830b20e-e936-4e65-9bf2-737dd451275ce",
    ]
    df["elt"] = (("id", "period"), [[0, 1, 0], [0, 1, 0], [1, 0, 1]])
    df["areaName"] = (("id"), ["Area1", "Area2", "Area3"])

    df = df.swap_dims({"id": "areaName"}).swap_dims({"areaName": "id"})
    Full_period = Period("20190726T16", "20190727T15")
    Request_time = "20190726T16"
    table_handler = SummarizedTable(
        df["elt"], request_time=Request_time, full_period=Full_period
    )
    table_handler.auto_save("/scratch/labia/chabotv/test")
    print(table_handler.get_unique_name())
    print(table_handler.get_unique_table())

    new_table = SummarizedTable.load("/scratch/labia/chabotv/test")
    print(new_table.get_unique_table())
    print(new_table.full_period)
