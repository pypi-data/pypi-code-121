
def is_objects_list(name, config_dict):
    """Check if the given configuration is an objects list.

    Args:
        config_dict (any): A configuration

    Returns:
        bool: True if 'config_dict' is a dictionary that defines an objects list
    """
    if not isinstance(config_dict, list) or len(config_dict) == 0:
        return False
    for obj in config_dict:
        if not is_object("", obj):
            return False
    return True


def is_object(name, config_dict):
    """Checks if the given configuration defines an object.

    Args:
        config_dict (any): A configuration

    Returns:
        bool: True if 'config_dict' is a dictionary that defines an object
    """
    from .variables import SingleObjectTag
    if not isinstance(config_dict, dict):
        return False
    keys = list(config_dict.keys())
    return len(keys) == 1 and isinstance(keys[0], SingleObjectTag)


def is_var(name, config_dict):
    """Checks if the given configuration defines a variable

    Args:
        config_dict (any): A configuration

    Returns:
        bool: True if 'config_dict' defines a variable
    """  
    return isinstance(config_dict, int) or isinstance(config_dict, float) or isinstance(config_dict, str)


def is_list(name, config_dict):
    return not is_objects_list(name, config_dict) and isinstance(config_dict, list)

def is_config(name, config_dict):
    return isinstance(config_dict, dict)

def is_from(name, config_dict):
    from .variables import FromTag
    return isinstance(name, FromTag)

def valid_var_name(name : str):
    """Raise an error if 'name' is not a valid Variable name.

    Args:
        name (str): Name of the variable

    Raises:
        ValueError: If name contains caracters that are not alphabetical or numerical
        ValueError: If name begin with a number
    """
    if name == "":
        return 
    stripped_name = name.replace("_", "")
    if stripped_name == "":
        raise ValueError(f"Variable '{name}' cannot contain only underscores.")
    if not stripped_name.isalnum():
        raise ValueError(f"Variable '{name}' must contain alphabetical or numerical caracters or underscores.")
    if not name[0].isalpha() or name[0] == "_":
        raise ValueError(f"Variable '{name}' must begin with an alphabetical caracter or an underscore.")