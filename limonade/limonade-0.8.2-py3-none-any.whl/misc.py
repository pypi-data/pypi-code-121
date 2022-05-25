import re
import datetime as dt
from pathlib import Path
import numpy as np
from typing import Optional, Union
from types import SimpleNamespace
import json
import limonade.loaders as ldr

def make_run_id(base_path, base_name):
    """
    Make sure old data is never overwritten. Adds an incremented number to base name. If a datafile with the same name
    already exists, then the number is incremented.


    :param base_path:
    :param base_name:
    :return:
    """
    base_dir = Path(base_path) / (base_name + '-')
    dirlist = Path(base_path).glob(base_name + '-???')
    meas_numlist = [-1]
    for name in dirlist:
        namestr = str(name)
        if name.is_dir():
            if namestr[len(str(base_dir))].isnumeric():
                meas_numlist.append(int(namestr[len(str(base_dir)):]))
    meas_num = max(meas_numlist) + 1
    return str(base_dir)+'{:03d}'.format(meas_num), base_name+'-{:03d}'.format(meas_num)


def parse_time(args, cfg):
    """
    Parses command line time slice with optional timebase argument. Timebase argument is one of 's', 'm', 'h' or 'd'.
    Timebase argument, if it exists, is the last value in the list or tuple of (start, [stop], [timebase]) that defines
    the slice.

    :param args: A list or tuple of (start, [stop], [timebase]). All input arguments are strings.
    :param args: Detector config for index variable info.
    :return: returns parsed time slice (start, stop) in integer nanoseconds.

    """

    if len(args) > 3:
        print('Invalid time range!')
        raise ValueError
    index_slice = [None, None]
    timebase, new_args = parse_index_unit(args, cfg)
    index_slice[:len(new_args)] = [int(new_args[x]) * timebase for x in range(len(new_args))]
    return index_slice


def parse_index_unit(args, cfg):
    """
    Parses the index unit string if it exists, supplies default if it does not and returns the timebase multiplier
    with the other arguments. Default is the first in the list of unit strings

    :param args: A list or tuple of (start, [stop], [index_unit]). All input arguments are strings.
    :param args: The detector configuration
    :return: timebase multiplier for ns-transformation and list of the other arguments.

    """

    if args[-1].isnumeric():  # no timebase character added, using first as default
        timebase = cfg.det['index_variable'].items()[0][1]
        return timebase, args
    else:
        # units = {'ns': 1, 'us': 1000, 'ms': 1e6, 's': 1e9, 'm': 60e9, 'h': 3600e9, 'd': 24 * 3600e9}
        units = cfg.det['index_variable']['unit']
        if args[-1] in units.keys():
            timebase = units[args[-1]]
            new_args = args[:-1]
        else:
            print('Invalid index unit. Index base in {}!'.format(units))
            raise ValueError
    return timebase, new_args


def atoi(text):
    """
    Convert integer text to int, otherwise return the original string. Used to parse long filenames with numbering
    in the filenme.

    :param text: Input string.
    :return: If text is convertible to integer this returns the integer, otherwise the original text.
    """

    return int(text) if text.isdigit() else text


def natural_keys(text):
    """
    alist.sort(key=natural_keys) sorts number strings in human order ('1' before '10') and so on.
    Taken from:
    http://nedbatchelder.com/blog/200712/human_sorting.html

    :param text: input string
    :return:

    """

    nums = re.split(r'(\d+)', text)

    return [atoi(x) for x in nums]

'''
def fromisoformat(dt_string):
    """
    Converts string returned by python 3.7+ datetime.toisoformat() into a proper datetime object. This was needed
    because the isoformat seems to be fairly new thing in python and not present in 3.6 or earlier.

    The string to be parsed is of the format: "2020-06-09T04:00:01.434322"

    :param dt_string: isoformat string

    :return: datetime object

    """

    date_p, time_p = dt_string.split('T')
    date_p = date_p.split('-')
    time_p = time_p.split(':')
    secval = float(time_p[2])
    time_p[-1] = int(secval // 1)
    time_p.append(int((secval-time_p[-1]) * 1000000))
    in_list = [int(x) for x in date_p + time_p]
    return dt.datetime(*in_list)
'''

