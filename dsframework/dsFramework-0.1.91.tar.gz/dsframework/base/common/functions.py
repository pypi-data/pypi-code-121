import json
import pickle
from datetime import datetime

from dsframework.base.common.regex_handler import RegexHandler

regex = RegexHandler

##
# @file
# @brief This file has general functions that can simplify things when coding.



def flatten(d,sep="_"):
    """! Flatten dictionary recursively
       For example   : d = {"message": {"hello": 123456}}
        will return -> obj = {"message_hello": 123456}
      Args:
        d: the dictionary we want to flatten
      Returns:
        obj : break all dict in dict and return one flatten dict
    """
    import collections

    obj = collections.OrderedDict()

    def recurse(t, parent_key=""):

        if isinstance(t, dict):
            for k, v in t.items():
                recurse(v, parent_key + sep + k if parent_key else k)
        else:
            obj[parent_key] = t
    recurse(d)
    return obj


def get_from_dict(key, container:dict, default='', delete=False):
    """! Get value from the specific dictionary[key].
         Also, can delete item
        Args:
          key : dictionary key.
          container: the dictionary.
          default : empty string ('').
          delete(=False) : if TRUE delete container[key]
        Returns:
           val : from container[key] .
    """
    if not container or type(container) is not dict:
        return default
    if key in container:
        val = container[key]
        if delete:
            del container[key]
        return val
    return default


def get_date_time(short=False, no_space=False):
    """! Get date & time in required form
         default form example: 28/02/2022 11:59:59
      Args:
          short(default=False): only get date (example: 28_02_2022).
          no_space(default=False): No space (example: 20220328-0:00:59)
      Returns:
          string : which includes the time&date with the required form.
      """
    now = datetime.now()
    form = '%d/%m/%Y %H:%M:%S'
    if short:
        form = '%d_%m_%Y'
    elif no_space:
        form = "%Y%m%d-%H%M%S"
    dt_string = now.strftime(form)
    return dt_string


def load_pickle(path):
    """! Loads pickle file
     Args:
         path: Absolute path to data file.
     Returns:
         pkl : pickle file.
     """

    pkl = None
    with open(path, 'rb') as fid:
        pkl = pickle.load(fid)
    return pkl


def load_json(path):
    """! Loads json file
     Args:
         path: Absolute path to the file.
    Returns:
         jsn : json file.
    """
    jsn = None
    with open(path) as fid:
        jsn =  json.load(fid)
    return jsn 

def load_file_to_dict(in_file, sep=',', key_type=str, value_type=str):
    """! Loads file and parse him to a dictionary with (key , value )
     Args:
         in_file : the file we want to parse.
         sep (=',') : character separation
         key_type : The key type.
         value_type : The value type.
     Returns:
         dictionary : The dictionary created from the file.
     """
    dictionary = {}
    with open(in_file) as f:
        for line in f:
            (key, value) = line.rstrip('\n').split(sep)
            dictionary[key_type(key)] = value_type(value)
    return dictionary

def save_pickle(obj, path):
    """! Saves as a pickle
      Args:
          obj : the object we want to add to the file.
          path: Absolute path to the file.
    """
    with open(path, 'wb') as fid:
        pickle.dump(obj, fid)


def save_json(obj, path):
    """! Saves as a json
       Args:
           obj : the object we want to add to the file.
           path: Absolute path to the file.
     """
    with open(path, 'w') as f:
        json.dump(f, obj)


def remove_empty_leafs(d):
    """! Remove empty leafs from list or dictionary with recursion
       Args:
           d : list or dictionary.
       Returns:
           d : the same input without empty nodes.
    """
    if not isinstance(d, (dict, list)):
        return d
    if isinstance(d, list):
        return [v for v in (remove_empty_leafs(v) for v in d) if v]
    return {k: v for k, v in ((k, remove_empty_leafs(v)) for k, v in d.items()) if v}


def flatten_list(l):
    """! This function Flatten list and return it.
    @verbatim
    Args:
        l : List.
    Returns:
        list : flatten list
    @endverbatim
    """
    def get_el(el):
        if type(el) is not list:
            return [el]
        return el
    l2 = [get_el(el) for el in l]
    flatten = lambda l: [item for sublist in l for item in sublist]
    return flatten(l2)


def is_list_of_list(l):
    """! Is list of list bool function.
    @verbatim
    Args:
        l : List.
    Returns:
        bool: True if successful, False otherwise.
    @endverbatim
    """
    for el in l:
        if type(el) is list:
            return True
    return False


def ngram_splitter(line, ngram=3,all_grams=False):
    """! NGRAM splitter.
    @verbatim
    Args:
        line : Line .
        ngram (=3) :
        all_grams(=False) :
    Returns:
        string : splitted line (regarding the ngram number input)
    @endverbatim
    """
    tokens       = line.split(" ")
    loop_index   = 1
    result       = []
    ngram_window = []
    for token in tokens:
        ngram_window.append(token)
        if all_grams==False:
            if loop_index >= ngram:
                result.append(" ".join(ngram_window))
        else:
            for j in range(1,ngram+1):
                if loop_index >=j:
                    if len(result)<j:
                        result.append([" ".join(ngram_window[0:loop_index-1+j])])
                    else:
                        result[j-1].append(" ".join(ngram_window[min(loop_index-j,ngram-j):min(ngram,loop_index+j-1)]))
        if loop_index >= ngram:
            ngram_window = ngram_window[1:]
        loop_index +=1 
    return result


def remove_duplicates_lines(lines = []):
    """! Remove duplicates lines.
    @verbatim
    Args:
       lines : all the lines
    Returns:
       list : lines that are uniq from each other.
    @endverbatim
    """
    ls = lines
    lookup = set()  # a temporary lookup set
    ls = [x for x in ls if x not in lookup and lookup.add(x) is None]
    return ls 


def get_html_block_elements_list():
    """! This function returns the HTML block elements as a list.
        for example : ['<address', '<article', '<aside', '<blockquote',...]
    @verbatim
    Returns:
       list : HTML block elements.
    @endverbatim
     """
    return ['<address', '<article', '<aside', '<blockquote', '<canvas', '<dd', '<div',
            '<dl',
            '<dt', '<fieldset', '<figcaption', '<figure', '<footer', '<form', '<h1',
            '<h2', '<h3',
            '<h4', '<h5', '<h6', '<header', '<hr', '<li', '<main', '<nav',
            '<noscript', '<ol', '<p', '<pre', '<section', '<table', '<tfoot', '<ul',
            '<video']


def get_html_inline_elements_list():
    """! This function returns the HTML inline elements as a list.
        for example : ['<code', '<dfn', '<em',...]
    @verbatim
    Returns:
       list : HTML inline elements.
    @endverbatim
    """
    return ['<a', '<abbr', '<acronym', '<b', '<bdo', '<big', '<br', '<button', '<cite',
            '<code', '<dfn', '<em',
            '<i', '<img', '<input', '<kbd', '<label', '<map', '<object', '<output',
            '<q', '<samp', '<script',
            '<select', '<small', '<span', '<strong', '<sub', '<sup', '<textarea',
            '<time', '<tt', '<var']


def split_dataframe(df, batch_size=3):
    """
    Helper function that can chunk a dataframe according to a given chunk size
    :param df: Dataframe to divide
    :param batch_size: Batch size
    :return: A list of chunks, each the size of the desired batch size
    """
    chunks = list()
    num_chunks = len(df) // batch_size + 1
    for i in range(num_chunks):
        chunks.append(df[i * batch_size:(i + 1) * batch_size])
    return chunks

