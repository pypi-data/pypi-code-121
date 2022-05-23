"""
SDQC loading file
"""
import warnings
import logging
import configparser
from ast import literal_eval
from pathlib import Path
import pysd
from pysd.builders.python.namespace import NamespaceManager
from pysd.builders.python.subscripts import SubscriptManager
from pysd.translators.structures.abstract_model import AbstractSubscriptRange

from .checks_dict import checks_dict as checks

# keep missing values of external objects
pysd.external.External.missing = "keep"


def load_data(file_name, elements_subset=None, files_subset=None):
    """
    Loads the data.

    Parameters
    ----------
    file_name: str or pathlib.Path
        File name to load external data from. It must be a Vensim model file
        (.mdl) or python PySD compatible file (.py).

    elements_subset: list
        List of elements to load. If None, all elements are loaded. It can be
        a list of original_names, py_name or py_short_name.

    files_subset: list
        List of files to load. If None, all files are loaded. File paths must
        be relative to the model file.

    Returns
    -------
    initialized: list
        The list of dictionaries containing the PySD External objects used in
        the model and additional information.

    """
    if isinstance(file_name, str):
        file_name = Path(file_name)

    file_extension = file_name.suffix

    if file_extension == ".mdl":
        model = pysd.read_vensim(file_name, initialize=False)
    elif file_extension == ".py":
        model = pysd.load(file_name, initialize=False)
    else:
        raise ValueError(
            "Invalid file extension.\n"
            + "The file must be Python file or Vensim's mdl file"
            )

    # Add original Vensim name information to the objects
    exts = model._external_elements
    namespace = model.namespace
    namespace.pop("Time")

    initialized = []
    for ext in exts:
        ext.original_name = None
        for element in namespace:
            if ext.py_name in ['_ext_data_' + namespace[element],
                               '_ext_constant_' + namespace[element],
                               '_ext_lookup_' + namespace[element],
                               namespace[element]]:
                # original name
                ext.original_name = element
                # short name
                ext.py_short_name = namespace[element]

        if elements_subset:  # initialize only the subset passed by the user
            if (ext.original_name.lower() in elements_subset) or \
                (ext.py_name.lower() in elements_subset) or \
                    (ext.py_short_name.lower() in elements_subset):

                __initialize_external_object(initialized, ext)

        elif files_subset:  # initialize only the variables in the files passed
            if all(map(lambda x: x in files_subset, ext.files)):
                __initialize_external_object(initialized, ext)

        else:  # initialize all model externals
            __initialize_external_object(initialized, ext)

    logging.info(f"\n{len(initialized)} external objects could be initialized "
                 f"out of {len(exts)}.\n")

    return initialized


def load_from_dict(elements, elements_subset=None, files_subset=None):
    """
    Loads external outpust from a elements dictionary.

    Parameters
    ----------
    elements: dict
        Dictionary of the elements. Check documentation #TODO add link

    elements_subset: list
        List of elements to load. If None, all elements are loaded. It can be
        a list of original_names, py_name or py_short_name.

    files_subset: list
        List of files to load. If None, all files are loaded. File paths must
        be relative to the model file.

    Returns
    -------
    initialized: list
        The list of dictionaries containing the PySD External objects used in
        the model and additional information.

    """
    namespace_obj = NamespaceManager()
    namespace = namespace_obj.namespace  # namespace of external objects
    namespace.pop("Time")
    abstract_subscripts = []  # subscript dictionary

    for element, data in elements.items():
        if data['type'] == 'SUBSCRIPT':
            # add subscripts to the dict
            abstract_subscripts.append(AbstractSubscriptRange(
                element, data['values'], []))
        elif data['type'] == 'EXTERNAL':
            # add external variables to the namespace
            namespace_obj.add_to_namespace(element)

    added = {'dataseries': {}, 'constant': {}}

    # instantiating a SubscriptManager object
    subscript_obj = SubscriptManager(abstract_subscripts, None)

    for element in namespace:

        if len(elements[element]['excel']) == 1:
            final_coords = subscript_obj.make_coord_dict(
                    elements[element]['excel'][0]["subs"] or [])
        else:
            final_coords = subscript_obj.make_coord_dict(
                subscript_obj.make_merge_list(
                 [ex["subs"] for ex in elements[element]['excel']]))

        for excel in elements[element]['excel']:
            # retrieve excel information
            filename = excel.get('filename')
            sheet = excel.get('sheet')
            cell = excel.get('cell')
            # TODO errors for missing filename/sheet/cell
            root = Path(excel.get('root'))
            x_row_or_col = excel.get('x_row_or_cols')
            coords = subscript_obj.make_coord_dict(excel["subs"] or [])

            if x_row_or_col:
                # convert series data to pysdexternal Lookup object
                if element in added['dataseries']:
                    # add table to existing object
                    added['dataseries'][element].add(
                        filename, sheet, x_row_or_col, cell, coords)
                else:
                    # create new object
                    obj = pysd.external.ExtLookup(
                        filename, sheet, x_row_or_col, cell, coords,
                        root, final_coords,
                        '_ext_lookup_'+namespace[element])
                    obj.original_name = element
                    obj.py_short_name = namespace[element]
                    added['dataseries'][element] = obj
            else:
                # convert constant data to pysdexternal Constant object
                if element in added['constant']:
                    # add table to existing object
                    added['constant'][element].add(
                        filename, sheet, cell, coords)
                else:
                    # TODO check the final_coords value
                    # create new object
                    obj = pysd.external.ExtConstant(
                        filename, sheet, cell, coords,
                        root, final_coords,
                        '_ext_constant_'+namespace[element])
                    obj.original_name = element
                    obj.py_short_name = namespace[element]
                    added['constant'][element] = obj

    exts_ = list(added['dataseries'].values())\
        + list(added['constant'].values())

    initialized = []
    for ext in exts_:
        if elements_subset:  # initialize only the subset passed by the user
            if (ext.original_name.lower() in elements_subset) or \
                (ext.py_name.lower() in elements_subset) or \
                    (ext.py_short_name.lower() in elements_subset):

                __initialize_external_object(initialized, ext)

        elif files_subset:  # initialize only the variables in the files passed
            if all(map(lambda x: x in files_subset, ext.files)):
                __initialize_external_object(initialized, ext)

        else:  # initialize all model externals
            __initialize_external_object(initialized, ext)

    return initialized


