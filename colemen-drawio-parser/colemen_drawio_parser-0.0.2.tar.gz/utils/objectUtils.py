
# pylint: disable=missing-function-docstring
# pylint: disable=missing-class-docstring

def get_kwarg(key_name, default_val=False, value_type=None, **kwargs):
    kwargs = keys_to_lower(kwargs)
    if isinstance(key_name, list) is False:
        key_name = [key_name]

    for name in key_name:
        # generate basic variations of the name
        varis = _gen_variations(name)
        for v_name in varis:
            if v_name in kwargs:
                if value_type is not None:
                    if isinstance(kwargs[v_name], value_type) is True:
                        return kwargs[v_name]
                else:
                    return kwargs[v_name]
    return default_val


def _gen_variations(string):
    string = str(string)
    varis = []
    lower = string.lower()
    upper = string.upper()
    snake_case = lower.replace(" ", "_")
    screaming_snake_case = upper.replace(" ", "_")
    varis.append(lower)
    varis.append(upper)
    varis.append(snake_case)
    varis.append(screaming_snake_case)
    return varis

def keys_to_lower(dictionary):
    '''
        Converts all keys in a dictionary to lowercase.
    '''
    return {k.lower(): v for k, v in dictionary.items()}

def get_unique_keys(obj, **kwargs):
    '''
        Gets all unique keys in the object provided.

        @param {dict|list} obj - The object or list to search for keys within.
        @param {boolean} [**sort_list=True] - Sort the list alphabetically.
        @param {boolean} [**case_sensitive=True] - If True the case of the key is ignored.
        @param {boolean} [**force_lowercase=True] - Convert all keys to lowercase.
        @param {boolean} [**recursive=True] - Recurse into nested objects to find keys.
        @param {int} [**max_depth=500] - The maximum recursions it is allowed to make.
        @return {list} A list of unique keys from the object, if none are found the list is empty.
        @function get_unique_keys
    '''

    __current_depth = get_kwarg(['__current_depth'], 0, int, **kwargs)
    sort_list = get_kwarg(['sort_list'], False, bool, **kwargs)
    case_sensitive = get_kwarg(['case_sensitive'], True, bool, **kwargs)
    force_lowercase = get_kwarg(['force_lowercase'], True, bool, **kwargs)
    recursive = get_kwarg(['recursive'], True, bool, **kwargs)
    max_depth = get_kwarg(['max_depth'], 500, int, **kwargs)
    kwargs['__current_depth'] = __current_depth + 1

    keys = []

    if recursive is True and __current_depth < max_depth:
        if isinstance(obj, (list, tuple, set)):
            for element in obj:
                if isinstance(element, (list, dict)):
                    keys = keys + get_unique_keys(element, **kwargs)

    if isinstance(obj, dict):
        keys = list(obj.keys())

        if recursive is True and __current_depth < max_depth:
            # pylint: disable=unused-variable
            for k, value in obj.items():
                # find nested objects
                if isinstance(value, (list, dict, tuple, set)):
                    keys = keys + get_unique_keys(value, **kwargs)

    if case_sensitive is True:
        output = []
        lkkeys = []
        for key in keys:
            low_key = key.lower()
            if low_key not in lkkeys:
                output.append(key)
                lkkeys.append(low_key)
        keys = output

    if force_lowercase is True:
        keys = [x.lower() for x in keys]

    keys = list(set(keys))

    if sort_list is True:
        keys = sorted(keys, key=lambda x: int("".join([i for i in x if i.isdigit()])))
    return keys

def find_list_diff(list_one, list_two):
    '''
        find elements in list_one that do not exist in list_two.
        @param {list} list_one the primary list for comparison
        @param {list} list_two
        @function findListDiff
    '''
    return [x for x in list_one if x not in list_two]

def set_defaults(default_vals, obj):
    '''
        Sets default values on the dict provided, if they do not already exist.

        ----------

        Arguments
        -------------------------
        `default_vals` {dict}
            The default values to set on the obj.
        `obj` {dict}
            The object to assign default values to.

        Keyword Arguments
        -------------------------
        `arg_name` {type}
                arg_description

        Return {dict}
        ----------------------
        The obj with default values applied

        Meta
        ----------
        `author`: Colemen Atwood
        `created`: 12-09-2021 08:04:03
        `memberOf`: object_utils
        `version`: 1.0
        `method_name`: set_defaults
    '''
    for k, v in default_vals.items():
        if k not in obj:
            obj[k] = v
        # print(f"k: {k} - v: {v}")
    return obj

def get_arg(args,key_name,default_val=False, value_type=None):
    if isinstance(args,(dict)) is False:
        return default_val
    if len(args.keys()) == 0:
        return default_val
    
    args = keys_to_lower(args)
    # if defaults is not None:
    #     defaults = keys_to_lower(defaults)
    #     args = set_defaults(defaults,args)

    if isinstance(key_name, list) is False:
        key_name = [key_name]

    for name in key_name:
        # generate basic variations of the name
        varis = _gen_variations(name)
        for v_name in varis:
            if v_name in args:
                if value_type is not None:
                    if isinstance(args[v_name], value_type) is True:
                        return args[v_name]
                else:
                    return args[v_name]
    return default_val