def parse_file(dir_name: Union[Path, str], file_name: Optional[str], cfg: SimpleNamespace):  # data_type: str, index_var: str):
    """
    Finds data files (matching optional file_name prefix) from directory. First event mode data files are searched for,
    if not found, then channel mode files and finally raw data files are searched for. All files in the directory (or
    matching a given base name) are returned

    Problem is that some raw data formats (Caen, native channel data) have multiple files per measurement. This is fixed
    by having a wildcard expression of the postfix of the filename included in the extension
    like ch???.dat for caen data. Unique names are then automatically resolved by saving the base names as keys to a
    dictionary (which is ordered in py3.7+ unlike the set?).

    :param dir_name: The directory containing the data
    :param: file_name: optional base name for data files if they are named differently from directory.
    :param: data_type: Name of the data type (a string key in loaders.loader_dict).
    :param: index_var: Name of the index variable data (a given in detector configuration).

    :return: list of base names of data files in the directory (matching file_name prefix)
    """
    data_type = cfg.det['data_type']
    index_var = cfg.det['index_variable']['name']
    # into pathlib object if not already
    directory = Path(dir_name)
    if file_name is not None:  # if filename prefix is given
        prefix = file_name
    else:  # otherwise use the directory name as prefix
        prefix = directory.stem

    suffix = '_{}.dat'.format(index_var)
    print('Searching for direct match:', directory, prefix + suffix)

    if (directory / (prefix + suffix)).exists():
        # a match
        base_names = [prefix]
    else:
        # list of base names matching the prefix
        base_names = [x.name[:-len(suffix)] for x in directory.glob(prefix + '*' + suffix)]

    print('base names', base_names)

    # if event data is not found the data may be split to several channel- or raw- files. Need to construct list of
    # unique base names.
    if len(base_names) == 0:  # if channel data is present the loading will go on from there
        suffix = '_{}_ch?.dat'.format(index_var)
        print('Searching for channel data: {}.'.format(prefix + suffix))
        # temp = {x.name[:-len(prefix + suffix)]: None for x in
        temp = {x.name[:-len(suffix)]: None for x in
                directory.glob(prefix + suffix)}
        base_names = list(temp.keys())

    if len(base_names) == 0:  # raw data is checked last
        suffix = ldr.loader_dict[data_type].extension
        if suffix is not None:
            print('Searching for raw data: {}.'.format(prefix + suffix))
            temp = {x.name[:-len(suffix)]: None for x in
                    directory.glob(prefix + suffix)}
            base_names = list(temp.keys())

    if len(base_names) == 0:
        print('No datafiles found from', directory)
        print('Tried to match with base name', prefix)

    return base_names


def check_monotonousness(vector):
    """
    Checks if values in a given vector are monotonously increasing. If they are not, the index of the first element
    that breaks the monotonousness is returned. None.
    :param vector:
    :return: Index of first out-of-place element in vector. None is returned if vector is monotonous.
    """
    retval = None

    # Check for timestamp reset events in good data
    temp = vector[1:] <= vector[:-1]
    if np.any(temp):

        retval = np.argmax(temp) + 1
        print('vec at', retval, vector[retval], temp[retval])
        print('Time reset event!')

    #for i in range(vector.shape[0]-1):
    #    if (vector[i] > vector[i+1]):
    #        retval = i+1
    #        break
    return retval


def sanitize_for_json(athing):
    # Takes in a dict or an old type config namespace and puts out a new style config dict with json-compatible types.
    int_types = (np.uint8, np.int8, np.uint32, np.int32, np.uint64, np.int64)
    float_types = (np.float32, np.float64)
    if isinstance(athing, SimpleNamespace):
        athing = athing.__dict__

    if isinstance(athing, list):
        for idx, val in enumerate(athing):
            athing[idx] = sanitize_for_json(val)

    elif isinstance(athing, np.ndarray):
        athing = athing.tolist()

    elif isinstance(athing, dict):
        for key, val in athing.items():
            athing[key] = sanitize_for_json(val)
    else:
        if isinstance(athing, int_types):
            athing = int(athing)
        elif isinstance(athing, float_types):
            athing = float(athing)
        elif isinstance(athing, dt.datetime):
            athing = athing.isoformat()
    return athing


def desanitize_json(athing, akey=None):
    """
    This is the opposite of sanitize_for_json, so that given keywords are cast back to their proper numpy or datetime
    formats on load. Lists of keywords are maintained here and any new specially typed data should be added to the
    lists to ensure proper operation.

    The function recursively goes through the input dictionary looking for dictionary keywords in the internal type
    tuples. If one is found, the data value of the key is cast into proper format.

    :param athing:  A dictionary that will be sanitized
    :param akey:  The key of athing, if it came from a dictionary
    :return:        A dictionary with properly cast data
    """

    float_types = ('dead_time', 'live_time', 'quantity')
    date_types = ('start', 'stop', 'collection_start', 'collection_stop')
    int_types = ('input_counts', 'counts', 'events', 'total_time')
    cal_types = ('cal')

    if akey is not None:
        # First check, if was part of a dictionary. Check against special key types.
        if akey in float_types:
            athing = float(athing)
        elif akey in int_types:
            athing = int(athing)
        elif akey in date_types:
            if isinstance(athing, str):
                athing = dt.datetime.fromisoformat(athing)  # fromisoformat(val)
        elif akey in cal_types:
            acal = athing
            for key2, val2 in acal.items():
                try:
                    acal[key2] = np.asarray(val2).astype(float)
                except:
                    print(val2)
                    raise
            athing = acal
        else:
            # the key was none of the special ones. Normal operation continues
            pass
    if isinstance(athing, list):
        # Lists will be walked through and recursively desanitized
        for idx, val in enumerate(athing):
            athing[idx] = desanitize_json(val)
    elif isinstance(athing, dict):
        # Dicts are walked through and recursively desanitized, but the key is given to the function call
        for key, val in athing.items():
            athing[key] = desanitize_json(val, key)
    else:
        # Otherwise the value is passed through
        pass

    return athing


def json_pp(in_obj):
    """
    Prints a json object with 2 space indent and no sorting of dicts. PrettyPrint prints lists nicely spread out, but
    some replacements are still needed.
    """
    import pprint
    pp = pprint.PrettyPrinter(indent=2, sort_dicts=False)
    out_str = pp.pformat(in_obj)
    out_str = out_str.replace("'", '"')
    out_str = out_str.replace('False', 'false')
    out_str = out_str.replace('True', 'true')
    out_str = out_str.replace('None', 'null')
    return out_str


