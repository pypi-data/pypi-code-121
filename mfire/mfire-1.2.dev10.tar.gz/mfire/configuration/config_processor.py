"""
@package configuration.config_processor

Config processor module
"""

# Standard packages
import os
import tarfile
import time
from copy import deepcopy
from typing import List, Optional, Union, Tuple

from multiprocessing import Manager

# Third parties packages
import pandas as pd

# Own package
from mfire.settings import get_logger, Settings, LOCAL, TEXT_ALGO
from mfire.utils import MD5, JsonFile, Parallel
from mfire.utils.date import Datetime, Timedelta
from mfire.utils.formatter import TagFormatter
from mfire.utils.exception import ConfigurationError
from mfire.configuration.geos import FeatureConfig, FeatureCollectionConfig, MaskConfig
from mfire.configuration.resources import MaskRHConfig
from mfire.configuration.periods import PeriodCollectionConfig
from mfire.configuration.configs import VersionConfig
from mfire.configuration.rules import Rules
import mfire.composite as composite


# Logging
LOGGER = get_logger(name="config_processor.mod", bind="config_processor")

DEFAULT_TIME_DIMENSION = "valid_time"  # TODO: put it in the csv settings files
DEFAULT_COMPUTE_LIST = ["density", "extrema", "representative", "summary"]

EventComposites = Union[
    composite.EventComposite, composite.EventBertrandComposite,
]
ComponentComposites = Union[
    composite.RiskComponentComposite, composite.TextComponentComposite,
]


