import copy
import logging
import os
import shutil
import xml.etree.ElementTree as ET  # noqa: S405
from typing import Callable, Dict, Sequence, Union
from pyabc import Parameter
from pyabc.external import LOC, TIMEOUT, ExternalModel
from .. import util, C
from ..sumstat import SummaryStatistics
logger = logging.getLogger("FitMultiCell.Model")


class MorpheusModel(ExternalModel):
    """
    Derived from pyabc.ExternalModel. Allows pyABC to call morpheus
    in order to do the model simulation, and then record the results
    for further processing.

    Parameters
    ----------
    model_file:
        The XML file containing the morpheus model.
    par_map:
        A dictionary from string to string, the keys being the parameter ids
        to be used in pyabc, and the values xpaths in the `morpheus_file`.
    par_scale:
        A dictionary or string to state the scale used to define the parameter
        space, e.g., lin, log10, log2
    sumstat_funs:
        List of functions to calculate summary statistics. The list entries
        are instances of fitmulticell.sumstat.SumstatFun.
    executable:
        The path to the morpheus executable. If None given,
        'morpheus' is used.
    suffix, prefix:
        Suffix and prefix to use for the temporary folders created.
    dir:
        Directory to put the temporary folders into. The default is
        the system's temporary files location. Note that these files
        are usually deleted upon system shutdown.
    clean_simulation:
        Whether to remove simulation files when they are no longer needed.
    show_stdout, show_stderr:
        Whether to show or hide the stdout and stderr streams.
    raise_on_error:
        Whether to raise on an error in the model execution, or
        just continue.
    name:
        A name that can be used to identify the model, as it is
        saved to db. If None is passed, the model_file name is used.
    time_var:
        The name of the time variable as define in Morpheus model.
    ignore_list:
        A list of columns to ignore from Morpheus output. This is introduced to
        solve the issue with result that cannot be eliminated from morpheus
        output but yet are not used in the fitting process.
    timeout:
        Maximum execution time in seconds, after which Morpheus is stopped.
    ss_post_processing:
        A callable function to perform post processing on Morpheus output. If
        a dict is passed, then specific function will be applied to each
        summary statistics.
    output_file:
        A name of the file containing the simulation output.
    """

    def __init__(
        self,
        model_file: str,
        par_map: Dict[str, str],
        sumstat: SummaryStatistics = None,
        par_scale: Union[Dict[str, str], str] = C.LIN,
        exp_cond_map: Dict = None,
        executable: str = C.MORPHEUS,
        gui_executable: str = C.GUI_MORPHEUS,
        suffix: str = None,
        prefix: str = "morpheus_model_",
        dir: str = None,
        clean_simulation: bool = False,
        show_stdout: bool = False,
        show_stderr: bool = True,
        raise_on_error: bool = False,
        timeout: float = None,
        name: str = None,
        time_var: str = C.TIME,
        outputdir: str = None,
        ss_post_processing: Union[Callable, dict] = None,
        # output_file: str = C.OUTPUT_FILE,
    ):
        if name is None:
            name = model_file
        super().__init__(
            executable=executable,
            file=model_file,
            fixed_args=None,
            create_folder=True,
            suffix=suffix,
            prefix=prefix,
            dir=dir,
            show_stdout=show_stdout,
            show_stderr=show_stderr,
            raise_on_error=raise_on_error,
            timeout=timeout,
            name=name,
        )
        self.gui_executable = gui_executable
        self.clean_simulation: bool = clean_simulation

        self.par_map: Dict[str, str] = par_map

        if isinstance(par_scale, str):
            par_scale = {key: par_scale for key in par_map}
        self.par_scale: Dict[str, str] = par_scale

        self.exp_cond_map: Dict = exp_cond_map
        self.timeout: float = timeout
        # if sumstat_funs is None:
        #     if self.exp_cond_map is None:
        #         sumstat_funs = [IdSumstatFun()]
        #     else:
        #         sumstat_funs = [
        #             IdSumstatFun(name=list(self.exp_cond_map.keys())[0])
        #         ]
        # self.summary_statistics()
        self.sumstat = sumstat
        # if sumstat is not None:
        #     self._check_sumstat_funs()
        if self.exp_cond_map is not None:
            self.sumstat.name = list(self.exp_cond_map.keys())[0]
        self.clean_simulation: bool = clean_simulation
        self.time_var: str = time_var
        self.outputdir = outputdir
        self.ss_post_processing: Union[Callable, dict] = ss_post_processing
        # self.output_file: str = output_file

    def __str__(self):
        s = (
            f"MorpheusModel {{\n"
            f"  name         : {self.name}\n"
            f"  par_map      : {self.par_map}\n"
            f"  sumstat      : {self.sumstat}\n"
            f"  executable   : {self.eh.executable}\n"
            # f"  output_file  : {self.output_file}\n"
            f"}}"
        )
        return s

    def __repr__(self):
        return self.__str__()

    def __call__(self, pars: Parameter):
        """Simulate data for parameters.

        This function is used in ABCSMC (or rather the sample() function,
        which redirects here) to simulate data for given parameters `pars`.
        """
        # create target on file system
        if self.outputdir is not None:
            self.eh.dir = self.outputdir
        loc = self.eh.create_loc()
        model_file = os.path.join(loc, "model.xml")

        # write new file with parameter modifications
        self.write_modified_model_file(model_file, pars)

        # create command
        cmd = self.eh.create_executable(loc)
        cmd = cmd + f" -file={model_file} -outdir={loc}"
        if self.eh.timeout is None and self.timeout is not None:
            self.eh.timeout = self.timeout
        # call the model
        status = self.eh.run(cmd=cmd, loc=loc)

        # check whether simulation timed out
        if status["returncode"] == TIMEOUT:
            # remove simulation output
            if self.clean_simulation:
                clean_simulation_output(loc)
            return TIMEOUT

        # compute summary statistics
        sumstats = self.compute_sumstats(loc)

        # remove simulation output
        if self.clean_simulation:
            clean_simulation_output(loc)

        # perform data post-process on Morpheus output
        # sumstats = self.call_post_processing_ss(sumstats)

        return sumstats

    def get_parmap_xpath_attr(self, key, attrib='value'):
        """
        Get the xpath and for the parameter of interest

        Parameters
        ----------
        key: str
            name of parameter of interest.
        attrib: str
            the type of attribute that need to be changed on the xml file.
        """
        par = self.par_map[key]
        if isinstance(par, str):
            return par, attrib
        elif isinstance(par, (list, tuple)) and len(par) == 2:
            return par[0], par[1]
        else:
            raise TypeError(
                f"par_map[{key}] should be a str or a list/tuple of length 2"
            )

    def get_expcondmap_xpath_attr(self, key, attrib='value'):
        """
        Get the xpath and for the experimental conditions of interest

        Parameters
        ----------
        key: str
            name of experimental condition of interest.
        attrib: str
            the type of attribute that need to be changed on the xml file.
        """
        exp_cond = self.exp_cond_map[key]
        if isinstance(exp_cond, str):
            return exp_cond, attrib
        elif isinstance(exp_cond, (list, tuple)) and len(exp_cond) == 2:
            return exp_cond[0], exp_cond[1]
        else:
            raise TypeError(
                f"par_map[{key}] should be a str or a list/tuple of length 2"
            )

    def write_modified_model_file(self, file_: str, pars: Dict[str, float]):
        """
        Write a modified version of the morpheus xml file to the target
        directory.
        """
        rescaled_pars = util.unscale(pars, self.par_scale)
        tree = ET.parse(self.eh.file)  # noqa: S314
        root = tree.getroot()
        for key, val in rescaled_pars.items():
            xpath, attr = self.get_parmap_xpath_attr(key)
            node = root.findall(xpath)
            if node.__len__() == 1:
                node[0].set(attr, str(val))
            else:
                raise KeyError(f"Key {key} is not unique or does not exist.")

        if self.exp_cond_map:
            if len(self.exp_cond_map) < 2:
                for condition, val in self.exp_cond_map.items():
                    for element, inner_val in val.items():
                        if type(inner_val) != list:
                            xpath = element
                        else:
                            xpath = element
                            attr = inner_val[0]
                            inner_val = inner_val[1]
                        node = root.findall(xpath)
                        if node.__len__() == 1:
                            node[0].set(attr, str(inner_val))
                        else:
                            raise KeyError(
                                f"condition {condition} "
                                f"is not unique or does not exist."
                            )
            else:
                raise KeyError(
                    "It seems that the model has more that one condition. "
                    "Please try to use only one condition or"
                    " use appropriate model class."
                )

        tree.write(file_, encoding="utf-8", xml_declaration=True)

    def get_par_value_form_xml_file(self, file_, param):
        """
        Get a parameter value from the model's xml file. This is currently
        being used for testing purposes.
        """
        temp_par = copy.deepcopy(param)
        tree = ET.parse(self.eh.file)  # noqa: S314
        root = tree.getroot()
        xpath, attr = self.get_parmap_xpath_attr(temp_par)
        node = root.findall(xpath)
        return node[0].attrib[attr]

    def compute_sumstats(self, loc: str) -> dict:
        """
        Compute summary statistics from the simulated data according to the
        provided list of summary statistics functions.
        """
        sumstat_dict = {LOC: loc}

        if self.sumstat is None:
            sumstat = SummaryStatistics()
            # sumstat_dict[LOC] = loc
            sumstat_dict = sumstat(loc)
            # here add the prepare function,e.g., 0: val,val,val
            # safe_append_sumstat(sumstat_dict, sumstat,)
            return sumstat_dict
        else:
            tmp_sumstat = self.sumstat(loc)
            # here add the prepare function,e.g., 0: val,val,val
            return tmp_sumstat

    def _check_sumstat_funs(self):
        """
        Check sumstat functions for validity.
        """
        names = [ssf.name for ssf in self.sumstat]
        if not len(set(names)) == len(names):
            raise AssertionError(
                f"The summary statistics passed to MorpheusModel must have"
                f"unique names, but obtained {names}"
            )

    def sanity_check(self, par: Parameter = None):
        """Sanity check of the model.

        In particular executes the model once.

        Parameters
        ----------
        par:
            Parameters at which to evaluate. If not specified, parameters are
            as in the model file.
        """
        raise_on_error = self.eh.raise_on_error
        self.eh.raise_on_error = True
        if par is None:
            par = Parameter()
        self(par)
        self.eh.raise_on_error = raise_on_error
        logger.info("Sanity check successful")

    def SBML_to_MorpheusML(self,
                           output_dir=''):
        SBML_model = os.path.basename(self.eh.file)
        SBML_model_name, SBML_model_extension = os.path.splitext(SBML_model)
        if output_dir == "":
            output_dir = f"./{SBML_model_name}_morpheusML{SBML_model_extension}"

        full_SBML_model = self.eh.file

        # create command
        cmd = self.gui_executable
        cmd = cmd + f" --convert={full_SBML_model},{output_dir}"
        self.eh.run(cmd=cmd)
        self.eh.file = output_dir
        logger.info("SBML model successfully converted to MorpheusML")

        return self

    # def _call_post_processing_ss_use_module(self, sumstats, function_name):
    #     sumstat_pp = {}
    #     for key, _module in self.ss_post_processing.items():
    #         try:
    #             func = getattr(
    #                 self.ss_post_processing[key], function_name, None
    #             )
    #             sumstat_pp[key] = func({key: sumstats[key]})
    #         except Exception as e:
    #             raise RuntimeError(
    #                 f"the selected ss_post_processing function "
    #                 f"can not be called. Be sure that the main "
    #                 f"function called `main(). `{e}"
    #             )
    #     return sumstat_pp

    # def _call_post_processing_ss_use_function(self, sumstats):
    #     sumstat_pp = {}
    #     for key, function in self.ss_post_processing.items():
    #         try:
    #             post_process_ss = function({key: sumstats[key]})
    #             sumstat_pp[key] = post_process_ss[key]
    #         except Exception as e:
    #             raise RuntimeError(
    #                 f"the selected ss_post_processing function "
    #                 f"can not be called. `{e}"
    #             )
    #     return sumstat_pp


