from typing import Union
import logging
import datetime
import os
import csv
import json
import time
import yaml
from unidecode import unidecode
import re
import pandas as pd
import findhelp.custom_utils as custom_utils

from findhelp.custom_exceptions import NotValidDirectoryError
from findhelp.custom_exceptions import NotValidArgumentError
from findhelp.custom_exceptions import MissingFilename


main_logger = logging.getLogger(__name__)
main_logger.setLevel(logging.INFO)
formatter = logging.Formatter("%(asctime)s:%(levelname)s:%(message)s")
now = datetime.datetime.now()
date_today = now.strftime("%Y%m%d")
date_now = now.strftime("%Y%m%d_%H_%M_%S")

stream_handler = logging.StreamHandler()
stream_handler.setFormatter(formatter)

main_logger.addHandler(stream_handler)


# For printing
HEADER_RESULT = ["fullpath",
                 "type",
                 "folder_parent",
                 "folder_name",
                 "file_name",
                 "ext"]

CONFIG_PATH = os.path.join(os.path.dirname(
    os.path.realpath(__file__)), "config.yaml")


def __search_elements(
        search_type: str, string_search: Union[str, re.Pattern] = "", path: str = ".", dir_sep: str = "/",
        ignore_case: bool = False, ignore_accents: bool = False, ignore_folders: list = None, results: list = None,
        ext_exclude: list = None, ext_include: list = None, output: str = "console"):
    """Recursively searches for coincidences of files / folders in the specified 'path'. Called from '__search'

    Args:
        search_type (str): Indicates what to search for {files, folders, both}
        string_search (Union[str, re.Pattern], optional): The string to look for
        path (str, optional): Root path to look for. Defaults to ".".
        dir_sep (str, optional): Just for results purposes: which separator use for paths. Defaults to "/".
        ignore_case (bool, optional): Indicates whether or not searching is case-sensitive. Defaults to False.
        ignore_accents (bool, optional): Ignore accents. Defaults to False.
        ignore_folders (list, optional): Folders to ignore while searching. Defaults to None.
        results (list, optional): List to append the found results. Defaults to None.
        ext_exclude (list, optional): List of extensions to exclude. Defaults to None.
        ext_include (list, optional): List of extensions to search.
            If different than None, searching ignores 'ext_exclude' and considers only 'ext_include'. 
            Defaults to None.
        output (str): {console,txt,csv,json,df,obj_list,list}
                Indicates if results appears on console or are written to a file.
                Defaults to "console".

    Returns:
        _type_: _description_
    """
    # it seems double, but otherway
    if results == None:
        results = []

    if output in ["console", "list"]:
        output_type = "list"
    else:
        output_type = "dict"

    if os.path.split(path)[1] not in ignore_folders:
        for dirpath, dir_names, file_names in os.walk(path):
            dir_names[:] = [d for d in dir_names if d not in ignore_folders]

            if search_type in ("folders", "both") and not ext_include:
                # folders
                dir_founds = custom_utils.search_in_list(
                    dir_names, string_search, ignore_case, ignore_accents)

                filtered_dir_founds = [
                    found for found in dir_founds if found.lower() not in ignore_folders]

                for found in filtered_dir_founds:
                    results.append(custom_utils.join_result(output_type, dir_sep,
                                                            dirpath, "folder", os.path.dirname(dirpath), found))

            # files
            if search_type in ("files", "both"):
                founds = custom_utils.search_in_list(
                    file_names, string_search, ignore_case, ignore_accents)

                if ext_include:
                    filtered_founds = [found for found in founds if os.path.splitext(
                        found)[1].lower() in ext_include]
                elif ext_exclude:
                    filtered_founds = [found for found in founds if os.path.splitext(
                        found)[1].lower() not in ext_exclude]
                else:
                    filtered_founds = founds

                for found in filtered_founds:
                    tempext = os.path.splitext(found)[1]
                    results.append(custom_utils.join_result(output_type, dir_sep,
                                                            dirpath, "file", os.path.dirname(dirpath), os.path.basename(dirpath), found, tempext))

    return results


