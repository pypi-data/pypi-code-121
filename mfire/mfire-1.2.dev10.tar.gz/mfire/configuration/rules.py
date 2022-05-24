"""
Pydantic models for data rules
"""
import os
from copy import deepcopy
from typing import Optional, Union, List, Tuple

import pandas as pd
import numpy as np
from pydantic import BaseModel, validator, root_validator

from mfire.settings import RULES_DIR
from mfire.utils.date import Datetime, Timedelta


def get_terms(start: Datetime, stop: Datetime, step: Timedelta) -> List[Datetime]:
    """Function returning a list of Datetime-terms out of given start, stop and step
    arguments.

    Args:
        start (Datetime): First term
        stop (Datetime): Max term
        step (Timedelta): Step between two consecutive terms

    Returns:
        List[Datetime]: List of terms
    """
    term_range = range(int((stop - start) / step) + 1)
    return [Datetime(start + step * i) for i in term_range]


class CommonRules(BaseModel):
    """Class which encapsulate the Data Rules concept of Promethee.
    To recap : "data rules" in promethee consists in defining which data
    to retrieve according to various criterias like the current datetime,
    the geometry used, the time steps to provide, etc. It also concerns the
    definition of extraction and preprocessing processes.
    This rules are defined in CSV files.

    In the common rules, we use the following CSV files :
    - grib_param : defines the way to extract parameters from grib files
    - agg_param : defines the links between accumulated parameters (e.g. RR6_SOL)
        and their equivalent root parameters (e.g. RR_SOL)
    - param_link : defines linked parameters (e.g. FF, RAF and DD)
    - geometries : defines the geometries (e.g. EURW1S100) features.

    Args:
        dirname (Optional[str]): Directory where to find the CSV files. Default to
            os.path.dirname(__file__).

    Raises:
        ValueError: If given dirname doesn't exist
    """

    dirname: Optional[str] = RULES_DIR
    _grib_param_df: Optional[pd.DataFrame] = None
    _agg_param_df: Optional[pd.DataFrame] = None
    _param_link_df: Optional[pd.DataFrame] = None
    _geometries_df: Optional[pd.DataFrame] = None

    class Config:
        """Pydantic base model config to accept private attrs of
        arbitrary types (e.g. pd.DataFrames)
        """

        arbitrary_types_allowed = True
        underscore_attrs_are_private = True

    @validator("dirname")
    def init_dirname(cls, dirname: str) -> str:
        """validates the given dirname.

        Args:
            dirname (str): Directory where the CSV are expected to be.

        Raises:
            ValueError: If the given dirname doesn't exist.

        Returns:
            str: Given validated directory.
        """
        if os.path.isdir(dirname):
            raise ValueError(f"Directory {dirname} doesn't exist")
        return dirname

    def _get_filename(self, file_kind: str) -> str:
        """Provides the filename corresponding to the given file kind.

        Args:
            file_kind (str): Kind of CSV file among "grib_param", "agg_param",
                "param_link" and "geometries".

        Raises:
            ValueError: If the filename corresponding to the given kind doesn't exist
                where it is expected.

        Returns:
            str: Corresponding full filename.
        """
        filename = os.path.join(self.dirname, file_kind + ".csv")
        if not os.path.isfile(filename):
            raise ValueError(f"Csv file {filename} doesn't exist.")
        return filename

    def _get_df(
        self, file_kind: str, index_col: Union[int, List[int]] = None
    ) -> pd.DataFrame:
        """Private method to factorize the dataframe retrieving/creation process.
        It checks if the dataframe corresponding to the file_kind already exists, and
        if not it creates the dataframe, then it returns it.

        Args:
            file_kind (str): Kind of CSV file.
            index_col (Union[int, List[int]], optional): Pandas option index_col.
                Defaults to None.

        Returns:
            pd.DataFrame: Imported csv file as a pandas DataFrame
        """
        attr_name = f"_{file_kind}_df"
        if self.__getattribute__(attr_name) is None:
            new_df = (
                pd.read_csv(self._get_filename(file_kind), index_col=index_col)
                .dropna(axis=1, how="all")
                .sort_index()
            )
            self.__setattr__(attr_name, new_df)
        return self.__getattribute__(attr_name)

    @property
    def grib_param_df(self) -> pd.DataFrame:
        return self._get_df("grib_param", index_col=[0, 1])

    @property
    def agg_param_df(self) -> pd.DataFrame:
        return self._get_df("agg_param", index_col=0)

    @property
    def param_link_df(self) -> pd.DataFrame:
        return self._get_df("param_link", index_col=0)

    @property
    def geometries_df(self) -> pd.DataFrame:
        return self._get_df("geometries", index_col=0)

    def get_bounds(self) -> List[Tuple[str, list]]:
        bound_names = ["lat_min", "lon_min", "lat_max", "lon_max"]
        return [
            (geometry, self.geometries_df.loc[geometry, bound_names].values)
            for geometry in self.geometries_df.index
        ]

    def param_to_description(self, param: str) -> Tuple[str, int]:
        """param_to_description : Get a complete parameter name and returns
        a tuple containing the root parameter name, the parameter level, and
        the accumulation period in hours

        Args:
            param (str): Parameter complete name

        Returns:
            tuple:
                str: Parameter level
                int: Accumulation period in hours
        """
        root_param, param_level = param.split("__")
        if root_param in self.agg_param_df.index:
            agg_description = self.agg_param_df.loc[root_param]
            return (
                agg_description["param"] + "__" + param_level,
                int(agg_description["accum"]),
            )

        return param, None

    def description_to_param(
        self, root_param: str, param_level: str, accum: int
    ) -> str:
        """description_to_param: Returns the complete parameter name given
        the root parameter name, the parameter level and the accumulation period.

        Args:
            root_param (str): Root parameter name
            param_level (str): Parameter level
            accum (int): Accumulation period in hours

        Returns:
            str: Complete parameter name
        """
        agg_index = self.agg_param_df[self.agg_param_df["param"] == root_param]
        agg_index = agg_index[agg_index["accum"] == accum].index
        if len(agg_index) == 0:
            return root_param + "__" + param_level

        param_name = agg_index[0]
        return param_name + "__" + param_level


