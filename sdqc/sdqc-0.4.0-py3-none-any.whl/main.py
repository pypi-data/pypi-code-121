"""
SDQC main file
"""
import warnings
from pathlib import Path

import numpy as np
import pandas as pd
from pysd.py_backend.external import External

from .loading import load_data, load_config, load_from_dict, add_info
from .tools import _add_config_to_ext
from .reports import Report
from .checks_dict import checks_dict as checks


def check(source, config_file=None, output='dataframe',
          report_config=None, report_filename=None, verbose=False,
          elements_subset=None, files_subset=None):
    """
    Main function to run the check.

    Parameters
    ----------
    source: str, pathlib.Path, dict or list
        File name or dictionary to load external data from or list of
        dictionaries containing initialized External objects in the obj key.
        If a file name is given, it must be a Vensim model file
        (.mdl) or python PySD compatible file (.py). If a dict is
        given it should be compatible with loading.load_from_dict
        function (see #TODO link to documentation).

    config_file: str (optional)
        Path to the config file.

    output: str (optional)
        Options: "dataframe" or "report". When "report" is chosen, the user can
        define the type of report using the report_config file. Supported
        report formats are html, markdown and pdf.

    report_config: str or pathlib.Path (optional)
        Path to the config file of the report.

    report_filename: str or pathlib.Path (optional)
        Name of the report file, including extension.

    verbose: bool (optional)
        If True the output from all checks is saved. If False (default)
        only the output from not passed checks will be saved.

    elements_subset: list (optional)
        List of model variables that load external data that the user wants to
        check. This prevents the loading of all external data of the model.

    files_subset: list (optional)
        List of files that the user wants to check. This prevents the loading
        of external data from the rest of files. File paths must be relative to
        the model file. The elements_subset argument prevails if both are
        passed.

    Returns
    -------
    out: pd.DataFrame or Report
        Either a dataframe with the results of the checks or a Report object.

    """

    if isinstance(source, (str, Path)):
        # load external objects from .mdl/PySD model in Python
        exts = load_data(source, elements_subset, files_subset)
    elif isinstance(source, dict):
        # load data from a dictionary
        exts = load_from_dict(source, elements_subset, files_subset)
    elif isinstance(source, list) and all(
         map(lambda y: isinstance(y, External), source)):
        # use the list of initialized External objects
        exts = source
        [add_info(ext) for ext in exts]
    else:
        raise ValueError("Source must be a file_name, a Path, a dictionary "
                         "or a list of initialized pysd External objects.")

    # load configuration
    config = load_config(config_file)

    # add config information to each external object

    _add_config_to_ext(exts, config)

    # iterate over External objects to run the checks
    out = []
    for ext in exts:
        if ext.check_config['_type'] == 'constant':
            check_constant(ext, out, verbose)
        elif ext.check_config['_type'] == 'dataseries':
            check_dataseries(ext, out, verbose)

    if output == "dataframe":
        return pd.DataFrame(out)
    elif output == "report":
        report_obj = Report(out)
        if not report_obj.data.empty:  # if there is data to report
            report = report_obj.build_report(report_config, verbose)
            report_obj.report_to_file(report, report_filename)

        return report_obj
    else:
        raise ValueError("Output must be 'dataframe' or 'html'.")


def check_constant(ext, out, verbose):
    """
    Run the checks in a ExtConstant type object.

    Parameters
    ----------
    ext: dict
        The dictionary contains the pysd.external.ExtConstant object to pass
        the check in the obj key. It must have the py_short_name, original_name
        and config attributes, set previously.
    out: list
        The list to append the results of the checks.
    verbose: bool
        If True the output from all checks is saved. If False only the
        output from not passed checks will be saved.

    Returns
    -------
    None

    """
    # TODO enable checks by dimension/subscript range

    if not hasattr(ext, 'data'):
        return

    if ext.coordss[0]:
        constant_values = ext().values
    else:
        # if constant value is 0-D (float) no test can be passed
        return

    # Start checks
    for chk in checks:
        # Is this check type selected and can it be run on constants?
        if 'constant' in checks[chk]['targets']\
          and ext.check_config[checks[chk]['flag']]:
            new_info = _run_check(
                [constant_values], chk, ext.check_config,
                'constant', ext.info, verbose)
            if new_info:
                out.append(new_info)


