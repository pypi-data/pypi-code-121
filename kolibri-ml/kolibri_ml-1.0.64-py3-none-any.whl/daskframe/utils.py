from kdmt.infer import is_list_value,is_list_of_one_element, is_dict_of_one_element, is_url, is_int, is_list_of_int, is_list_of_tuples, is_str, is_list_of_list, is_tuple
from kdmt.lists import val_to_list, one_list_to_val
from kdmt.errors import RaiseError
import os
from glob import glob
import ntpath
import regex as re
from urllib.request import Request, urlopen
import tempfile
from kolibri.logger import get_logger

logger=get_logger(__name__)

from ordered_set import OrderedSet


def escape_columns(columns):
    """
    Add a backtick to a columns name to prevent the dot in name problem
    :param columns:
    :return:
    """

    escaped_columns = []
    if is_list_value(columns):
        for col in columns:
            # Check if the column is already escaped
            if col[0] != "`" and col[len(col) - 1] != "`":
                escaped_columns.append("`" + col + "`")
            else:
                escaped_columns.append(col)
    else:
        # Check if the column is already escaped
        if columns[0] != "`" and columns[len(columns) - 1] != "`":
            escaped_columns = "`" + columns + "`"
        else:
            escaped_columns.append(columns)

    return escaped_columns


def parse_data_types(df, value):
    """
    Get the data type from a string data type representation. for example 'int' from 'uint64'
    :param value:
    :param df:
    :return:
    """

    value = val_to_list(value)

    data_type = []

    for v in value:
        v = df.constants.INTERNAL_TO_OPTIMUS.get(v, v)
        data_type.append(v)

    return one_list_to_val(data_type)

def names_by_data_types(df, data_type):
    """
    Return column names filtered by the column data type
    :param df: Dataframe which columns are going to be filtered
    :param data_type: Datatype used to filter the column.
    :type data_type: str or list
    :return:
    """
    parsed_data_type = parse_data_types(df, data_type)
    data_type = val_to_list(data_type)
    parsed_data_type = val_to_list(parsed_data_type)
    # Filter columns by data type
    result = []
    for col_name in df.cols.names():
        found_parsed_data_type = df.cols.schema_data_type(col_name)
        found_data_type = df.cols.data_types(col_name)
        if any([dt in found_parsed_data_type for dt in parsed_data_type])\
        or any([dt in found_data_type for dt in data_type]):
            result.append(col_name)
    return result


def check_for_missing_columns(df, col_names):
    """
    Check if the columns you want to select exits in the dataframe
    :param df: Dataframe to be checked
    :param col_names: cols names to
    :return:
    """
    _col_names = df.cols.names()
    missing_columns = list(OrderedSet(col_names) - OrderedSet(_col_names))

    if len(missing_columns) > 0:
        RaiseError.value_error(missing_columns, _col_names)
    return False

def format_dict(_dict, tidy=True):
    """
    This function format a dict. If the main dict or a deep dict has only on element
     {"col_name":{0.5: 200}} we get 200
    :param _dict: dict to be formatted
    :param tidy:
    :return:
    """

    if tidy is True:
        levels = 2
        while (levels >= 0):
            levels -= 1
            if is_list_of_one_element(_dict):
                _dict = _dict[0]
            elif is_dict_of_one_element(_dict):
                _dict = next(iter(_dict.values()))
            else:
                return _dict

    else:
        if is_list_of_one_element(_dict):
            return _dict[0]
        else:
            return _dict

def downloader(url, file_format):
    """
    Send the request to download a file
    """

    def write_file(response, file, chunk_size=8192):
        """
        Load the data from the http request and save it to disk
        :param response: data returned from the server
        :param file:
        :param chunk_size: size chunk size of the data
        :return:
        """
        total_size = response.headers['Content-Length'].strip() if 'Content-Length' in response.headers else 100
        total_size = int(total_size)
        bytes_so_far = 0

        while 1:
            chunk = response.read(chunk_size)
            bytes_so_far += len(chunk)
            if not chunk:
                break
            file.write(chunk)
            total_size = bytes_so_far if bytes_so_far > total_size else total_size

        return bytes_so_far

    # try to infer the file format using the file extension
    if file_format is None:
        filename, file_format = os.path.splitext(url)
        file_format = file_format.replace('.', '')

    i = url.rfind('/')
    data_name = url[(i + 1):]

    headers = {"User-Agent": "Optimus Data Downloader/1.0"}

    req = Request(url, None, headers)

    logger.print("Downloading %s from %s", data_name, url)

    # It seems that avro need a .avro extension file
    with tempfile.NamedTemporaryFile(suffix="." + file_format, delete=False) as f:
        bytes_downloaded = write_file(urlopen(req), f)
        path = f.name

    if bytes_downloaded > 0:
        logger.print("Downloaded %s bytes", bytes_downloaded)

    logger.print("Creating DataFrame for %s. Please wait...", data_name)

    return path

