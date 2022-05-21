import cProfile
from functools import wraps
import datetime
import inspect


def retrieve_name(var):
    """
    Gets the name of var. Does it from the out most frame inner-wards.
    :param var: variable to get name from.
    :return: string
    """
    for fi in reversed(inspect.stack()):
        names = [var_name for var_name, var_val in fi.frame.f_locals.items() if var_val is var]
        if len(names) > 0:
            return names[0]

def prnt(val, label='', val_newline=True):
    '''
    Print wrapper for clear logging
    '''
    if not label:
        label = retrieve_name(val)
    newline_add = '\n' if val_newline else ''
    print(f"\n{label}: {newline_add}{val}\n", flush=True)


def prnt_label_val(val, label='undefined label'):
    # print wrapper that prints label and then value on next line with indentation
    print(f"{label}\n    {val}")


def print_keys(dict_, depth=0):
    '''
    prints keys recursively at a certain <depth> and indents based on <depth> (times 2)
    '''
    for key in dict_:
        print(f"{' ' * depth * 2}{key}")
        if isinstance(dict_[key], dict):
            print_keys(dict_[key], depth+1)


def print_items(dict_, depth=0):
    for key in dict_:
        print(f"{' ' * depth * 2}{key}")
        if isinstance(dict_[key], dict):
            print_items(dict_[key], depth+1)
        elif isinstance(dict_[key], list):
            print("\n")
            for item_ in dict_[key]:
                print(f"{' ' * (depth + 1) * 2}{item_}")
            print("\n")
        else:
            print(f"\n{' ' * (depth + 1) * 2}{dict_[key]}\n")

def prnt_attrs(obj, *attrs, incl_dir=True):
    if incl_dir:
        prnt(dir(obj))
    for attr in attrs:
        try:
            prnt(getattr(obj, attr), attr)
        except AttributeError:
            prnt(f'{obj} has no attribute: {attr}')

def print_object_attrs(obj, len_limit=1000, try_call_functions=False):

    def print_truncated_label_value(label, value):
        try:
            if len(value) > len_limit:
                prnt_label_val(f'{value[:len_limit]}\n\n...\n\t\tValue truncated to first {len_limit} characters', label)
            else:
                prnt_label_val(value, label)
        except:
            prnt_label_val('No value could be determined', label)


    if try_call_functions:
        for attr in dir(obj):
            if callable(getattr(obj, attr)):
                try:
                    value = getattr(obj, attr)()
                    print_truncated_label_value(attr, value)
                except:
                    prnt_label_val(f'ERROR calling {getattr(obj, attr)}', attr)
            else:
                value = getattr(obj, attr)
                print_truncated_label_value(attr, value)

    else:
        for attr in dir(obj):
            value = getattr(obj, attr)
            print_truncated_label_value(attr, value)


def get_item_with_largest_val(items, attr, attr_type='int'):
    '''
    probably needs rewriting

    input is expected to be an object of objects or a list of objects

    returns object from <item>'s objects that has largest val of <attr>
    '''

    output_item = None
    if isinstance(items, list):
        for obj in items:
            if not output_item:
                output_item = obj

            if attr_type == 'int':
                if int(output_item[attr]) < int(obj[attr]):
                    output_item = obj

    elif isinstance(items, object):

        for key in items:
            if not output_item:
                output_item = items[key]

            if attr_type == 'int':
                if int(output_item[attr]) < int(items[key][attr]):
                    output_item = items[key]

    return output_item


def get_objects_with_attr_val(objects, attr, val):
    '''
    returns list of objects from input list/object <objects> that has an <attr> value of <val>
    '''

    output = []

    if isinstance(objects, object):
        for obj in objects:
            if objects[obj][attr] == val:
                output.append(obj)

    elif isinstance(objects, list):
        for obj in objects:
            if obj[attr] == val:
                output.append(obj)

    return output


def combine_lists(list1, list2):
    # lists must be of same size or list2 must be 1 less than list1
    output = []
    for i in range(len(list1)):
        output.append(list1[i])
        try:
            output.append(list2[i])
        except IndexError:
            pass
    return output

def print_command_history():
    import readline
    for i in range(readline.get_current_history_length()):
        print (readline.get_history_item(i + 1))

def convert_to_iso_8601(datetime_obj):
    # returns iso8601 string
    return datetime_obj.strftime('%Y-%m-%dT%H:%M:%SZ')

def convert_from_iso_8601(iso8601_string):
    # returns datetime obj
    return datetime.datetime.strptime(iso8601_string, '%Y-%m-%dT%H:%M:%SZ')