class MorpheusModels(ExternalModel):
    """
    Derived from pyabc.ExternalModel. Allows pyABC to call morpheus
    in order to do the models simulation, and then record the results
    for further processing.

    Parameters
    ----------
    models: A list of MorpheusModel objects.
    name: Name of the joint model.
    """

    def __init__(self, models: Sequence[MorpheusModel], name: str = None):
        self.models: Sequence[MorpheusModel] = models
        self.name: str = name

    def __str__(self):
        s = f"MorpheusModels {{\n" f"\tname      : {self.name}\n" f"}}"
        return s

    def __repr__(self):
        return self.__str__()

    def __call__(self, pars: Parameter):
        """
        This function is used in ABCSMC (or rather the sample() function,
        which redirects here) to simulate data for given parameters `pars`
        and given experimental conditions.
        """

        # TODO: move all the content to another function and just call here.

        # a list that will hold result for each experimental condition.
        sumstats_all = {}
        # create target on file system
        for model in self.models:
            # cond_sumstats = {}
            sumstats = model(pars)
            # for ss_key, ss_val in sumstats.items():
            #     cond_sumstats[list(model.exp_cond_map.keys())[0]
            #     + '__' + ss_key] = sumstats[ss_key]
            sumstats_all.update(sumstats)
        return sumstats_all

    def get_parmap_xpath_attr(self, key, attrib='value'):
        """
        Get the xpath and for the parameter of interest

        Parameters
        ----------
        key: str
            name of parameter of interest.
        attrib: str
            the type of attribute that need to be changed on the xml file.

        """
        # TODO: this function is written twice
        par = self.par_map[key]
        if isinstance(par, str):
            return par, attrib
        elif isinstance(par, (list, tuple)) and len(par) == 2:
            return par[0], par[1]
        else:
            raise TypeError(
                f"par_map[{key}] should be a str or a list/tuple of length 2"
            )

    def write_modified_models_file(self, file_, pars, exp_cod):
        """
        Write a modified version of the morpheus xml file to the target
        directory.
        """
        rescaled_pars = util.unscale(pars, self.par_scale)
        tree = ET.parse(self.eh.file)  # noqa: S314
        root = tree.getroot()
        # parameters
        for key, val in rescaled_pars.items():
            xpath, attr = self.get_parmap_xpath_attr(key)
            node = root.findall(xpath)
            if node.__len__() == 1:
                node[0].set(attr, str(val))
            else:
                raise KeyError(f"Key {key} is not unique or does not exist.")
        # conditions
        for key, val in exp_cod.items():
            xpath, attr = self.get_parmap_xpath_attr(key)
            node = root.findall(xpath)
            if node.__len__() == 1:
                node[0].set(attr, str(val))
            else:
                raise KeyError(f"Key {key} is not unique or does not exist.")

        tree.write(file_, encoding="utf-8", xml_declaration=True)

    # def call_post_processing_ss(self, sumstats, function_name='main'):
    #     if self.ss_post_processing is not None:
    #         if isinstance(self.ss_post_processing, Callable):
    #             sumstats = self.ss_post_processing(sumstats)
    #         elif isinstance(self.ss_post_processing, dict):
    #             if not set(self.ss_post_processing.keys()).issubset(
    #                 sumstats.keys()
    #             ):
    #                 raise ValueError(
    #                     "the keys on the 'ss_post_processing' does not "
    #                     "match the one on the summary statistics names."
    #                 )
    #             if isinstance(
    #                 list(self.ss_post_processing.values())[0], Callable
    #             ):
    #                 sumstats = self._call_post_processing_ss_use_function(
    #                     sumstats
    #                 )
    #             elif isinstance(
    #                 list(self.ss_post_processing.values())[0], ModuleType
    #             ):
    #                 sumstats = self._call_post_processing_ss_use_module(
    #                     sumstats, function_name
    #                 )
    #         else:
    #             raise ValueError(
    #                 f"the type of 'post_processing_ss' should be str or dict."
    #                 f" However, {type(self.ss_post_processing)} was given."
    #             )
    #     return sumstats

    def _call_post_processing_ss_use_module(self, sumstats, function_name):
        sumstat_pp = {}
        for key, _module in self.ss_post_processing.items():
            try:
                # sumstat_pp[key] = module.main(sumstats)
                func = getattr(
                    self.ss_post_processing[key], function_name, None
                )
                sumstat_pp[key] = func(sumstats[key])
            except Exception as e:
                raise RuntimeError(
                    f"the selected ss_post_processing function "
                    f"can not be called. Be sure that the main "
                    f"function called `main(). `{e}"
                )
        return sumstat_pp

    def _call_post_processing_ss_use_function(self, sumstats):
        sumstat_pp = {}
        for key, function in self.ss_post_processing.items():
            try:
                sumstat_pp[key] = function(sumstats[key])
            except Exception as e:
                raise RuntimeError(
                    f"the selected ss_post_processing function "
                    f"can not be called. `{e}"
                )
        return sumstat_pp


# def safe_append_sumstat(sumstat_dict, sumstat):
#     types_ = (numbers.Number, np.ndarray, pd.DataFrame)
#     if isinstance(sumstat, types_):
#         if key in sumstat_dict:
#             raise KeyError(
#                 f"Key {key} for sumstat {sumstat} already in the "
#                 f"sumstat dict {sumstat_dict}."
#             )
#         sumstat_dict[key] = sumstat
#         return
#     if isinstance(sumstat, dict):
#         if key in sumstat_dict:
#             raise KeyError(
#                 f"Key {key} for sumstat {sumstat} already in the "
#                 f"sumstat dict {sumstat_dict}."
#             )
#         sumstat_dict.update(sumstat)
#         return
#     raise ValueError(
#         f"Type {type(sumstat)} of sumstat {sumstat} " f"is not permitted."
#     )


def clean_simulation_output(loc):
    """
    Remove the simulation output directory after calculating the
    summary statistics.

    Parameters
    ----------
    loc: str
        Location of the simulation directory.
    """

    shutil.rmtree(loc, ignore_errors=True)
