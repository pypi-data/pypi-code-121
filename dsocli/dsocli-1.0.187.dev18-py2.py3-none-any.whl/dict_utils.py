import re
from unittest import result
from .logger import Logger
from .exceptions import DSOException



# def merge_dicts(source, destination):
#     if not source: return destination
#     for key, value in source.items():
#         if isinstance(value, dict):
#             if key in destination.keys():
#                 if not isinstance(destination[key], dict):
#                     raise Exception(f"Failed to merge '{key}' beacuse destination has an existing key with incompatible type ({type(destination[key])}) to that of the source ({type(source[key])}).")
#             else:
#                 destination[key] = {}
#             node = destination[key]
#             merge_dicts(value, node)
#         else:
#             destination[key] = value

#     return destination


# def merge_dicts(source: dict, destination: dict, merge_key=None):
    
#     if not isinstance(source, dict) or not isinstance(destination, dict):
#         raise Exception("Failed to merge, 'dict' type is expected for source and destination.")

#     def find_item(item, alist, merge_key=None):
#         if merge_key:
#             if callable(merge_key):
#                 found = [x for x in alist if merge_key(x) == merge_key(item)]
#             else:
#                 if isinstance(item, dict) and merge_key in item:
#                     found = [x for x in alist if x[merge_key] == item[merge_key]]
#                 else:
#                     found = [x for x in alist if x == item]
#         else:
#             found = [x for x in alist if x == item]

#         return found[0] if found else None

#     if not source: return destination
    
#     for key, value in source.items():
#         if isinstance(value, dict):
#             if key in destination.keys():
#                 if not isinstance(destination[key], dict):
#                     raise Exception(f"Failed to merge '{key}' beacuse destination has an existing key with incompatible type ({type(destination[key])}) to that of the source ({type(source[key])}).")
#             else:
#                 destination[key] = {}
#             node = destination[key]
#             merge_dicts(value, node, merge_key)
#         elif isinstance(value, list):
#             if key in destination.keys():
#                 if not isinstance(destination[key], list):
#                     raise Exception(f"Failed to merge '{key}' beacuse destination has an existing key with incompatible type ({type(destination[key])}) to that of the source ({type(source[key])}).")
#             else:
#                 destination[key] = []
#             for item in value:
#                 if not isinstance(item, dict):

#                 node = find_item(item, destination[key], merge_key)
#                 if node:
#                     if isinstance(node, dict):
#                         if not isinstance(item, dict):
#                             raise Exception("Failed to merge. Destination has an existing key with incompatible type.")
#                         merge_dicts(item, node, merge_key)
#                     else:
#                         if destination[key].index(item) < 0:
#                             destination[key].append(item)
#                 else:
#                     destination[key].append(item)
#         # elif isinstance(value, tuple):
#         #     raise NotImplementedError
#         # elif isinstance(value, set):
#         #     raise NotImplementedError
#         else:
#             destination[key] = value

#     return destination


def merge_dicts(source, destination, merge_key=None):
    
    def find_item(item, alist, merge_key=None):
        found = None
        if merge_key:
            if callable(merge_key):
                for x in alist:
                    if merge_key(x) == merge_key(item):
                        found = x
                        break
                # found = [x for x in alist if merge_key(x) == merge_key(item)]
            else:
                if isinstance(item, dict) and merge_key in item:
                    for x in alist:
                        if isinstance(x, dict) and merge_key in x and x[merge_key] == item[merge_key]:
                            found = x
                            break
                    # found = [x for x in alist if merge_key in x and x[merge_key] == item[merge_key]]
                else:
                    for x in alist:
                        if x == item:
                            found = x
                            break
                    # found = [x for x in alist if x == item]
        else:
            for x in alist:
                if x == item:
                    found = x
                    break

        return found

    if source is None: 
        return destination

    # if destination is None:
    #     destination = type(source)()

    if not type(source) == type(destination):
        raise Exception(f"Failed to merge source ({source}) and destination ({destination}) due to incompatible types: {type(source)} and {type(destination)}")

    if isinstance(source, dict):
        for key, value in source.items():
            if isinstance(value, dict) or isinstance(value, list) or isinstance(value, tuple):
                if not key in destination.keys(): destination[key] = type(value)()
                node = destination[key]
                merge_dicts(value, node, merge_key)
            else:
                destination[key] = value

    elif isinstance(source, list):
        for item in source:
            node = find_item(item, destination, merge_key)
            if node:
                if isinstance(node, dict) or isinstance(node, list) or isinstance(source, tuple):
                    merge_dicts(item, node, merge_key)
            else:
                destination.append(item)
    else:
        raise NotImplementedError


    return destination



def flatten_dict(input, prefixed_key = '', delimiter = '.'):
    def visit(input, prefixed_key, delimiter, output):
        if isinstance(input, dict):
            for key, value in input.items():
                new_key = f'{prefixed_key}{delimiter}{key}' if prefixed_key else f'{key}'
                visit(value, new_key, delimiter, output)
        elif isinstance(input, list):
            for idx, item in enumerate(input):
                new_key = f'{prefixed_key}{delimiter}{idx}' if prefixed_key else f'{idx}'
                visit(item, new_key, delimiter, output)
        else:
            output[prefixed_key] = input

        return output

    return visit(input, prefixed_key, delimiter, {})



def deflatten_dict(input: dict, delimiter = '.'):
    data = {}
    for key, value in input.items():
        set_dict_value(data, key.split(delimiter), value, overwrite_parent=True, overwrite_children=True)
    return data