# Main class : ConfigProcessor
class ConfigProcessor:
    """ConfigProcessor : Class which parses a configuration file
    (tar archive or json) and produces three configurations out of it :

    * a mask configuration (self.mask_config): config following the geojson
    standard which describes all the geographical geos used in production.
    This file aims to be used by the mask creation module lately.

    * a data configuration (self.data_config) : config which describes all
    the raw data files (using the Vortex Standard) necessary for production
    and all the pre-processings that must be done before production (parameter
    extraction, accumulations, combinations, etc.)
    This file aims to be used by the data preprocessing module lately.

    * a production configuration (self.prod_config) : config which describes
    all the files necessary for production and all the processing to be done
    in order to produce Promethee data (risks and texts).
    This file aims to be used by the core module lately.
    """

    def __init__(self, config_filename: str, rules: str, drafting_datetime: Datetime):
        """__init__

        Args:
            config_filename (str): path to the configuration file to process
            rules (str): Name of the rules convention used for files selection. This
                argument must belong to the RULES_NAMES list.
            drafting_datetime (datetime.datetime): Promethee's drafting datetime
        """
        global LOGGER
        self.settings = Settings(config_filename=config_filename)
        # Opening the conf file
        LOGGER.info("Creating ConfigProcessor ...", func="__init__")
        self.config = []
        try:
            if tarfile.is_tarfile(config_filename):
                LOGGER.info("Config is a tarfile", func="__init__")
                with tarfile.open(config_filename) as config_tar:
                    members = config_tar.getmembers()
                    for i, config_file in enumerate(members):
                        config = JsonFile(config_tar.extractfile(config_file)).load()
                        LOGGER.info(
                            f"File {i+1}/{len(members)} loaded", func="__init__"
                        )
                        if isinstance(config, list):
                            self.config += config
                        elif isinstance(config, dict):
                            self.config += [config]
                        else:
                            raise ConfigurationError(
                                f"Configuration is a {type(config)},"
                                " while list or dict expected."
                            )
            elif config_filename.endswith(".json"):
                LOGGER.info("Config is a JSON file", func="__init__")
                self.config += JsonFile(config_filename).load()
                LOGGER.info("File loaded", func="__init__")
        except TypeError:
            # Cas où l'on passe un IOBase.
            self.config = JsonFile(config_filename).load()

        # Checking rules convention
        LOGGER.info("Initiating rules...", func="__init__")
        self.rules = Rules(name=rules, drafting_datetime=drafting_datetime)
        LOGGER.info("Rules validated...", func="__init__")

        self.data_config = {
            "config_version": self.hashcode,
            "sources": dict(),
            "preprocessed": dict(),
        }
        self.prod_config = dict()
        self.mask_config = dict()

    @property
    def hashcode(self) -> str:
        """hashcode (Property)

        Returns:
            str : hexadecimal hash key of the config's MD5 checksum
        """
        return MD5(self.config).hash

    @staticmethod
    def int_timedelta(d0: Datetime, d1: Datetime):
        """int_timedelta : Static method returning the difference between 2 dates
        in hours (as an integer)

        Args:
            d0 (Datetime): First date
            d1 (Datetime): Second date

        Returns:
            int : Diffence in hours between d0 and d1
        """
        return int((Datetime(d1) - Datetime(d0)) // Timedelta(hours=1))

    def get_components_params(self, compo_config):
        """get_components_params : Method which returns all the parameters
        used in the component or linked to the component.

        Args:
            compo_config (dict): Component config

        Returns:
            set : Set of parameter used in the component or linked.
        """
        params = []
        if compo_config["type"] == "risk":
            for level in compo_config["levels"]:
                for event in level["elementsEvent"]:
                    full_root_param, accum = self.rules.param_to_description(
                        event["field"]
                    )
                    if full_root_param not in self.rules.param_link_df:
                        params += [event["field"]]
                        continue
                    linked_root_params = [
                        p.split("__")
                        for p in self.rules.param_link_df[full_root_param]
                        .dropna()
                        .index
                    ]
                    params += [
                        self.rules.description_to_param(p, l, accum)
                        for p, l in linked_root_params
                    ]
        elif compo_config["type"] == "text":
            for weather in compo_config["weather"]:
                params += set(
                    TEXT_ALGO[weather["id"]][weather.get("algo", "generic")][
                        "params"
                    ].values()
                )
                if "field" in weather["condition"]:
                    params += [weather["condition"]["field"]]
        else:
            raise ConfigurationError(
                f"Unexpected component type : {compo_config['type']}."
            )
        return set(params)

    def useable_geometries(self, geo_config: FeatureConfig) -> List[str]:
        """useable_geometries : Returns the useable geometries with
        a geographical zone according to its configuration.

        Args:
            geo_config (FeatureConfig): Geograpghical zone's configuration

        Returns:
            List[str] : list of useable geometries's names.
        """
        return [
            gname
            for gname, bounds in self.rules.get_bounds()
            if geo_config.is_in(*bounds)
        ]

    def create_rh(
        self,
        file_id: str,
        term: Datetime = None,
        param: str = None,
        alternate: tuple = None,
    ) -> dict:
        # basic infos from dataframe
        file_info = self.rules.get_file_info(file_id)

        # resource_handler
        resource_columns = [
            "kind",
            "model",
            "date",
            "geometry",
            "cutoff",
            "origin",
            "nativefmt",
        ]
        rh_dico = file_info[resource_columns].to_dict()
        rh_dico["date"] = str(Datetime(file_info["date"]))
        rh_dico["vapp"] = file_info.get("vapp", self.settings.vapp)
        rh_dico["vconf"] = file_info.get("vconf", self.settings.vconf)
        rh_dico["experiment"] = file_info.get("experiment", self.settings.experiment)
        rh_dico["block"] = file_info["block"]
        rh_dico["namespace"] = file_info["namespace"]
        rh_dico["format"] = file_info["nativefmt"]

        # case if we create a source rh
        if file_id in self.rules.source_files_df.index and term is not None:
            rh_dico["term"] = self.int_timedelta(file_info["date"], term)
            role_name = f"{file_id} {term}"

        # case if we create a preprocessed rh
        elif file_id in self.rules.preprocessed_files_df.index and param is not None:
            rh_dico["param"] = param
            rh_dico["begintime"] = self.int_timedelta(
                file_info["date"], file_info["start"]
            )
            rh_dico["endtime"] = self.int_timedelta(
                file_info["date"], file_info["stop"]
            )
            rh_dico["step"] = int(file_info["step"])
            role_name = f"{file_id} {param}"

        # role or alternate
        if alternate is None:
            rh_dico["local"] = os.path.join(
                self.settings.data_dirname,
                TagFormatter().format_tags(LOCAL[file_info["kind"]], rh_dico),
            )
            rh_dico["role"] = role_name

        else:
            rh_dico["alternate"], rh_dico["local"] = alternate

        rh_dico["fatal"] = False
        rh_dico["now"] = True
        return rh_dico

    def create_full_file_config(
        self, file_id: str, term: Datetime = None, param: str = None
    ) -> list:
        # creating main rh
        role_rh = self.create_rh(file_id, term=term, param=param)
        rhs = [role_rh]

        # adding alternates
        current_file_id = file_id
        for _ in range(self.settings.alternate_max):
            current_file_id = self.rules.get_alternate(current_file_id)
            if current_file_id not in self.rules.files_ids:
                break
            rhs += [
                self.create_rh(
                    current_file_id,
                    term=term,
                    param=param,
                    alternate=(role_rh["role"], role_rh["local"]),
                )
            ]

        return rhs

    def source_files_terms(self, file_id: str, param: str, accum: int) -> dict:
        """source_files_terms : Returns source files id and term needed for a given
        preprocessed file id, a complete parameter name, an accumulation period
        and start/stop datetimes. It also computes the source files configurations
        and stores them into the self.data_config['sources'].

        Args:
            file_id (str): Preprocessed file id
            param (str): Complete Parameter name
            accum (int): Accumulation period in hours

        Returns:
            dict : Dictionnary with the following structure :
                {
                    <source_file_id> : [terms]
                }
        """
        preprocessed_file_info = self.rules.get_file_info(file_id)
        source_files_list = [
            source_file_id.strip()
            for source_file_id in self.rules.files_links_df.loc[param, file_id].split(
                ","
            )
        ]
        source_files_dico = dict()
        current_start = preprocessed_file_info["start"]
        # Adding virtual terms due to accumulation (for preproc files)
        preproc_stop = preprocessed_file_info["stop"]
        preproc_step = Timedelta(hours=int(preprocessed_file_info["step"]))
        accum_td = Timedelta(hours=int(accum)) if accum is not None else Timedelta(0)
        virtual_stop = preproc_stop + accum_td
        virtual_range = range(1, int((virtual_stop - preproc_stop) / preproc_step) + 1)
        virtual_terms = [preproc_stop + preproc_step * i for i in virtual_range]
        for source_file_id in source_files_list:
            # We check until virtual stop in case of accumulation
            if virtual_stop <= current_start:
                break
            if source_file_id not in self.rules.source_files_df.index:
                continue
            source_file_info = self.rules.get_file_info(source_file_id)
            source_files_dico[source_file_id] = {
                "terms": [
                    self.int_timedelta(source_file_info["date"], term)
                    for term in source_file_info["terms"]
                    if (
                        term >= current_start
                        and term in preprocessed_file_info["terms"] + virtual_terms
                    )
                ],
                "step": int(source_file_info["step"]),
            }
            current_start = source_file_info["terms"][-1] + preproc_step

            if source_file_id in self.data_config["sources"]:
                continue
            self.data_config["sources"][source_file_id] = dict()
            for term in source_file_info["terms"]:
                term_int = self.int_timedelta(source_file_info["date"], term)
                self.data_config["sources"][source_file_id][
                    term_int
                ] = self.create_full_file_config(file_id=source_file_id, term=term)
        return source_files_dico

    def change_slice_to_islice(self, slice_time, file_id):
        """change_slice_to_islice: Function which enable to go from slice (in hours)
        to islice (which select elements)

        Args:
            slice_time (tuple): A tuple describing the first and last hour to take
            file_id (str): Preprocessed file id

        Returns:
            [tuple]: New tuple
        """
        file_info = self.rules.get_file_info(file_id)
        date = file_info["date"]
        start = file_info["start"]
        td_start = self.int_timedelta(date, start)
        step = int(file_info["step"])
        n_start = int((slice_time[0] - td_start) / step)
        n_stop = int((slice_time[1] - td_start) / step)
        return (n_start, n_stop + 1)

    def preprocessed_rh(self, file_id, param):
        key = " ".join([file_id, param])
        if key in self.data_config["preprocessed"]:
            return self.data_config["preprocessed"][key]["resource_handler"]

        return self.create_full_file_config(file_id, param=param)

    def list_components_configs(self, prod_idx):
        """list_components_config : list all the components configurations
        contained in a prod_idx configuration.

        Args:
            prod_idx (int): Production index in the self.config
        """
        return deepcopy(self.config[prod_idx]["components"])

    def get_geo(self, config: dict) -> FeatureCollectionConfig:
        """Patch to transform config geos config such as it is compatible
        with GeoJSON format

        Args:
            config (dict): geo configs

        Returns:
            FeatureCollection: Corresponding feature collection
        """
        return FeatureCollectionConfig(**config)

    def get_configuration_datetime(self):
        """Retourne la date de configuration d'un bulletin
        Args:
            prod_idx : le bulletin en quesiton
        Returns:
            La date au format promethee.
            Par défaut on retourne le 1er Janvier 1901.
        """
        return Datetime(self.config[0].get("date_config"))

    @staticmethod
    def get_new_threshold(threshold: dict) -> composite.Threshold:
        return composite.Threshold(
            threshold=threshold["threshold"],
            comparison_op=threshold["comparisonOp"],
            units=threshold["units"],
        )

    @staticmethod
    def get_aggregation(
        aggregation: dict, mask_file: str, grid_name: str = "",
    ) -> composite.Aggregation:
        kwargs = aggregation.get("kwargs")
        if kwargs is None:
            return composite.Aggregation(**aggregation)
        # Filling new kwargs
        new_kwargs = dict()

        # dr: float
        if "dr" in kwargs:
            new_kwargs["dr"] = kwargs["dr"]
        elif "drConditional" in kwargs:
            new_kwargs["dr"] = kwargs["drConditional"]
        elif "drCentralZone" in kwargs:
            new_kwargs["dr"] = kwargs["drCentralZone"]
        new_kwargs["dr"] = float(new_kwargs["dr"])
        if new_kwargs["dr"] > 1 and new_kwargs["dr"] <= 100:
            new_kwargs["dr"] = new_kwargs["dr"] / 100.0

        # central_weight: Optional[int]
        if "centralWeight" in kwargs:
            new_kwargs["central_weight"] = kwargs["centralWeight"]

        # outer_weight: Optional[int]
        if "outerWeight" in kwargs:
            new_kwargs["outer_weight"] = kwargs["outerWeight"]

        # central_mask_id: Optional[GeoComposite]
        for central_key in ("central_mask_id", "centralZone", "centralZoneConditional"):
            central_mask_id = kwargs.get(central_key)
            if central_mask_id is not None:
                new_kwargs["central_mask_id"] = composite.GeoComposite(
                    file=mask_file, mask_id=central_mask_id, grid_name=grid_name,
                )
        return composite.Aggregation(method=aggregation["method"], kwargs=new_kwargs)

    def get_new_event(
        self,
        event: dict,
        compo_config: dict,
        single_data_config: dict,
        geos_base: dict,
        file_id: str,
        start_stop: Tuple[Datetime, Datetime],
        aggregation_aval: Optional[dict] = None,
    ) -> EventComposites:
        current_data_config = single_data_config[(file_id, event["field"])][0]
        grid_name = current_data_config["geometry"]
        global LOGGER
        LOGGER = LOGGER.bind(
            param=event["field"], grid_name=grid_name, func="get_new_event",
        )

        # list of stuff to pass on:
        composite_class = composite.EventComposite
        new_event = dict()
        # field: FieldComposite
        new_event["field"] = composite.FieldComposite(
            file=current_data_config["local"],
            name=event["field"],
            grid_name=grid_name,
            selection={"slice": {"valid_time": start_stop}},
        )

        # category: Category
        new_event["category"] = event["category"]

        # plain: Threshold
        new_event["plain"] = self.get_new_threshold(event["plain"])

        # mountain: Optional[Threshold]
        if "mountain" in event:
            new_event["mountain"] = self.get_new_threshold(event["mountain"])

        # mountain_altitude: Optional[int]
        if "altitude" in event:
            new_event["mountain_altitude"] = event["altitude"][0]["mountainThreshold"]

        # altitude: Optional[AltitudeComposite] = AltitudeComposite()
        new_event["altitude"] = composite.AltitudeComposite(
            grid_name=grid_name,
            alt_min=compo_config.get("alt_min"),
            alt_max=compo_config.get("alt_max"),
        )

        # geos: Optional[GeoComposite]
        new_event["geos"] = composite.GeoComposite(grid_name=grid_name, **geos_base,)

        # time_dimension: Optional[str]
        new_event["time_dimension"] = DEFAULT_TIME_DIMENSION

        # aggregation: Optional[Aggregation]
        if "aggregation" in event:
            new_event["aggregation"] = self.get_aggregation(
                event["aggregation"], geos_base["file"], grid_name
            )

        # aggregation_aval: Optional[Aggregation]
        new_event["aggregation_aval"] = self.get_aggregation(
            aggregation_aval, geos_base["file"], grid_name
        )

        # compute_list: Optional[list]
        new_event["compute_list"] = DEFAULT_COMPUTE_LIST

        # checking if in case of a BertrandEvent
        root_param = event["field"].split("__")[0]
        if root_param in self.rules.agg_param_df.index:
            # Cas special des arguments pour riskBertrand
            tmp_param, accum = self.rules.param_to_description(event["field"])
            model_step = int(self.rules.get_file_info(file_id)["step"])
            LOGGER.info(
                f"Parameter {event['field']} is inside agg_param_list. "
                "Checking for Bertrand risk.",
            )
            if accum > model_step:
                base_param, tmp_l = tmp_param.split("__")
                param_base = self.rules.description_to_param(
                    base_param, tmp_l, model_step
                )
                LOGGER.info(
                    "Adding information for Bertrand risk. "
                    f"Param de base a cette echeance {param_base}",
                )
                new_event["field_1"] = composite.FieldComposite(
                    file=self.preprocessed_rh(file_id, param_base)[0]["local"],
                    name=param_base,
                    grid_name=grid_name,
                    selection={"slice": {"valid_time": start_stop}},
                )
                new_event["cum_period"] = accum
                composite_class = composite.EventBertrandComposite

        LOGGER.try_unbind("param", "grid_name", "func")
        return composite_class(**new_event)

    def get_new_level(
        self,
        level: dict,
        compo_config: dict,
        single_data_config: dict,
        geos_base: dict,
        file_id: str,
        start_stop: Tuple[Datetime, Datetime],
    ) -> composite.LevelComposite:
        global LOGGER
        LOGGER = LOGGER.bind(level=level["level"])

        new_level = {
            "level": level["level"],
            "probability": level.get("probability"),
            "logical_op_list": level["logicalOpList"],
            "aggregation_type": level["aggregationType"],
            "time_dimension": DEFAULT_TIME_DIMENSION,
            "compute_list": DEFAULT_COMPUTE_LIST,
        }

        # aggregation: Optional[Aggregation]
        aggregation_aval = None
        if "aggregation" in level:
            aggregation_aval = level["aggregation"]
            new_level["aggregation"] = self.get_aggregation(
                aggregation_aval, geos_base["file"], None
            )

        # localisation: LocalisationConfig
        new_level["localisation"] = composite.LocalisationConfig(
            compass_split=compo_config.get("compass_split", True),
            altitude_split=compo_config.get("altitude_split", True),
            geos_descriptive=compo_config.get("geos_descriptive", []),
        )

        # elements_event: List[Union[EventBertrandComposite, EventComposite]]
        new_level["elements_event"] = []
        for event in level["elementsEvent"]:
            new_level["elements_event"].append(
                self.get_new_event(
                    event=event,
                    compo_config=compo_config,
                    single_data_config=single_data_config,
                    geos_base=geos_base,
                    file_id=file_id,
                    start_stop=start_stop,
                    aggregation_aval=aggregation_aval,
                )
            )
        LOGGER.try_unbind("level")
        return composite.LevelComposite(**new_level)

    def get_new_weather(
        self,
        weather: dict,
        single_data_config: dict,
        geos_base: dict,
        file_id: str,
        start_time: Datetime,
        stop_time: Datetime,
        processed_compo_config: dict(),
    ) -> dict:
        new_weather = deepcopy(weather)
        params = TEXT_ALGO[weather["id"]][weather.get("algo", "generic")][
            "params"
        ].items()
        # params: FieldComposite
        new_weather["params"] = {
            key: composite.FieldComposite(
                file=single_data_config[(file_id, param)][0]["local"],
                selection={"slice": {"valid_time": (start_time, stop_time)},},
                grid_name=single_data_config[(file_id, param)][0]["geometry"],
                name=single_data_config[(file_id, param)][0]["param"],
            )
            for key, param in params
        }

        # geos: GeoComposite
        for key, param in params:
            new_weather["geos"] = composite.GeoComposite(
                grid_name=single_data_config[(file_id, param)][0]["geometry"],
                **geos_base,
            )

        # localisation: LocalisationConfig
        new_weather["localisation"] = composite.LocalisationConfig(
            compass_split=processed_compo_config["compass_split"],
            altitude_split=processed_compo_config["altitude_split"],
            geos_descriptive=processed_compo_config["geos_descriptive"],
        )

        # condition: EventComposite
        new_weather["condition"] = composite.EventComposite(
            field=composite.FieldComposite(
                file=single_data_config[(file_id, weather["condition"]["field"])][0][
                    "local"
                ],
                selection={"slice": {"valid_time": (start_time, stop_time)},},
                grid_name=single_data_config[(file_id, weather["condition"]["field"])][
                    0
                ]["geometry"],
                name=single_data_config[(file_id, weather["condition"]["field"])][0][
                    "param"
                ],
            ),
            plain=self.get_new_threshold(weather["condition"]["plain"]),
            category=weather["condition"]["category"],
            geos=composite.GeoComposite(
                grid_name=single_data_config[(file_id, weather["condition"]["field"])][
                    0
                ]["geometry"],
                **geos_base,
            ),
            aggregation=self.get_aggregation(
                weather["condition"]["aggregation"], geos_base
            ),
            altitude=composite.AltitudeComposite(
                grid_name=single_data_config[(file_id, weather["condition"]["field"])][
                    0
                ]["geometry"],
            ),
        )

        # altitude: champ non implémenté dans la configuration métronome
        if "mountain" in weather["condition"]:
            new_weather["altitude"] = weather["condition"]["altitude"]
            for cond in new_weather["condition"]:
                cond.mountain = self.get_new_threshold(weather["condition"]["mountain"])
                cond.altitude = weather["condition"]["altitude"]

        return new_weather

    def process_single_component(
        self,
        compo_config: dict,
        single_data_config: dict,
        single_mask_config: MaskConfig,
        processed_periods: composite.PeriodCollection,
        processed_hazards: dict,
    ) -> List[ComponentComposites]:
        """process_single_component :

        Args:
            compo_config (dict): [description]
            single_data_config (dict): [description]
        """
        global LOGGER
        LOGGER = LOGGER.bind(
            compo_id=compo_config.get("id"), period_id=compo_config.get("period"),
        )
        processed_compo_config = deepcopy(compo_config)
        # Component's params
        params = self.get_components_params(compo_config)
        # Component's period
        processed_period = processed_periods.get(compo_config.get("period"))
        processed_compo_config["period"] = processed_period
        if compo_config["type"] == "risk":
            if "name" not in processed_compo_config:
                LOGGER.info("Filling with hazard name", func="process_single_component")
                processed_compo_config["name"] = processed_hazards[
                    compo_config["hazard"]
                ].get("name")

            if "otherNames" not in processed_compo_config:
                processed_compo_config["otherNames"] = processed_hazards[
                    compo_config["hazard"]
                ].get("otherNames")
        # Component's geos
        files_groups = dict()
        for mask_id in compo_config["geos"]:
            LOGGER = LOGGER.bind(mask_id=mask_id)
            geometries = self.useable_geometries(
                next(
                    feature
                    for feature in single_mask_config.geos.features
                    if feature.id == mask_id
                )
            )
            best_files = tuple(
                self.rules.best_preprocessed_files(
                    start=processed_period.start,
                    stop=processed_period.stop,
                    geometries=geometries,
                    params=params,
                )
            )
            if len(best_files) == 0:
                LOGGER.error(
                    f"No preprocessed file found for start={processed_period.start}; "
                    f"stop={processed_period.stop}; geometries={geometries}; "
                    f"params={params}",
                )

            if best_files in files_groups:
                files_groups[best_files] += [mask_id]
            else:
                files_groups[best_files] = [mask_id]
        LOGGER = LOGGER.try_unbind("mask_id")

        LOGGER.info(
            "Files group created",
            func="process_single_component",
            params=list(params),
            files_groups=[
                [list(best_files), list(geos)]
                for best_files, geos in files_groups.items()
            ],
        )

        new_components_list = []
        for best_files, geos in files_groups.items():
            for file_id, _, _ in best_files:
                for param in params:
                    if (file_id, param) not in single_data_config:
                        single_data_config[(file_id, param)] = self.preprocessed_rh(
                            file_id, param
                        )

            new_compo_config = deepcopy(processed_compo_config)
            geos_base = {"file": single_mask_config.file, "mask_id": geos}
            new_compo_config["geos"] = geos
            new_compo_config["time_dimension"] = DEFAULT_TIME_DIMENSION
            new_compo_config["production_datetime"] = self.rules.bulletin_datetime
            new_compo_config[
                "configuration_datetime"
            ] = self.get_configuration_datetime()
            if new_compo_config["type"] == "text":
                new_compo_config["weathers"] = list()
                for weather in processed_compo_config["weather"]:
                    new_compo_config["weathers"] = [
                        self.get_new_weather(
                            weather=weather,
                            single_data_config=single_data_config,
                            geos_base=geos_base,
                            file_id=file_id,
                            start_time=start_time,
                            stop_time=stop_time,
                            processed_compo_config=processed_compo_config,
                        )
                        for file_id, start_time, stop_time in best_files
                    ]

                new_compo = composite.TextComponentComposite(**new_compo_config)
            else:
                new_compo_config["levels"] = []
                for file_id, start_time, stop_time in best_files:
                    LOGGER = LOGGER.bind(file_id=file_id)
                    new_compo_config["levels"] += [
                        self.get_new_level(
                            level=level,
                            compo_config=compo_config,
                            single_data_config=single_data_config,
                            geos_base=geos_base,
                            file_id=file_id,
                            start_stop=(start_time, stop_time),
                        )
                        for level in processed_compo_config["levels"]
                    ]
                LOGGER = LOGGER.try_unbind("file_id")
                new_compo = composite.RiskComponentComposite(**new_compo_config)
            new_components_list.append(new_compo)
        return new_components_list

    def process_single_config(self, prod_idx):
        """process_single_config

        Args:
            config (dict): configuration of a single bulletin

        Returns:
            (dict, set, dict): Tuple containing :
                * the extracted mask configuration dictionnary (geoJSON
                standard)
                * the set of all the data_files (filename and params) necessary
                for production
                * the extracted production configuration dictionnary
        """
        t0 = time.time()
        config = self.config[prod_idx]
        prod_hashcode = MD5(config).hash
        prod_id = config.get("production_id", prod_idx)
        prod_name = config.get("production_name", f"production_{prod_id}")
        global LOGGER
        LOGGER = LOGGER.bind(prod_id=prod_id)
        LOGGER.info("Starting process_single_config", func="process_single_config")
        # Mask configs
        mask_file = os.path.join(self.settings.mask_dirname, f"{prod_id}.nc")
        single_mask_config = MaskConfig(
            file=mask_file,
            id=prod_id,
            name=prod_name,
            config_hash=self.hashcode,
            prod_hash=prod_hashcode,
            geos=self.get_geo(config["geos"]),
            resource_handler=MaskRHConfig(
                role=f"mask_{prod_id}",
                fatal=False,
                kind="promethee_mask",
                promid=prod_id,
                version=None,  # automatically changed by the validator
                namespace="vortex.cache.fr",
                experiment=self.settings.experiment,
                vapp=self.settings.vapp,
                vconf=self.settings.vconf,
                block="masks",
                format="netcdf",
                local=mask_file,
            ),
        )
        LOGGER.info("Mask config done", func="process_single_config")

        # Processing periods
        processed_periods = PeriodCollectionConfig(**config).get_processed_periods(
            production_datetime=self.rules.bulletin_datetime
        )
        LOGGER.info("Periods created", func="process_single_config")

        # Processing Hazards
        processed_hazards = dict()
        for hazard in config["hazards"]:
            LOGGER = LOGGER.bind(hazard_id=hazard["id"])
            if isinstance(hazard["id"], (list, tuple)):
                LOGGER.warning(
                    "Given hazard['id'] as list (or tuple)",
                    func="process_single_config",
                )
                if len(hazard["id"]) > 1:
                    raise ConfigurationError(
                        "Given hazard['id'] as list or tuple,"
                        f"of length {len(hazard['id'])} > 1",
                        func="process_single_config",
                    )
                hazard["id"] = hazard["id"][0]
            processed_hazards[hazard["id"]] = deepcopy(hazard)
        LOGGER = LOGGER.try_unbind("hazard_id")
        LOGGER.info("Hazards created", func="process_single_config")

        # Data and prod configs
        single_prod_config = {
            "id": prod_id,
            "name": prod_name,
            "config_hash": self.hashcode,
            "prod_hash": prod_hashcode,
            "mask_hash": single_mask_config.mask_hash,
            "components": [],
        }

        single_data_config = dict()
        components_configs = self.list_components_configs(prod_idx)
        nb_compos = len(components_configs)
        for i, compo_config in enumerate(components_configs):
            compo_id = compo_config.get("id")
            compo_hazard = "text"
            if compo_config.get("type") == "risk":
                compo_hazard = compo_config.get(
                    "hazard_name", compo_config.get("hazard")
                )
            try:
                LOGGER.info(
                    f"Starting to process component {i+1}/{nb_compos}.",
                    compo_id=compo_id,
                    compo_hazard=compo_hazard,
                    func="process_single_config",
                )
                t1 = time.time()
                single_prod_config["components"] += self.process_single_component(
                    compo_config,
                    single_data_config,
                    single_mask_config,
                    processed_periods,
                    processed_hazards,
                )
                LOGGER.info(
                    f"Component {i+1}/{nb_compos} processed",
                    compo_id=compo_id,
                    compo_hazard=compo_hazard,
                    elapsed_time=time.time() - t1,
                    func="process_single_config",
                )
            except BaseException:
                LOGGER.error(
                    f"Failed to process component {compo_id} {compo_hazard}",
                    compo_id=compo_id,
                    compo_hazard=compo_hazard,
                    exc_info=True,
                )
        LOGGER.info("process_single_config done", elapsed_time=time.time() - t0)
        LOGGER = LOGGER.try_unbind(
            "prod_id", "compo_id", "period_id", "mask_id", "param", "level", "file_id"
        )
        return single_mask_config, single_data_config, single_prod_config

    def append_config(self, single_processed_configs):
        """append_config : callback method for parallel processing
        of individual processed configs

        Args:
            single_processed_configs ([type]): [description]
        """
        t0 = time.time()
        prod_id = single_processed_configs[0].id
        LOGGER.debug("Receiving processed config.", prod_id=prod_id)
        # Mask
        self.mask_config[prod_id] = single_processed_configs[0]
        LOGGER.debug("Mask config append.", prod_id=prod_id)

        # Prod
        self.prod_config[prod_id] = single_processed_configs[2]
        LOGGER.debug("Prod config append.", prod_id=prod_id)

        # Data
        t1 = time.time()
        LOGGER.debug("Starting data config integration", prod_id=prod_id)
        for (file_id, param), rh_dico in single_processed_configs[1].items():
            t1_bis = time.time()
            key = " ".join([file_id, param])
            if key in self.data_config["preprocessed"]:
                continue

            # sources
            full_root_param, accum = self.rules.param_to_description(param)
            sources_dico = self.source_files_terms(
                file_id=file_id, param=full_root_param, accum=accum,
            )
            self.data_config["preprocessed"][key] = {
                "resource_handler": rh_dico,
                "sources": sources_dico,
                "agg": {"param": full_root_param, "accum": accum},
            }
            LOGGER.debug(
                "Data config: preproc file added.",
                prod_id=prod_id,
                preproc_file=key,
                elapsed_time=time.time() - t1_bis,
            )
        LOGGER.debug(
            "Data config append.", prod_id=prod_id, elapsed_time=time.time() - t1,
        )
        LOGGER.debug(
            "All configs append.", prod_id=prod_id, elapsed_time=time.time() - t0,
        )

    @property
    def version_config(self):
        return VersionConfig(
            version=self.hashcode,
            drafting_datetime=self.rules.drafting_datetime,
            reference_datetime=self.rules.reference_datetime,
            production_datetime=self.rules.bulletin_datetime,
            configuration_datetime=self.get_configuration_datetime(),
        )

    def process_all(self, nproc: int = os.cpu_count()):
        """process_all

        Returns:
            (dict, dict, dict): Tuple of all three expected configuration
                dictionnaries (mask, data and production)
        """
        parallel = Parallel(processes=nproc)
        for i in range(len(self.config)):
            prod_id = self.config[i].get("production_id", i)
            parallel.apply(
                self.process_single_config,
                args=(i,),
                callback=self.append_config,
                name=prod_id,
            )
        # self.prod_config, self.data_config and self.mask_config
        # can be used by different processes creating proxies via Manager
        # to handle multiprocess.
        # We use that "trick" to prevent RuntimeError("Dictionnary changed sized ...")
        # Unfortunately, we did not find the root cause of that error
        # but Manager's usage seems to work as a convenient containment
        with Manager() as manager:
            self.data_config = manager.dict()
            self.data_config = {
                "config_version": self.hashcode,
                "sources": dict(),
                "preprocessed": dict(),
            }
            self.prod_config = manager.dict()
            self.mask_config = manager.dict()

            parallel.run(timeout=self.settings.timeout)
            self.prod_config = dict(self.prod_config)
            self.mask_config = dict(self.mask_config)
            self.data_config = dict(self.data_config)

        return self.mask_config, self.data_config, self.prod_config


class ConfigMetronomeProcessor(ConfigProcessor):
    """ConfigMetronomeProcessor : Class which parses a configuration
    issued from Metronome, reshape it like an original Promethee config and
    produces three configurations out of it (like the ConfigProcessor) :
        * a mask configuration (self.mask_config)
        * a data configuration (self.data_config)
        * a production configuration (self.prod_config)
    """

    def __init__(self, config_filename: str, rules: str, drafting_datetime: Datetime):
        """__init__

        Args:
            config_filename (str): path to the configuration file
            rules_xls (str): path to the excel conf file containing all the
                rules to follow in order to choose the correct files for the
                situations.
            drafting_datetime (datetime.datetime): Promethee's drafting datetime
        """
        super().__init__(config_filename, rules, drafting_datetime)

    def get_geo(self, config: list) -> FeatureCollectionConfig:
        """get_geo
        Enable to transform METRONOME area config dictionnary such that
        it is compatible with GeoJSON format.

        Args:
            config (list): The input config
        Returns:
            FeatureCollection: [The config in GeoJSON format]
        """
        return FeatureCollectionConfig(features=config)

    @staticmethod
    def base_component_config(compo_config):
        """base_component_config: Returns the base configuration of a component
        given its original configuration

        Args:
            compo_config (dict): Component's original configuration

        Returns:
            dict: Component's base configuration
        """
        output = {}
        if "alt_min" in compo_config["data"]:
            output["alt_min"] = compo_config["data"].get("alt_min")
        if "alt_max" in compo_config["data"]:
            output["alt_max"] = compo_config["data"].get("alt_max")
        output.update(
            {
                "id": compo_config["id"],
                "type": compo_config["data"]["type"],
                "name": compo_config["name"],
                "customer": compo_config["customer"],
                "customer_name": compo_config.get("customer_name", "unknown"),
                "production_id": compo_config.get("production_id", "UnknownProdId"),
                "production_name": compo_config.get(
                    "production_name", "UnknownProdName"
                ),
                "product_comment": compo_config["data"].get("product_comment", True),
                "compass_split": compo_config["data"].get("compass_split", True),
                "altitude_split": compo_config["data"].get("altitude_split", True),
                "geos_descriptive": compo_config["data"].get("geos_descriptive", []),
            }
        )

        return output

    def reshape_hazard(
        self, hazard_idx: int, hazard: dict, columns: list
    ) -> pd.DataFrame:
        global LOGGER
        hazard_df = pd.DataFrame(columns=columns)
        LOGGER = LOGGER.bind(hazard_id=hazard["id"])
        if isinstance(hazard["id"], (list, tuple)):
            LOGGER.warning("Given hazard_id as list (or tuple)", func="reshape_hazard")
            if len(hazard["id"]) > 1:
                raise ConfigurationError(
                    "Given hazard_id as list or tuple, "
                    f"of length {len(hazard['id'])} > 1",
                    func="reshape_hazard",
                )
            hazard["id"] = hazard["id"][0]

        hazard_name = hazard.get("label", hazard.get("technical_name", "unknown"))
        if hazard_name == "unknwon":
            LOGGER.warning("Given hazard as no known name")
        for level_idx, level in enumerate(hazard["levels"]):
            for config_idx, config in enumerate(level["configs"]):
                for geo in config["geos"]:
                    for period in config["periods"]:
                        hazard_df = hazard_df.append(
                            other={
                                "hazard": hazard["id"],
                                "period": period,
                                "hazard_name": hazard_name,
                                "geo": geo,
                                "hazard_idx": hazard_idx,
                                "level_idx": level_idx,
                                "config_idx": config_idx,
                            },
                            ignore_index=True,
                        )
        LOGGER = LOGGER.try_unbind("hazard_id")
        return hazard_df

    def reshape_risk_component(self, compo_config):
        """reshape_risk_component: Transform a risk component configuration
        into a Promethee's structure given a component configuration with
        a Metronome structure.
        TO DO : Explain changes between component's configurations structures

        Args:
            compo_config (dict): Component's configuration
                (with a Metronome's structure)

        Returns:
            list of dict : List of component's configuration following
                Promethee's structure
        """
        global LOGGER
        LOGGER = LOGGER.bind(compo_id=compo_config.get("id"))
        component_df = pd.DataFrame(
            columns=[
                "hazard",
                "period",
                "hazard_name",
                "geo",
                "hazard_idx",
                "level_idx",
                "config_idx",
            ]
        )
        for hazard_idx, hazard in enumerate(compo_config["data"]["hazards"]):
            try:
                component_df = component_df.append(
                    self.reshape_hazard(hazard_idx, hazard, component_df.columns),
                    ignore_index=True,
                )
            except BaseException:
                LOGGER.error(
                    "Failed to reshape hazard.",
                    hazard_id=hazard.get("id"),
                    exc_info=True,
                )
        component_df = component_df.set_index(
            ["hazard", "period", "hazard_name", "geo"]
        ).sort_index()

        grouped_components_dict = dict()
        for idx in set(component_df.index):
            key = idx[:3] + tuple(component_df.loc[idx].values.reshape(-1))
            if key in grouped_components_dict:
                grouped_components_dict[key] += [idx[3]]
            else:
                grouped_components_dict[key] = [idx[3]]

        reshaped_components = []
        base_component_config = self.base_component_config(compo_config)
        for key, value in grouped_components_dict.items():
            new_compo = {
                "hazard": key[0],
                "period": key[1],
                "geos": value,
                "hazard_name": key[2],
                "levels": [],
            }
            new_compo.update(base_component_config)
            levels_indices = component_df.loc[
                (key[0], key[1], key[2], value[0])
            ].values.reshape((-1, 3))
            for hidx, lidx, cidx in levels_indices:
                current_level = compo_config["data"]["hazards"][hidx]["levels"][lidx]
                current_config = current_level["configs"][cidx]
                current_level_config = {"level": current_level["level"]}
                current_level_config.update(current_config["dataModel"])
                new_compo["levels"] += [current_level_config]

            reshaped_components += [new_compo]
        LOGGER = LOGGER.try_unbind("compo_id", "hazard_id")
        return reshaped_components

    def reshape_text_component(self, compo_config):
        """reshape_text_component: Transform a text component configuration
        into a Promethee's structure given a component configuration with
        a Metronome structure.
        TO DO : Explain changes between component's configurations structures

        Args:
            compo_config (dict): Component's configuration
                (with a Metronome's structure)

        Returns:
            list of dict : List of component's configuration following
                Promethee's structure
        """
        component_df = pd.DataFrame(
            columns=["period", "geo", "weather_idx", "config_idx"]
        )
        for weather_idx, weather in enumerate(compo_config["data"]["weather"]):
            for config_idx, config in enumerate(weather["configs"]):
                for period in config["periods"]:
                    for geo in config["geos"]:
                        component_df = component_df.append(
                            other={
                                "period": period,
                                "geo": geo,
                                "weather_idx": weather_idx,
                                "config_idx": config_idx,
                            },
                            ignore_index=True,
                        )
        component_df = component_df.set_index(["period", "geo"]).sort_index()
        reshaped_components = []
        base_component_config = self.base_component_config(compo_config)
        for idx in set(component_df.index):
            new_compo = {"period": idx[0], "geos": [idx[1]], "weather": []}
            new_compo.update(base_component_config)
            component_df_idx = component_df.loc[idx]
            if isinstance(component_df_idx, pd.Series):
                current_weather = compo_config["data"]["weather"][
                    component_df_idx["weather_idx"]
                ]
                current_config = current_weather["configs"][
                    component_df_idx["config_idx"]
                ]
                new_compo["weather"] += [
                    {
                        "id": current_weather["id"],
                        "condition": current_config["dataModel"]["text"],
                    }
                ]
            else:
                for widx, cidx in component_df.loc[idx].values:
                    current_weather = compo_config["data"]["weather"][widx]
                    current_config = current_weather["configs"][cidx]
                    new_compo["weather"] += [
                        {
                            "id": current_weather["id"],
                            "condition": current_config["dataModel"]["text"],
                        }
                    ]
            reshaped_components += [new_compo]

        return reshaped_components

    def list_components_configs(self, prod_idx):
        """list_components_config : list all the components configurations
        contained in a prod_idx configuration.

        Args:
            prod_idx (int): Production index in the self.config
        """
        global LOGGER
        components_list = []
        for compo_config in self.config[prod_idx]["components"]:
            # On va rajouter les clés de production si elles sont présentes
            # Pour l'instant on ne sait pas si elles sont au niveau du composant ou au
            # dessus.
            compo_config.setdefault(
                "production_id",
                self.config[prod_idx].get("production_id", "UnknownProductionID"),
            )
            compo_config.setdefault(
                "production_name",
                self.config[prod_idx].get("production_name", "UnknownProductionName"),
            )
            try:
                LOGGER = LOGGER.bind(compo_id=compo_config.get("id"))
                compo_type = compo_config["data"]["type"]
                if compo_type == "risk":
                    components_list += self.reshape_risk_component(compo_config)
                elif compo_type == "text":
                    components_list += self.reshape_text_component(compo_config)
                else:
                    raise ConfigurationError(
                        f"Unexpected component type : {compo_type}.",
                        func="list_components_configs",
                    )
            except ConfigurationError:
                LOGGER.error(
                    "Configuration Error caught.",
                    func="list_components_configs",
                    exc_info=True,
                )
            except BaseException:
                LOGGER.error(
                    "Exception caught.", func="list_components_configs", exc_info=True,
                )

        LOGGER = LOGGER.try_unbind("compo_id")
        return components_list


if __name__ == "__main__":
    cfp = ConfigMetronomeProcessor(
        "../examples/remotes/BDPE/new_14797.tgz", "default", Datetime.utcnow()
    )
    cfp.process_all()

    JsonFile("mask.json").dump(cfp.mask_config)
    JsonFile("data.json").dump(cfp.data_config)
    JsonFile("prod.json").dump(cfp.prod_config)