def __search(
        path: str, string_search: str, ignore_case: bool, ignore_accents: bool, reg_exp: bool,
        ext: Union[str, list], all: bool, only_files: bool, only_dirs: bool, dir_sep: str,
        output: str):
    """Called from 'go_search'. Defines what extensions / folders ignore and / or consider.
        and calls __search_elements to get a list of coincidences

    Args:
        path (str): Root path to look for
        string_search (str): The string to look for
        ignore_case (bool): Indicates whether or not searching is case-sensitive
        ignore_accents (bool): Ignore accents
        reg_exp (bool): Searches by regular expresion
        ext (Union[str, list]): List of extensions to limit the search
        all (bool): Searches on all folders, ignores 'ignore_folders' switch on 'config.yaml'
        only_files (bool): Searches only for files (not directories)
        only_dirs (bool): Searches only for directories (not files)
        dir_sep (str): Just for results purposes: which separator use for paths
        output (str): {console,txt,csv,json,df,obj_list,list}
                Indicates if results appears on console or are written to a file        

    Raises:
        NotADirectoryError: Raised if path is not a directory
        NotValidDirectoryError: Raised if path to directory doesn't really exist

    Returns:
        list[str]: List of strings with found coincidences
    """
    if not os.path.isdir(path):
        raise NotADirectoryError
    elif not os.path.exists(path):
        raise NotValidDirectoryError(
            message="Specified directory is not valid")

    string_search = unidecode(
        string_search) if ignore_accents else string_search

    string_search = re.compile(
        f"{string_search}") if reg_exp else string_search

    _config = __config()

    ignore_folders = custom_utils.sel_arg(_config, "ignore_folders")
    if ignore_folders == None or all:
        ignore_folders = []

    ext_exclude = custom_utils.sel_arg(_config, "ignore_extensions")

    if ext_exclude != None:
        if isinstance(ext_exclude, list):
            if len(ext_exclude) == 0:
                ext_exclude = None
            else:
                ext_exclude = [f".{str(ext)}".replace("..", ".").lower()
                               for ext in ext_exclude]
    if ext:
        ext_include = [f".{ext.lower()}".replace("..", ".") for ext in ext]
    else:
        ext_include = None

    results = []

    if only_dirs:
        results += __search_elements("folders", string_search, path,
                                     dir_sep, ignore_case, ignore_accents, ignore_folders, output=output)
        return results

    if only_files:
        results += __search_elements("files", string_search, path, dir_sep, ignore_case, ignore_accents, ignore_folders,
                                     ext_exclude=ext_exclude, ext_include=ext_include, output=output)
        return results

    results += __search_elements("both", string_search, path, dir_sep, ignore_case, ignore_accents, ignore_folders,
                                 ext_exclude=ext_exclude, ext_include=ext_include, output=output)
    return results


def __get_results(results: list, output_type: str, delimiter: str, search_args: dict,
                  time_start: datetime, time_end: datetime, total_time: float,
                  output_path: str, output_filename):
    """Turns the results list into the selected choice

    Args:
        results (list): List containing all the coincidences found
        output_type (str): Defines how to get the final output {console, txt, csv, json, df, obj_list, list}
            (df = pandas.DataFrame)
        delimiter (str): Delimiter used for {txt, csv, json} output
        search_args (dict): Arguments used for searching. Will be stored in file if output_type = 'json'
        time_start (datetime): Time when search began
        time_end (datetime): Time when search ended
        total_time (float): Difference between time_end and time_start
        output_path (str): Path in which the results file will be located. Default current directory.
        output_filename (str): Name of file in which results will be stored. Default search_results_yyyymmdd_hh_mm_ss 

    Returns:
        object: Returns a boolean if output_type in {'console', 'txt', 'csv', 'json'} 
            and prints the results to the actual choice
            Returns the selected object if output_type in {'obj_list', 'list', 'df'}
            (df = pandas.DataFrame)

    """
    """ if len(results) == 0:
        return 0 """

    output_type = output_type.lower()

    if output_type == "console":
        results.insert(0, HEADER_RESULT)
        max_l = [max(map(custom_utils.find_len, [results[outer_ind][ind] for outer_ind in range(len(results))])) + 1
                 for ind in range(len(results[0]))]

        for result in results:
            print(custom_utils.parse_line(result, max_l))
        return (len(results) - 1)

    elif output_type.lower() in ["df"]:
        return pd.DataFrame(results)
    elif output_type in ["obj_list", "list"]:
        return results
    else:
        output_fullpath = custom_utils.forcedir_sep(os.path.join(
            output_path, f"{output_filename}.{output_type}"), "/")

        if output_type in ("txt", "csv"):
            with open(f"{output_fullpath}", "w", newline="\n", encoding="utf-8") as new_file:
                csv_writer = csv.writer(new_file, delimiter=delimiter)
                headers = list(results[0].keys())
                csv_writer.writerow(headers)

                for result in results:
                    line = list(result.values())
                    csv_writer.writerow(line)

        if output_type in ("json"):
            export_dict = {
                "search_args": search_args,
                "start": time_start,
                "end": time_end,
                "total_time_seconds": total_time,
                "results": results
            }
            with open(f"{output_fullpath}", "w", encoding="utf-8") as new_file:
                json.dump(export_dict, new_file, indent=2, ensure_ascii=False)
        main_logger.info(f"Exported {output_fullpath}")

        return (len(results) - 1)


