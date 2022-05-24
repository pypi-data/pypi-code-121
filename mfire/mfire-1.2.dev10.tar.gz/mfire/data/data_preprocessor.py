"""
@package lib.data_preprocessor

Data Preprocessor module
"""

# Standard packages
import os
import json
from typing import List, Dict, Tuple, Union, Optional

# Third parties packages
import xarray as xr
import numpy as np

# Own package
from mfire.configuration.rules import Rules
from mfire.utils import xr_utils, exception, Parallel
from mfire.utils.date import Datetime, Timedelta
from mfire.settings import get_logger, RULES_NAMES, Settings

# Logging
LOGGER = get_logger(name="data_preprocessor.mod", bind="preprocess")


class DataPreprocessor:
    """ DataPreprocessor
    Class handling the following data preprocessing according to a given config
    file :
        * parameter extraction from multigrib files
        * concatenation of term by parameter
        * FUTURE : accumulations and combinations of files
        * export to netcdf
    """

    grib_param_dtypes: dict = {
        "discipline": int,
        "parameterCategory": int,
        "productDefinitionTemplateNumber": int,
        "parameterNumber": int,
        "typeOfFirstFixedSurface": str,
        "level": int,
        "typeOfStatisticalProcessing": int,
        "derivedForecast": int,
        "percentileValue": int,
        "scaledValueOfLowerLimit": int,
        "lengthOfTimeRange": int,
        "units": str,
    }
    mandatory_grib_param: list = ["name", "units", "startStep", "endStep", "stepRange"]
    optional_grib_param: list = ["dtype"]

    def __init__(self, data_config_filename: str, rules: str):
        """__init__

        Args:
            data_config_filename (str): Name of the data config file
            rules (str): Name of the rules convention used for files selection. This
                argument must be an element of the RULES_NAMES tuple.
        """
        # Opening the data config file
        LOGGER.info(f"Opening config '{data_config_filename}'", func="__init__")
        with open(data_config_filename, "r") as data_config_file:
            data_config = json.load(data_config_file)
        self.sources_config = data_config["sources"]
        self.preprocessed_config = data_config["preprocessed"]
        self.missing_gribs = []

        # Checking rules convention
        LOGGER.info("Checking rules convention", func="__init__")
        if rules not in RULES_NAMES:
            raise ValueError(
                f"Given rules '{rules}' not among the available rules : {RULES_NAMES}"
            )

        # Opening rules_xls file (for the grib_param_df)
        self.rules = Rules(name=rules)

    def get_grib_params(self, param: str, model: str) -> Dict[str, str]:
        """Method which extract grib's params information from the
        self.grib_param_df, for extraction purposes.

        Args:
            param (str): Param's name frollowing the Promethee standard (defined
                in the RULES csv configuration file)
            model (str): Model name following the Promethee standard (defined in
                the RULES csv standard)

        Returns:
            Dict[str, str]: dict of paired keys/values corresponding to the given
                (param, model)
        """
        try:
            return self.rules.grib_param_df.loc[(param, model)].dropna().to_dict()
        except KeyError:
            LOGGER.warning(
                f"Using 'default' model to retrieve '{param}' backend_kwargs.",
                param=param,
                model=model,
                func="get_backend_kwargs",
            )
            return self.rules.grib_param_df.loc[(param, "default")].dropna().to_dict()

    def get_backend_kwargs(
        self, param: str, model: str, indexpath: str = ""
    ) -> Dict[str, Union[List[str], Dict[str, str], str]]:
        """get_backend_kwargs : Method which extract the exact backend_kwargs
        dictionnary for the cfgrib engine corresponding to the given param and
        model

        Args:
            param (str): Param name following the Promethee standard (defined
                in the RULES csv configuration file)
            model (str): Model name following the Promethee standard (defined
                in the RULES csv configuration file)
            indexpath (str, optional): Path to the directory where to store the
                .idx temporary files created by cfgrib. Defaults to ''.

        Returns:
            dict : Backend_kwargs dictionnary for the cfgrib engine :
                * read_keys : list of keys to read
                * filter_by_keys : dict of paired keys/value corresponding
                    to the given (param, model)
                * indexpath : path where to store the .idx files created by
                    cfgrib. Default to ''.
        """
        raw_dico = self.get_grib_params(param=param, model=model)

        param_keys = dict()
        for key, value in raw_dico.items():
            if key in self.optional_grib_param:
                continue
            if key not in self.grib_param_dtypes:
                raise exception.ConfigurationError(
                    f"Grib param key '{key}' not referenced in the grib_param_dtypes"
                )
            value_type = self.grib_param_dtypes[key]
            param_keys[key] = value_type(value)

        return {
            "read_keys": list(param_keys.keys()) + self.mandatory_grib_param,
            "filter_by_keys": param_keys,
            "indexpath": indexpath,
        }

    def get_param_dtype(self, param: str, model: str) -> str:
        """Gives the supposed dtype of a given param in the given model

        Args:
            param (str): Param's name frollowing the Promethee standard (defined
                in the RULES csv configuration file)
            model (str): Model name following the Promethee standard (defined in
                the RULES csv standard)

        Returns:
            str: Expected dtype of the variable
        """
        return self.get_grib_params(param=param, model=model).get("dtype", "float32")

    def extract_param_from_grib(
        self,
        filename: str,
        param: str,
        model: Optional[str] = "default",
        attrs: Optional[Dict[str, str]] = None,
    ) -> xr.DataArray:
        """Method that extract a given parameter out of a given grib file and
        returns the corresponding xr.DataArray

        Args:
            filename (str): Grib file's name
            param (str): Parameter's name to extract following the Promethee standard.
            model (Optional[str]): Model's name to extract following the Promethee
                standard. Defaults to "default".
            attrs (Optional[Dict[str, str]]): Attributes to add to the extracted
                datarray. Defaults to None.

        Returns:
            xr.DataArray: Extracted parameter.
        """

        log_kwargs = {"filename": filename, "param": param, "model": model}
        backend_kwargs = self.get_backend_kwargs(param, model)

        # Opening file
        try:
            with xr.open_dataarray(
                filename_or_obj=filename,
                engine="cfgrib",
                backend_kwargs=backend_kwargs,
            ) as tmp_da:
                dataarray = tmp_da.load().astype(self.get_param_dtype(param, model))
        except Exception:
            LOGGER.error(
                "Failed to extract parameter from grib file",
                exc_info=True,
                **log_kwargs,
            )
            return None

        # Correcting attributes
        new_attrs = dict(units=backend_kwargs["filter_by_keys"].pop("units", None))
        if attrs is not None:
            new_attrs.update(attrs)

        for attr_key, attr_value in new_attrs.items():
            if attr_value != dataarray.attrs.get(attr_key):
                dataarray.attrs[attr_key] = attr_value

        return dataarray

    @staticmethod
    def extract_param_from_file(
        file_conf: dict,
    ) -> Tuple[str, dict, dict, xr.DataArray]:
        """extract_param_from_file : Extracts a single parameter from a single
        grib file

        Args:
            file_conf (dict): Dictionnary configuring the file to open and the
                param to extract. It contains the following keys :
                * grib_filename : Name of the raw grib file
                * backend_kwargs : backend cfgrib kwargs used to extract the
                    correct parameter
                * preproc_filename : Name of the output netcdf file
                * grib_attrs : Attributes corrections
        """
        dataarray = None
        log_kwargs = dict(
            grib_filename=file_conf["grib_filename"],
            preproc_filename=file_conf["preproc_filename"],
            backend_kwargs=file_conf["backend_kwargs"].get("filter_by_keys"),
            func="extract_param_from_file",
        )
        try:
            with xr.open_dataarray(
                file_conf["grib_filename"],
                engine="cfgrib",
                backend_kwargs=file_conf["backend_kwargs"],
            ) as tmp_da:
                dataarray = tmp_da.load()
        except Exception:
            LOGGER.error("Failed to extract parameter from grib file.", **log_kwargs)
            return (
                file_conf["preproc_filename"],
                file_conf["preproc_attrs"],
                file_conf["postproc"],
                dataarray,
            )

        # Casting dtypes
        try:
            dataarray = dataarray.astype(file_conf["dtype"])
        except TypeError:
            LOGGER.warning(
                f"Failed to cast dtype {file_conf['dtype']} "
                "to the extracted dataarray.",
                **log_kwargs,
            )

        # Attributes corrections
        for attr_key, attr_value in file_conf["grib_attrs"].items():
            if attr_key not in dataarray.attrs:
                dataarray.attrs[attr_key] = attr_value
                continue

            if attr_value == dataarray.attrs.get(attr_key):
                continue

            if (
                attr_key == "units"
                and dataarray.attrs[attr_key] != attr_value
                and attr_value is not None
            ):
                LOGGER.debug(
                    f"Found 'units' = { dataarray.attrs[attr_key]} "
                    f"while '{attr_value}' expected. "
                    f"Changing 'units' to '{attr_value}'.",
                    **log_kwargs,
                )
                dataarray.attrs[attr_key] = attr_value

        return (
            file_conf["preproc_filename"],
            file_conf["preproc_attrs"],
            file_conf["postproc"],
            dataarray,
        )

    @staticmethod
    def concat_dataarrays(dict_das: dict, preproc_filename: str = None) -> xr.DataArray:
        """concat_dataarrays : concatenate a group of dataarrays into a single
        and apply cumulation preprocessing

        Args:
            dict_das (dict): Dictionary with all the dataarrays

        Returns:
            xr.DataArray: Concatenated and preprocessed dataarray
        """
        # Avant cela on va mettre les fichiers sur la grille désirée
        das = []
        source_steps = []
        GRIB_StepRange = []
        grid_changes = 0
        var_to_delete = set(["heightAboveGround", "time", "step", "surface"])
        LOGGER.debug(f"{preproc_filename}: {len(dict_das['file'])} files")
        for elt in sorted(dict_das["file"], key=lambda x: x["da"].valid_time.values):
            source_grid = elt["preproc"].get("source_grid")
            preproc_grid = elt["preproc"].get("preproc_grid")
            source_steps.append(int(elt["preproc"].get("source_step", 1)))
            # On etend du nombre de step present dans le fichier en entree.
            GRIB_StepRange.extend(
                [elt["da"].attrs["GRIB_endStep"] - elt["da"].attrs["GRIB_startStep"]]
                * elt["da"].step.size
            )
            # On vire certaine variables
            drop_var = set(elt["da"].coords).intersection(var_to_delete)
            elt["da"] = elt["da"].drop_vars(list(drop_var))
            if source_grid != preproc_grid:
                grid_changes += 1
                da = xr_utils.change_grid(elt["da"], preproc_grid)
                das.append(da)
            else:
                das.append(elt["da"])
        LOGGER.debug(
            "Changement de grilles effectués",
            number_grid_change=grid_changes,
            preproc_filename=preproc_filename,
            func="concat_dataarrays",
        )

        # Maintenant on concatene les differentes steps.
        concat_da = xr.concat(das, dim="valid_time")

        # on crée le stepsize_da pour les cumuls
        stepsize_da = xr.DataArray(GRIB_StepRange, coords=[concat_da.valid_time])

        # on trie
        concat_da = concat_da.sortby("valid_time")
        stepsize_da = stepsize_da.sortby("valid_time")

        # Enforcing variable name
        variable_name = dict_das["postproc"].get("param")
        concat_da.name = variable_name

        da_out = concat_da

        # On regarde si on doit accumuler.
        accum = dict_das["postproc"].get("accum")
        if accum is not None:
            LOGGER.debug(
                "Doing accumulation",
                preproc_filename=preproc_filename,
                func="concat_dataarrays",
            )
            # On va changer le nom de la variable pour inclure l'accumulation
            l_var = variable_name.split("__")
            l_var[0] = l_var[0] + str(accum)
            concat_da.name = "__".join(l_var)
            LOGGER.debug(
                "Fixing promethee name for accumulation",
                old_name=variable_name,
                new_name=concat_da.name,
                preproc_filename=preproc_filename,
                func="concat_dataarrays",
            )
            da_out = xr_utils.compute_sum_futur(
                concat_da, stepout=accum, var="valid_time", da_step=stepsize_da,
            ).sel(valid_time=concat_da.valid_time)

        elif (np.array(source_steps) != dict_das["postproc"]["step"]).any():
            LOGGER.info(
                "source_step != target_step, passage par xr_utils.fill_dataarray",
                source_steps=source_steps,
                target_step=dict_das["postproc"]["step"],
                preproc_filename=preproc_filename,
                dim="valid_time",
            )
            da_out = xr_utils.fill_dataarray(
                da=concat_da,
                source_steps=source_steps,
                target_step=dict_das["postproc"]["step"],
                dim="valid_time",
                freq_base="h",
            )

        LOGGER.debug(
            f"da_out={da_out}",
            preproc_filename=preproc_filename,
            source_steps=source_steps,
            target_step=dict_das["postproc"]["step"],
            start=str(dict_das["postproc"]["start"]),
            stop=str(dict_das["postproc"]["stop"]),
        )
        return xr_utils.slice_dataarray(
            da=da_out,
            start=dict_das["postproc"]["start"],
            stop=dict_das["postproc"]["stop"],
            dim="valid_time",
        )

    def concat_export_dataarrays(self, dataarray_group: Tuple[str, dict]) -> bool:
        """concat_export_dataarrays : Concatenate and export to netcdf a
        group of xarray DataArrays

        Args:
            dataarray_group (tuple) : This tuple has two components :
                * ouput_filename (str) : name of the netcdf file to be exported
                * dict_das (dictionnaire) :

        Returns:
            bool : True if the export went correctly
        """
        preproc_filename, dict_das = dataarray_group
        try:
            concat_da = self.concat_dataarrays(
                dict_das=dict_das, preproc_filename=preproc_filename
            )
        except Exception:
            LOGGER.error(
                f"Failed to concat {preproc_filename}",
                func="concat_export_dataarrays",
                preproc_filename=preproc_filename,
                exc_info=True,
            )
            return False
        LOGGER.debug(f"{preproc_filename} dataarray: {concat_da}")
        try:
            concat_da.to_netcdf(preproc_filename)
        except Exception:
            LOGGER.error(
                f"Failed to export {preproc_filename}",
                func="concat_export_dataarrays",
                preproc_filename=preproc_filename,
                exc_info=True,
            )
            return False
        return os.path.isfile(preproc_filename)

    def build_stack(self) -> List[dict]:
        """build_stack : Builds a kind of "task processing stack"

        Returns:
            list : List of dictionnaries. Each dictionnary is the
                preprocessing config for a speficific file to extract.
        """
        stack = []
        # Loop on all the preprocessed files configurations to create
        # a 'raw stack', i.ea list of all the preprocessing config dicts
        for preproc_id, preproc_config in self.preprocessed_config.items():
            preproc_rh = preproc_config["resource_handler"][0]
            preproc_filename = preproc_rh["local"]
            os.makedirs(os.path.dirname(preproc_filename), exist_ok=True)
            root_param = preproc_config["agg"]["param"]
            # Retrieving all useful post-proc information
            preproc_rundate = Datetime(preproc_rh["date"])
            postproc = {
                "step": preproc_rh["step"],
                "start": preproc_rundate + Timedelta(hours=preproc_rh["begintime"]),
                "stop": preproc_rundate + Timedelta(hours=preproc_rh["endtime"]),
            }
            postproc.update(preproc_config["agg"])

            # file_conf_list = []
            for source_id, source_info in preproc_config["sources"].items():
                for term in source_info["terms"]:
                    if str(term) not in self.sources_config[source_id]:
                        LOGGER.error(
                            "Inconsistency between term given by preprocessed file "
                            "and available source terms",
                            preproc_id=preproc_id,
                            source_id=source_id,
                            term=term,
                            func="build_stack",
                        )
                        continue
                    if len(self.sources_config[source_id][str(term)]) == 0:
                        LOGGER.error(
                            "Source file configuration empty.",
                            source_id=source_id,
                            term=term,
                            func="build_stack",
                        )
                        continue

                    source_conf = self.sources_config[source_id][str(term)][0]
                    # checking if the source_conf["local"] grib is missing or empty
                    grib_filename = source_conf["local"]
                    if grib_filename in self.missing_gribs:
                        # if grib is already labeled as missing
                        continue
                    else:
                        if not os.path.isfile(grib_filename):
                            # if grib is missing and not already labeled as missing
                            LOGGER.error(
                                "Missing source grib file.",
                                grib_filename=grib_filename,
                                source_id=source_id,
                                term=term,
                                func="build_stack",
                            )
                            self.missing_gribs.append(grib_filename)
                            continue

                        if os.path.getsize(grib_filename) < 1000:
                            LOGGER.error(
                                "Source grib file empty (size = "
                                f"{os.path.getsize(grib_filename)} octets).",
                                grib_filename=grib_filename,
                                source_id=source_id,
                                term=term,
                                func="build_stack",
                            )
                            self.missing_gribs.append(grib_filename)
                            continue

                    try:
                        backend_kwargs = self.get_backend_kwargs(
                            root_param, source_conf["model"]
                        )
                        dtype = self.get_param_dtype(root_param, source_conf["model"])
                    except Exception:
                        LOGGER.error(
                            "Failed to retrieve backend_kwargs for (param, model)"
                            f" = ({root_param}, {source_conf['model']}).",
                            grib_filename=grib_filename,
                            source_id=source_id,
                            term=term,
                            func="build_stack",
                            exc_info=True,
                        )
                        continue

                    # Case of a accum param with lengthOfTimeRange
                    if "lengthOfTimeRange" in backend_kwargs["filter_by_keys"]:
                        backend_kwargs["filter_by_keys"]["lengthOfTimeRange"] = int(
                            source_info["step"]
                        )

                    units = backend_kwargs["filter_by_keys"].pop("units", None)

                    file_conf = {
                        "name": f"{source_id}_{term}_to_{preproc_id}",
                        "grib_filename": source_conf["local"],
                        "backend_kwargs": backend_kwargs,
                        "dtype": dtype,
                        "preproc_filename": preproc_filename,
                        "grib_attrs": {
                            "PROMETHEE_z_ref": preproc_rh["geometry"],
                            "units": units,
                        },
                        "postproc": postproc,
                        "preproc_attrs": {
                            "source_grid": source_conf["geometry"],
                            "preproc_grid": preproc_rh["geometry"],
                            "source_step": int(source_info["step"]),
                        },
                    }

                    # file_conf_list += [file_conf]
                    stack += [file_conf]

        return stack

    def preprocess(self, nproc: int) -> None:
        """preprocess : Preprocess all the data config dict in self.data_config

        Args:
            nproc (int): Number of CPUs to be used in parallel
        """
        # Building the preprocessing stack
        stack = self.build_stack()

        grouped_das = dict()

        def append_result(res: Tuple[str, dict, dict, xr.DataArray]) -> None:
            """Local function to progressively append extracted results to the
            grouped_das dictionnary.
            """
            preproc_filename, preproc, postproc, dataarray = res
            if dataarray is None:
                LOGGER.error(f"Extracted grib empty for {preproc_filename}.")
                return None
            grouped_das.setdefault(preproc_filename, {}).setdefault("file", []).append(
                {"da": dataarray, "preproc": preproc}
            )
            grouped_das[preproc_filename]["postproc"] = postproc

        # Logging building stack results
        parallel = Parallel(processes=nproc)
        for file_conf in stack:
            parallel.apply(
                self.extract_param_from_file,
                args=(file_conf,),
                callback=append_result,
                name=file_conf["name"],
            )
        parallel.run(timeout=Settings().timeout)
        parallel.clean()

        # Concat and export
        for dataarray_group in grouped_das.items():
            parallel.apply(
                self.concat_export_dataarrays,
                args=(dataarray_group,),
                name=dataarray_group[0],
            )
        parallel.run(timeout=(Settings().timeout / 2))