def load_config(config_file):
    """
    Load default configuration and user configuration if any.

    Parameters
    ----------
    config_file: str or pathlib.Path
      Path to the user configuration file. If None, no file is loaded.

    Returns
    -------
    config_dict: dict
      Dictionary with the configuration retrieved from the config file

    """
    # dictionary of arguments to load from config file and their type
    config_args = {}
    for check in checks.values():
        config_args[check['flag']] = 'bool'
        if check.get('args', None):
            for arg, (type, arg_in_func) in check['args'].items():
                config_args[arg] = type

    # TODO let define groups
    # TODO enable checks by dimension/subscript range

    # load default configuration
    config = configparser.ConfigParser()
    config.read(Path(__file__).parent / 'default-conf.ini')
    config_dict = {'all': {}, 'dataseries': {}, 'constant': {}}

    # update default configuration with user configuration
    if config_file:
        if isinstance(config_file, str):
            config_file = Path(config_file)
        if not config_file.is_file():
            raise FileNotFoundError(
                f"No such file or directory: '{config_file}'")
        # read user's config file
        config.read(config_file)

    for section in config.keys():
        sec = section.lower()
        if sec not in config_dict:
            config_dict[sec] = {}
        for key in config[section].keys():
            # convert default values to a dictionary
            if key not in config_args:
                warnings.warn(f"{key} defined in the config file is not"
                              " used in any check")
            elif config_args[key] == 'bool':
                # Boolean value (bool)
                config_dict[sec][key] = config.getboolean(section, key)
            elif config_args[key] == 'float':
                # Numeric value (float)
                config_dict[sec][key] = config.getfloat(section, key)
            elif config_args[key] == 'int':
                # Integer value (int)
                config_dict[sec][key] = config.getint(section, key)
            elif config_args[key] == 'str':
                # Type value (str)
                config_dict[sec][key] = config.get(section, key)
            elif config_args[key] == 'list (float)':
                # Range value (list)
                value = config.get(section, key)
                if value[0] == '[':
                    # literla evaluation of a list
                    config_dict[sec][key] = literal_eval(value)
                else:
                    value = [float(val) for val in value.split()]
                    if all([val.is_integer() for val in value]):
                        # if all are integers convert them to int class
                        value = [int(val) for val in value]

                    config_dict[sec][key] = value
            else:
                raise ValueError(
                    f"Invalid value type definde in checks_dict for {key}")

    return config_dict


def __initialize_external_object(initialized, ext):
    """
    Initialize external objects and add them to the initialized list.

    Parameters
    ----------
    initialized: list
        List of initialized objects.
    ext: pysd.py_backend.external.External

    """
    try:
        ext.initialize()
        add_info(ext)
        initialized.append(ext)
    except Exception as err:
        warnings.warn(
            err.args[0]
            + "\n\nNot able to initialize the following object:\n"
            f"{ext.py_name}\nFind error details above.\n")


def add_info(ext):
    """
    Add info dict to external to accelerate the DataFrame generation.

    Parameters
    ----------
    ext: pysd.py_backend.external.External

    """
    if not hasattr(ext, "py_short_name"):
        ext.py_short_name = ext.py_name
    if not hasattr(ext, "original_name"):
        ext.original_name = ext.py_name

    ext.info = {
            'py_name': ext.py_name,
            'py_short_name': ext.py_short_name,
            'original_name': ext.original_name,
            'file': ext.files,
            'sheet': ext.sheets,
            'transposed': getattr(ext, "transposed", None),
            'cell': ext.cells,
            'coords': ext.coordss,
            'final_coords': ext.final_coords
    }

    if hasattr(ext, 'time_row_or_cols'):
        # ExtLookup
        ext.info['x_row_or_col'] = ext.time_row_or_cols
    elif hasattr(ext, 'x_row_or_cols'):
        # ExtData
        ext.info['x_row_or_col'] = ext.x_row_or_cols