def go_search(args_dict):
    """Searches for files / folders in the specified 'path'.

    Args:
        args_dict (dict): Dictionary containing all the specification to perform the search.                
            path (str): Root path to look for, default = current directory
            stringsearch (str): The string to look for
            ignorecase (bool): Indicates whether or not searching is case-sensitive
            ignoreaccents (bool): Ignore accents
            regexp (bool): Searches by regular expresion
            ext (list[str]): List of extensions to limit the search
            all (bool): Searches on all folders, ignores 'ignore_folders' switch on 'config.yaml'
            onlyfiles (bool): Searches only for files (not directories)
            onlydirs (bool): Searches only for directories (not files)
            directoryseparator (str): Just for results purposes: which separator use for paths
            output (str): {console,txt,csv,json,df,obj_list,list}
                Indicates if results appears on console or are written to a file
            delimiter (str): Delimiter used for exporting, when output is different than 'console'
            outputpath (str): Path in which the results file will be located. Default current directory.
            outputfilename (str): Name of file in which results will be stored. Default search_results_yyyymmdd_hh_mm_ss 

    Raises:
        NotValidArgumentError: 'onlydirs' and 'onlyfolders' can't be True simultaneously
        NotValidArgumentError: If 'stringsearch' was not specified, 'ext' or 'onlydirs' or 'onlyfiles' must be passed
        NotADirectoryError: Raised if path is not a directory
        NotValidDirectoryError: Raised if path to directory doesn't really exist
    """

    # Compute start time
    time_start = datetime.datetime.now()
    start_search = time.perf_counter()
    main_logger.info(f"Searching for: {args_dict} , please wait...")

    # Checking arguments
    # When called from console, argparse makes validation, when called from other module, it is necessary to check
    ks = args_dict.keys()

    defaults = {"path": os.getcwd(), "stringsearch": "", "ignorecase": False,
                "ignoreaccents": False, "regexp": False, "ext": None, "all": False,
                "onlyfiles": False, "onlydirs": False, "directoryseparator": "/",
                "output": "console", "outputpath": ".", "outputfilename": date_now,
                "delimiter": "\t"}

    for key, value in defaults.items():
        if key not in ks:
            args_dict[key] = value
        elif args_dict[key] is None:
            args_dict[key] = value

    if args_dict["outputpath"]:
        if not os.path.isdir(args_dict["outputpath"]):
            raise NotADirectoryError(
                f"outputpath: {args_dict['outputpath']} is not a valid directory")

    if args_dict["outputfilename"] == "":
        raise MissingFilename("Filename can't be empty if passed as argument")
    else:
        args_dict["outputfilename"] = custom_utils.force_filename(
            args_dict["outputfilename"])

    if (args_dict["onlyfiles"] & args_dict["onlydirs"]):
        raise NotValidArgumentError(
            message="Not valid arguments, forbidden combination: onlyfiles=True and onlydirs=True")

    if args_dict["stringsearch"] == "":
        if ((not args_dict["ext"]) & (not args_dict["onlydirs"]) & (not args_dict["onlyfiles"])):
            raise NotValidArgumentError(message="Not a valid combination to search for:"
                                        "\nUsing 'stringsearch'='' requires specifying 'onlydirs' or ('onlyfiles' and/or 'ext')")

    # The actual searching
    search_results = __search(
        path=args_dict["path"], string_search=args_dict["stringsearch"], ignore_case=args_dict["ignorecase"],
        ignore_accents=args_dict["ignoreaccents"], reg_exp=args_dict["regexp"], ext=args_dict["ext"],
        all=args_dict["all"], only_files=args_dict["onlyfiles"], only_dirs=args_dict["onlydirs"], dir_sep=args_dict["directoryseparator"],
        output=args_dict["output"]
    )

    # Compute time end
    time_end = datetime.datetime.now()
    end_search = time.perf_counter()

    # Compute total time
    time_start_str = time_start.strftime("%Y/%m/%d, %H:%M:%S.%f")
    time_end_str = time_end.strftime("%Y/%m/%d, %H:%M:%S.%f")
    total_time = end_search - start_search

    main_logger.info(
        f"{len(search_results)} coincidences found in {round(total_time, 2)} second(s)")

    # Export / show results
    return __get_results(search_results, args_dict["output"], args_dict["delimiter"], args_dict,
                         time_start_str, time_end_str, total_time, args_dict["outputpath"], args_dict["outputfilename"])


def __config():
    """Reads 'config.yaml' 

    Returns:
        dict: Dictionary with configuration located in 'config.yaml' (ignore_folders + ignore_extensions)

    """
    with open(CONFIG_PATH, "r") as f:
        _config = yaml.safe_load(f)

    return _config


def set_ignore_folders(ignore_list=None):
    """Sets config.yaml 'ignore_folders' list

    Args:
        ignore_list (list[str], optional): List of folders to be ignored in future searches. 
            None of its subfolders will be considered. Defaults to None.
    """
    _config = __config()
    if ignore_list:
        ignore_list = [str(element) for element in ignore_list]
        _config["ignore_folders"] = ignore_list
    else:
        _config["ignore_folders"] = custom_utils.default_ignore_folders()

    with open(CONFIG_PATH, "w+") as yf:
        yaml.dump(_config, yf, allow_unicode=True, default_flow_style=False)


def set_ignore_extensions(ignore_list=None):
    """Sets config.yaml 'ingnore_extension' list

    Args:
        ignore_list (list[str], optional): List of extensions to be ignored in future searches. Defaults to None.
    """
    _config = __config()
    if ignore_list:
        ignore_list = [str(element) for element in ignore_list]
        _config["ignore_extensions"] = ignore_list
    else:
        _config["ignore_extensions"] = []

    with open(CONFIG_PATH, "w+") as yf:
        yaml.dump(_config, yf, allow_unicode=True, default_flow_style=False)
