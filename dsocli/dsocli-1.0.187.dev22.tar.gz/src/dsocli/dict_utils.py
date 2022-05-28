import re
from unittest import result
from venv import create
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
            if isinstance(value, dict) or isinstance(value, list):
                if not key in destination.keys(): destination[key] = type(value)()
                node = destination[key]
                merge_dicts(value, node, merge_key)
            else:
                destination[key] = value

    elif isinstance(source, list):
        for item in source:
            node = find_item(item, destination, merge_key)
            if node:
                if isinstance(node, dict) or isinstance(node, list):
                    merge_dicts(item, node, merge_key)
            else:
                destination.append(item)
    else:
        raise NotImplementedError


    return destination



def flatten_dict(input, prefixed_key = '', delimiter = '.', atomic_list=True):
    def visit(input, prefixed_key, delimiter, output):
        if isinstance(input, dict):
            for key, value in input.items():
                new_key = f'{prefixed_key}{delimiter}{key}' if prefixed_key else f'{key}'
                visit(value, new_key, delimiter, output)
        elif isinstance(input, list):
            if atomic_list:
                output[prefixed_key] = input        
            else:
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
        set_item(data, key.split(delimiter), value, overwrite_parent=True, overwrite_children=True)
    return data



# def get_item(data, keys, create=True, default={}, leaf_only=False):
#     for i in range(len(keys)):
#         key = keys[i]
#         if isinstance(data, dict):
#             if not key in data.keys() or data[key] is None:
#                 if create:
#                     data[key] = default.copy() ### !Important
#                 else:
#                     return None
#             data = data[key]
#         elif isinstance(data, list):
#             if key == '*':
#                 key = len(data)

#             key = int(key)
#             if key >= len(data):
#                 raise DSOException(f"Index '{key}' exceeded list size: {'.'.join(keys[:-1])}.{len(data)-1}")
#             data = data[key]
#         else:
#             raise NotImplementedError()
#     if leaf_only and type(data) in [dict]:
#         return None
#     return data
    


def safe_str_to_number(s):
    try:
        return int(s.strip())
    except:
        try:
            return float(s.strip())
        except:
            return s
            

def is_number(s):
    try:
        return type(int(s.strip())) == int
    except:
        try:
            return type(float(s.strip())) == float
        except:
            return False
            

def is_int(s):
    try:
        return type(int(s.strip())) == int
    except:
        return False
            

def get_item(data, keys, create=True, default={}, leaf_only=False):
    def create_new_item(keys, default):
        ### is this a leaf item?
        if len(keys) == 1:
            return default.copy() ### !Important
        else:
            ### decide type of the new item based on the next key
            if keys[1] == '*' or is_int(keys[1]):
                return [].copy() ### !Important
            else:
                return {}.copy() ### !Important

    def get_next_item(parent, keys, create, default):
        if type(parent) == dict:
            if not keys[0] in parent.keys() or parent[keys[0]] is None:
                if create:
                    parent[keys[0]] = create_new_item(keys, default)
                else:
                    return None, keys
            return parent[keys[0]], keys
        elif type(parent) == list:
            if keys[0] == '*':
                ### '*' is allowed only when creating/appending is enabled
                if not create:
                    return None, keys
                keys[0] = str(len(parent))
                parent.append(create_new_item(keys, default))
            else:
                if not is_int(keys[0]):
                    Logger.warn(f"Encountered a list but invalid index qualifier '{keys[0]}' provided: {parent}")
                    return None, keys
            
            if int(keys[0]) >= len(parent):
                raise DSOException(f"Index '{keys[0]}' exceeded the last index of list: {len(parent)-1}")

            return parent[int(keys[0])], keys

    if len(keys) == 0 or data is None:
        return data, keys
    if len(keys) == 1:
        if not type(data) in [dict, list]:
            return None, keys
        item, keys = get_next_item(data, keys, create, default)
    else:
        parent, keys = get_next_item(data, keys, create, default)
        item, keys2 = get_item(parent, keys[1:], create, default)
    
    if leaf_only and type(item) == dict:
        return None, keys
    else:
        return item, keys