def prepare_path(path, file_format=None):
    """d
    Helper to return the file to be loaded and the file name.
    This will memoise
    :param path: Path to the file to be loaded
    :param file_format: format file
    :return:
    """
    r = []
    if is_url(path):
        file = downloader(path, file_format)
        file_name = ntpath.basename(path)
        r = [(file, file_name,)]
    else:
        for file_name in glob.glob(path, recursive=True):
            r.append((file_name, ntpath.basename(file_name),))
    if len(r) == 0:
        raise Exception("File not found")
    return r


def parse_columns(df, cols_args, is_regex=None, filter_by_column_types=None, accepts_missing_cols=False, invert=False):
    """
    Return a list of columns and check that columns exists in the spark
    Accept '*' as parameter in which case return a list of all columns in the spark.
    Also accept a regex.
    If a list of tuples return to list. The first element is the columns name the others element are params.
    This params can be used to create custom transformation functions. You can find and example in cols().cast()
    :param df: Dataframe in which the columns are going to be checked
    :param cols_args: Accepts * as param to return all the string columns in the spark
    :param is_regex: Use True is cols_args is a regex
    :param filter_by_column_types: A data type for which a columns list is going be filtered
    :param accepts_missing_cols: if true not check if column exist in the spark
    :param invert: Invert the final selection. For example if you want to select not integers

    :return: A list of columns string names
    """

    # if columns value is * get all dataframes columns

    df_columns = df.cols.names()

    if is_regex is True:
        r = re.compile(cols_args)
        cols = list(filter(r.match, df_columns))

    elif cols_args == "*" or cols_args is None:
        cols = df_columns

    elif is_int(cols_args):
        cols = val_to_list(df_columns[cols_args])

    elif is_list_of_int(cols_args):
        cols = list(df_columns[i] for i in cols_args)

    elif is_tuple(cols_args) or is_list_of_tuples(cols_args):
        # In case we have a list of tuples we use the first element of the tuple is taken as the column name
        # and the rest as params. We can use the param in a custom function as follow
        # def func(attrs): attrs return (1,2) and (3,4)
        #   return attrs[0] + 1
        # df.cols().apply([('col_1',1,2),('cols_2', 3 ,4)], func)

        # Verify if we have a list with tuples

        cols_args = val_to_list(cols_args)
        # Extract a specific position in the tuple
        cols = [(i[0:1][0]) for i in cols_args]
        attrs = [(i[1:]) for i in cols_args]

    else:
        # if not a list convert to list
        cols = val_to_list(cols_args)
        # Get col name from index
        cols = [c if is_str(c) else df_columns[c] for c in cols]

    # Check for missing columns
    if accepts_missing_cols is False:
        check_for_missing_columns(df, cols)

    # Filter by column data type
    filter_by_column_types = val_to_list(filter_by_column_types)
    if is_list_of_list(filter_by_column_types):
        filter_by_column_types = [
            item for sublist in filter_by_column_types for item in sublist]

    columns_residual = None

    # If necessary filter the columns by data type
    if filter_by_column_types:
        # Get columns for every data type
        columns_filtered = names_by_data_types(
            df, filter_by_column_types)

        # Intersect the columns filtered per data type from the whole spark with the columns passed to the function
        final_columns = list(OrderedSet(cols).intersection(columns_filtered))

        # This columns match filtered data type
        columns_residual = list(OrderedSet(cols) - OrderedSet(columns_filtered))

    else:
        final_columns = cols

    cols_params = []
    if invert:
        final_columns = list(OrderedSet(df_columns) - OrderedSet(final_columns))

    cols_params = final_columns

    if columns_residual:
        logger.print("%s %s %s", ",".join(escape_columns(columns_residual)),
                     "column(s) was not processed because is/are not",
                     ",".join(filter_by_column_types))

    # if because of filtering we got 0 columns return None
    if len(cols_params) == 0:
        cols_params = None
        logger.print("Outputting 0 columns after filtering. Is this expected?")

    return cols_params