def get_dict_item(dic, keys, create=True, default={}, leaf_only=False):
    for i in range(0, len(keys)):
        key = keys[i]
        if isinstance(dic, dict):
            if not key in dic.keys() or dic[key] is None:
                if create:
                    dic[key] = default.copy() ### !Important
                else:
                    return None
            dic = dic[key]
        elif isinstance(dic, list):
            key = int(key)
            if key >= len(dic):
                raise IndexError()
            dic = dic[key]
        else:
            raise NotImplementedError()
    if leaf_only and type(dic) in [dict, tuple]:
        return None
    return dic
    
def safe_str_to_number(s):
    try:
        return int(s.strip())
    except:
        try:
            return float(s.strip())
        except:
            return s
            




def set_dict_value(dic, keys, value, overwrite_parent=False, overwrite_children=False):
    
    def set_list_value(alist, idx, value):
        ### idx must be a number
        if idx < len(alist):
            if isinstance(alist[idx], dict) or isinstance(alist[idx], list) or isinstance(alist[idx], set) or isinstance(alist[idx], tuple):
                if overwrite_children:
                    Logger.warn("'{0}' was overwritten.".format('.'.join(keys)))
                else:
                    raise DSOException(f"DSO did not set '{'.'.join(keys)}' becasue it would otherwise overwrite an existing item '{'.'.join(keys)}' of type {type(alist)}`.")
            alist[idx] = value
        elif idx == len(alist):
            alist.append(value)
        else:
            raise DSOException(f"Index '{idx}' exceeded list size: {'.'.join(keys[:-1])}.{len(alist)}")

    lastKey = keys[-1]
    
    ### are we appending to a list?
    if lastKey == '*':
        parent_item = get_dict_item(dic, keys[:-1], create=True, default=[])
        if not isinstance(parent_item, list):
            raise DSOException(f"Index qualifiers can only be used with lists not with {type(parent_item)}.")
        lastKey = len(parent_item)
        keys[-1] = str(lastKey)
    else:
        ### are we dealing with a list?
        try:
            lastKey = int(lastKey)
        except:
            parent_item = get_dict_item(dic, keys[:-1], create=True, default={})
        else:
            parent_item = get_dict_item(dic, keys[:-1], create=True, default=[])     
            if not isinstance(parent_item, list):
                raise DSOException(f"Index qualifiers can only be used with lists not with {type(parent_item)}.")

    ### is value a comma separated list enclosed in brackets?
    if type(value) == str:
        if re.match(r'^\[(.*)\]$', value):
            value = re.sub(r"^\[", "", re.sub(r"\]$", "", value))
            value = list(map(lambda x: safe_str_to_number(x), re.findall('([^,]+)', value)))
            ### alow overrwrite the entire list
            if not lastKey in parent_item or parent_item[lastKey] is None or isinstance(parent_item[lastKey], list):
                overwrite_children = True
            else:
                raise DSOException(f"DSO did not set '{'.'.join(keys)}' becasue it would otherwise overwrite an existing item of type {type(parent_item[lastKey])}`.")
        else:
            value = safe_str_to_number(value)

    if isinstance(parent_item, list):
        set_list_value(parent_item, lastKey, value)

    elif isinstance(parent_item, dict):
        if lastKey in parent_item.keys():
            ### item is expected to be a basic type (string, number, ...)
            if isinstance(parent_item[lastKey], dict) or isinstance(parent_item[lastKey], list) or isinstance(parent_item[lastKey], set) or isinstance(parent_item[lastKey], tuple):
                if overwrite_children:
                    Logger.warn("'{0}' was overwritten.".format('.'.join(keys)))
                else:
                    raise DSOException(f"DSO did not set '{'.'.join(keys)}' becasue it would otherwise overwrite an existing item of type {type(parent_item[lastKey])}`.")
        parent_item[lastKey] = value
    else:
        if overwrite_parent or parent_item is None:
            grand_parent_item = get_dict_item(dic, keys[:-2])
            ### are we dealing with a list or a dict?
            if type(lastKey) == int:
                grand_parent_item[keys[-2]] = []
                parent_item = grand_parent_item[keys[-2]]
                set_dict_value(parent_item, lastKey, value)
            else:
                grand_parent_item[keys[-2]] = {}
                parent_item = grand_parent_item[keys[-2]]
                parent_item[lastKey] = value
        else:
            raise DSOException(f"DSO did not set '{'.'.join(keys)}' becasue it would otherwise overwrite an existing item '{'.'.join(keys[:-1])}' of type {type(parent_item)}.")

    return '.'.join(keys)


def del_dict_item(dic, keys, leaf_only=False, silent=False):
    parent_item = get_dict_item(dic, keys[:-1], create=False)
    if not parent_item:
        return False
    if type(parent_item) == dict:
        if not keys[-1] in parent_item:
            return False
        item = parent_item[keys[-1]]
        if isinstance(item, dict):
            if leaf_only:
                if not silent:
                    raise DSOException("'{0}' is a dictionary and cannot be deleted.".format('.'.join(keys)))
                return False

        parent_item.pop(keys[-1])
        return True

    elif type(parent_item) == list:
        if int(keys[-1]) >= len(parent_item):
            return False
        item =  parent_item[int(keys[-1])]

        if isinstance(item, dict):
            if leaf_only:
                if not silent:
                    raise DSOException("'{0}' is a dictionary and cannot be deleted.".format('.'.join(keys)))
                return False

        parent_item.pop(int(keys[-1]))
        return True
    else:
        raise NotImplementedError()



def del_dict_empty_item(dic, keys):
    item = get_dict_item(dic, keys)
    if not item:
        del_dict_item(dic, keys, leaf_only=False)
        if len(keys) > 1:
            del_dict_empty_item(dic, keys[:-1])