def set_item(dic, keys, value, overwrite_parent=False, overwrite_children=False):
    
    def set_list_value(alist, idx, value):
        idx = int(idx)
        if idx < len(alist):
            if type(alist[idx]) == dict:
                if overwrite_children:
                    Logger.warn("'{0}' was overwritten.".format('.'.join(keys)))
                else:
                    raise DSOException(f"DSO did not set '{'.'.join(keys)}' becasue it would otherwise overwrite an existing item '{'.'.join(keys)}' of type {type(alist)}`.")
            alist[idx] = value
        elif idx == len(alist):
            alist.append(value)
        else:
            raise DSOException(f"Index '{idx}' exceeded the last index of list: {len(alist)-1}")
    
        return idx

    if not keys:
        return
        
    lastKey = keys[-1]
    parent, keys = get_item(dic, keys[:-1], create=True, default={}, leaf_only=False)
    if lastKey == '*':
        if not isinstance(parent, list):
            raise DSOException(f"Index qualifiers can only be used with lists not {type(parent)}.")
        ### append to the list
        lastKey = len(parent)
    elif is_int(lastKey):
        lastKey = int(lastKey)

    keys.append(str(lastKey))


    ### is value a comma separated list enclosed in brackets?
    if type(value) == str:
        if re.match(r'^\[(.*)\]$', value):
            value = re.sub(r"^\[", "", re.sub(r"\]$", "", value))
            value = list(map(lambda x: safe_str_to_number(x.strip()), re.findall('([^,]+)', value)))
            ### alow overrwrite the entire list
            if not lastKey in parent or parent[lastKey] is None or not type(parent[lastKey]) in [dict]:
                overwrite_children = True
            else:
                raise DSOException(f"DSO did not set '{'.'.join(keys)}' becasue it would otherwise overwrite an existing item of type {type(parent[lastKey])}`.")
        else:
            value = safe_str_to_number(value)


    if isinstance(parent, list):
        set_list_value(parent, lastKey, value)
    elif isinstance(parent, dict):
        if lastKey in parent.keys():
            ### item is expected to be a basic type (string, number, ...)
            if type(parent[lastKey]) == dict:
                if overwrite_children:
                    Logger.warn("'{0}' was overwritten.".format('.'.join(keys)))
                else:
                    raise DSOException(f"DSO did not set '{'.'.join(keys)}' becasue it would otherwise overwrite an existing item of type {type(parent[lastKey])}`.")
        parent[lastKey] = value
    else:
        if overwrite_parent or parent is None:
            grand_parent = get_item(dic, keys[:-2])[0]
            ### are we dealing with a list or a dict?
            if type(lastKey) == int:
                grand_parent[keys[-2]] = []
                parent = grand_parent[keys[-2]]
                set_item(parent, lastKey, value)
            else:
                grand_parent[keys[-2]] = {}
                parent = grand_parent[keys[-2]]
                parent[lastKey] = value
        else:
            raise DSOException(f"DSO did not set '{'.'.join(keys)}' becasue it would otherwise overwrite an existing item '{'.'.join(keys[:-1])}' of type {type(parent)}.")

    return value, keys


def del_item(dic, keys, leaf_only=False, silent=False):
    parent = get_item(dic, keys[:-1], create=False)[0]
    if not parent:
        return False
    if type(parent) == dict:
        if not keys[-1] in parent:
            return False
        item = parent[keys[-1]]
        if isinstance(item, dict):
            if leaf_only:
                if not silent:
                    raise DSOException("'{0}' is a dictionary and cannot be deleted.".format('.'.join(keys)))
                return False

        parent.pop(keys[-1])
        return True

    elif type(parent) == list:
        if int(keys[-1]) >= len(parent):
            return False
        item =  parent[int(keys[-1])]

        if isinstance(item, dict):
            if leaf_only:
                if not silent:
                    raise DSOException("'{0}' is a dictionary and cannot be deleted.".format('.'.join(keys)))
                return False

        parent.pop(int(keys[-1]))
        return True
    else:
        raise NotImplementedError()



def del_dict_empty_item(dic, keys):
    item = get_item(dic, keys)[0]
    if not item:
        del_item(dic, keys, leaf_only=False)
        if len(keys) > 1:
            del_dict_empty_item(dic, keys[:-1])





