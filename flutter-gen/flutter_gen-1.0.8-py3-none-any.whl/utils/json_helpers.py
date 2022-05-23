def get_keys(some_dictionary, list=[], separator="_", parent=None):
    if isinstance(some_dictionary, str):
        return
    for key, value in some_dictionary.items():
        if parent is None:
            path = "{}".format(key)
        else:
            path = "{}{}{}".format(parent, separator, key)
        if key not in list:
            list.append(path)
        if isinstance(value, dict):
            get_keys(value, list, separator, parent=path)
        else:
            pass