def check_dataseries(ext, out, verbose):
    """
    Run the checks in a ExtData or ExtLookup type object.

    Parameters
    ----------
    ext: dict
        The dictionary contains the pysd.external.ExtData or
        pysd.external.ExtLookup object to pass the check in the obj key. It
        must have the py_short_name, original_name and config attributes,
        set previously.
    out: list
        The list to append the results of the checks.
    verbose: bool
        If True the output from all checks is saved. If False only the
        output from not passed checks will be saved.

    Returns
    -------
    None

    """
    # TODO enable checks by dimension/subscript range

    if not hasattr(ext, "data"):
        return

    data_values = ext.data.values
    series_values = ext.data.coords[ext.data.dims[0]].values

    if ext.check_config["missing"]:
        # check for missing values in the series first, and add them to the
        # result of the check, as we need to remove them before starting the
        # other checks
        new_info = ext.info.copy()
        new_info['check_name'] = 'missing_values_series'
        new_info['check_description'] = checks['missing_values']['descr']
        new_info['check_target'] = 'series'
        new_info['check_arg'] = {}

        # run the check for missing values in the series
        new_info['check_pass'], new_info['check_out'] =\
            checks['missing_values']['func'](series_values)

        if verbose or not new_info['check_pass']:
            out.append(new_info)

    # here the user did not select that they want to check for missing values,
    # but we are removing them anyway
    elif np.any(np.isnan(series_values)):
        warnings.warn(
            "Removing the columns corresponding to missing values in "
            "the series. Activate the missing_values check to see "
            "the results of the check.")

    # Remove missing values from series, if any
    data_values = data_values[~np.isnan(series_values)]
    series_values = series_values[~np.isnan(series_values)]

    # Start checks
    for chk in checks:
        # Is the check activated?
        new_info = None
        if ext.check_config[checks[chk]['flag']]:
            if 'series' in checks[chk]['targets']:
                # Check for series
                new_info = _run_check([series_values], chk,
                                      ext.check_config, 'series', ext.info,
                                      verbose)
            elif 'data' in checks[chk]['targets']:
                # Check for data
                new_info = _run_check([data_values], chk,
                                      ext.check_config,
                                      'data', ext.info, verbose)
            elif 'dataseries' in checks[chk]['targets']:
                # Check for data + series
                new_info = _run_check([data_values, series_values], chk,
                                      ext.check_config, 'dataseries',
                                      ext.info, verbose)
            if new_info:
                out.append(new_info)


def _run_check(values, check_name, econfig, target, info, verbose):
    """
    Run a check with the given arguments.

    Parameters
    ----------
    values: list
        List of arguments to run a check, could be data, series,
        constant or data and series.
    check_name: str
        Name of the check to be passed.
    econfig: dict
        Configuration dictionary of the object. Needed to find extra
        arguments for the function.
    target: str
        The target of the check, must match the arguments passed in args.
    info: dict
        General info for the current reading block.
    verbose: bool
        If True the output from all checks is saved. If False only the
        output from not passed checks will be saved.

    Returns
    -------
    None

    """
    # create a new dictionary to sabe
    new_info = info.copy()

    # save name, description and target
    new_info['check_name'] = check_name
    new_info['check_description'] = checks[check_name]['descr']
    new_info['check_target'] = target

    if 'args' in checks[check_name] and checks[check_name]['args']:
        # read the arguments and save the info
        new_info['check_arg'] = {
            checks[check_name]['args'][arg][1]: econfig[arg]
            for arg in checks[check_name]['args']}
    else:
        # no arguments
        new_info['check_arg'] = {}

    # run the check
    new_info['check_pass'], new_info['check_out'] =\
        checks[check_name]['func'](*values,
                                   **new_info['check_arg'],
                                   coords=new_info['coords'],
                                   final_coords=new_info['final_coords'])

    # save the result if the check has not passed or verbose is True
    if not new_info['check_pass'] or verbose:
        return new_info