class Rules(CommonRules):
    """Class heritating from common rules to encapsulate specific data rules.

    In the specific rules, we use the following CSV files :
    - source_files : defines source grib files to use (following the Vortex standard)
    - preprocessed_files : defines preprocessed files to use (following the Vortex
        Standard)
    - files_links : defines the correspondances between preprocessed and source files.

    Raises:
        ValueError: If the given name doesn't have a corresponding directory
    """

    name: str
    drafting_datetime: Optional[Datetime] = Datetime.now()
    _source_files_df: Optional[pd.DataFrame] = None
    _preprocessed_files_df: Optional[pd.DataFrame] = None
    _files_links_df: Optional[pd.DataFrame] = None

    @root_validator
    def check_values(cls, values):
        """root validator in charge of checking if the given name
        has an existing corresponding directory

        Args:
            values: class args

        Raises:
            ValueError: If the directory corresponding to the given name doesn't exist

        Returns:
            Validated values.
        """
        rules_dirname = os.path.join(values.get("dirname"), values.get("name"))
        if not os.path.isdir(rules_dirname):
            raise ValueError(f"Directory {rules_dirname} doesn't exist")
        return values

    @validator("drafting_datetime", pre=True)
    def check_datetime(cls, v) -> Datetime:
        if isinstance(v, Datetime):
            return v
        return Datetime(v)

    @property
    def reference_datetime(self) -> Datetime:
        """reference_datetime : Property returning the reference datetime
            (i.e. the rounded drafting datetime to the previous hour)

        Returns:
            Datetime : reference datetime
        """
        return self.drafting_datetime.rounded

    @property
    def bulletin_datetime(self) -> Datetime:
        """bulletin_datetime : Property returning the bulletin datetime
            (i.e. the rounded drafting datetime to the next hour)

        Returns:
            Datetime : bulletin datetime
        """
        return self.reference_datetime + Timedelta(hours=1)

    def _get_filename(self, file_kind: str) -> str:
        """Supercharge method providing the filename corresponding to the given
        file_kind. It first checks if the file exists in the given rules directory,
        if not it provides the corresponding default common filname if it exists.

        Args:
            file_kind (str): Kind of the CSV file we want to retrieve.

        Returns:
            str: Corresponding full filename.
        """
        filename = os.path.join(
            os.path.join(self.dirname, self.name), file_kind + ".csv"
        )
        # First trying to find file in the actual rules directory
        if os.path.isfile(filename):
            return filename
        # If not found, trying to find file in the common directory
        return super(Rules, self)._get_filename(file_kind)

    def _apply_date(
        self, dataframe: pd.DataFrame, days_offset: int = 0
    ) -> pd.DataFrame:
        """apply_date : Change all the dates in a given dataframe according to the
        self.drafting_datetime (modulo a number of days 'days_offset').

        Args:
            dataframe (pandas.DataFrame): Dataframe to transform
            current_datetime (Datetime): Datetime to apply

        Returns:
            pd.DataFrame: New Dataframe with self.drafting_datetime applied
        """
        # copying the original dataframe
        dataframe_copy = pd.DataFrame()

        # calculating the proper date to apply
        my_date = (self.bulletin_datetime + Timedelta(days=days_offset)).midnight

        # columns processing
        for col in dataframe:
            new_col = my_date.format_bracketstr(col)
            dataframe_copy[new_col] = dataframe[col].apply(my_date.format_bracketstr)

        # index processing
        dataframe_copy.index = pd.Index(map(my_date.format_bracketstr, dataframe.index))

        if "date" not in dataframe:
            return dataframe_copy

        def datetimize(column: str, offset_datetime: Datetime):
            """datetimize : Local function for changing integer timedeltas
            into datetimes in the dataframe_copy.

            Args:
                column (str): Column name
                offset_datetime (Datetime): Base datetime from which all
                timedeltas are applied
            """
            if column not in dataframe_copy:
                return None
            dataframe_copy.loc[:, column] = (
                dataframe_copy[column].apply(
                    lambda n: Timedelta(hours=int(n)) if np.isfinite(n) else np.nan
                )
                + offset_datetime
            )
            return None

        for column in ["date", "dispo_time"]:
            # dates in columns 'date' and 'dispo_time' are calculated from the
            # 'my_date' variable.
            datetimize(column, my_date)

        for column in ["start", "stop"]:
            # while 'start' and 'stop' dates are calculated from the 'date'
            # column
            datetimize(column, dataframe_copy["date"])
        return dataframe_copy

    def _create_df(
        self, file_kind: str, concat_axis: int = 0, nb_days: int = 1
    ) -> pd.DataFrame:
        attr_name = f"_{file_kind}_df"
        if self.__getattribute__(attr_name) is None:
            # rules xls file opening
            raw_df = pd.read_csv(self._get_filename(file_kind), index_col=0).dropna(
                axis=1, how="all"
            )

            # Concatenating for today and nb_days before
            full_df = pd.concat(
                [self._apply_date(raw_df, days_offset=-i) for i in range(nb_days)],
                axis=concat_axis,
            )
            # Finally only keeping the lines of available files
            if "dispo_time" in full_df and "geometry" in full_df:
                full_df = full_df[full_df["dispo_time"] <= self.reference_datetime]
                full_df["mesh_size"] = full_df["geometry"].apply(
                    lambda s: self.geometries_df.loc[s, "mesh_size"]
                )
                full_df = full_df.sort_values(
                    by=["mesh_size", "dispo_time"], ascending=[True, False]
                )
                full_df["terms"] = full_df.apply(
                    lambda x: get_terms(
                        x["start"], x["stop"], Timedelta(hours=x["step"])
                    ),
                    axis=1,
                )
            self.__setattr__(attr_name, full_df)
        return self.__getattribute__(attr_name)

    @property
    def source_files_df(self) -> pd.DataFrame:
        return self._create_df("source_files", concat_axis=0, nb_days=3)

    @property
    def preprocessed_files_df(self) -> pd.DataFrame:
        df = self._create_df("preprocessed_files", concat_axis=0, nb_days=2)
        if "params" not in df:
            df["params"] = df.index.to_frame().applymap(
                lambda x: set(self.files_links_df[x].dropna().index)
            )
        return df

    @property
    def files_links_df(self) -> pd.DataFrame:
        return self._create_df("files_links", concat_axis=1, nb_days=2)

    @property
    def files_ids(self) -> set:
        return set(self.source_files_df.index).union(self.preprocessed_files_df.index)

    def get_file_info(self, file_id: str) -> pd.Series:
        """get_file_info : returns informations from a given file_id
        (source or preprocessed) extracted from either self.source_files_df
        or self.preprocessed_files_df and adds to the file_info the list of terms.

        Args:
            file_id (str): File ID in the self.source_files_df or in
                self.preprocessed_files_df indexes.

        Returns:
            dict : File info
        """
        if file_id in self.source_files_df.index:
            file_info = deepcopy(self.source_files_df.loc[file_id])

        elif file_id in self.preprocessed_files_df.index:
            file_info = deepcopy(self.preprocessed_files_df.loc[file_id])

        else:
            return pd.Series([], dtype=np.uint8)

        return file_info

    def get_alternate(self, file_id: str) -> str:
        try:
            return self.get_file_info(file_id)["alternate"]
        except Exception:
            return None

    def best_preprocessed_file_term(
        self, term: Datetime, geometries: List[str], params: List[str]
    ) -> str:
        """best_preprocessed_file_term: Returns the best preprocessed file id
        according to the given term, useable geometries and parameters

        Args:
            term (datetime.datetime): Term
            geometries (iterable of str) : List, tuple or set of useable geometries
            params (iterable of str) : List, tuple or set of parameters

        Returns:
            str : Most conveniant preprocessed file id
        """
        available_files_df = self.preprocessed_files_df[
            (self.preprocessed_files_df.start <= term)
            & (self.preprocessed_files_df.stop >= term)
            & (self.preprocessed_files_df.geometry.isin(geometries))
        ]
        for file_id in available_files_df.index:
            if term not in available_files_df.loc[file_id, "terms"]:
                continue
            params_set = set(self.param_to_description(param)[0] for param in params)
            if params_set.issubset(available_files_df.loc[file_id, "params"]):
                return [file_id] + available_files_df.loc[
                    file_id, ["date", "stop"]
                ].to_list()
        return None

    def best_preprocessed_files(
        self, start: Datetime, stop: Datetime, geometries: List[str], params: List[str]
    ) -> List[Tuple[str, str, str]]:
        """Find the most convenient preprocessed files according to the given start,
        stop, geometries and parameters.

        Args:
            start (datetime.datetime): Start datetime of the period
            stop (datetime.datetime): Stop datetime of the period
            geometries (iterable of str) : List, tuple or set of useable geometries
            params (iterable of str) : List, tuple or set of parameters

        Returns:
            list : list of all the files descriptions needed to cover the period,
                the zone and the parameters.
                A file description (an element of the returned list) is a tuple
                containing the filename, the start term of the file and the stop
                term.
        """

        if start > stop or self.bulletin_datetime > stop:
            # on vérifie d'abord la cohérence des dates données entre-elles
            return []

        # on vérifie ensuite que tous les fichiers qui nous vont bien
        # ne soient pas déjà dans le passé
        possible_files_df = self.preprocessed_files_df[
            (self.preprocessed_files_df.stop >= start)
            & (self.preprocessed_files_df.geometry.isin(geometries))
        ]
        files_start_min = possible_files_df.start.min()
        if len(possible_files_df) == 0 or stop < files_start_min:
            return []

        # on associe finalement au "start" la première date possible de début entre
        # la date de bulletin, la date de début donnée et la première date dispo
        correct_start = max(self.bulletin_datetime, start, files_start_min)
        current_best_file = self.best_preprocessed_file_term(
            correct_start, geometries, params
        )
        if current_best_file is None:
            # cas particulier où il existe encore des fichiers d'intérêt
            # mais le terme "correct_start" n'est pas contenu dans l'ensemble
            # des terms des fichiers
            return self.best_preprocessed_files(
                correct_start + Timedelta(hours=1), stop, geometries, params,
            )

        filename, _, file_stop = current_best_file
        other_files = []
        if file_stop >= stop:
            # si on a dépassé le date "stop" cible, alors on s'arrête
            file_stop = stop

        elif file_stop < possible_files_df.stop.max():
            # sinon si on n'a pas dépassé le "stop" max dispo alors on continue
            other_files = self.best_preprocessed_files(
                file_stop + Timedelta(hours=1), stop, geometries, params,
            )
        return [(filename, str(correct_start), str(file_stop))] + other_files
