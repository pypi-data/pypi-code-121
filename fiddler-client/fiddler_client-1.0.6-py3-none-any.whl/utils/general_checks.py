import re


def _name_check(name: str, max_length: int):
    if not name:
        raise ValueError(f'Invalid name {name}')
    if len(name) > max_length:
        raise ValueError(f'Name longer than {max_length} characters: {name}')
    if len(name) < 2:
        raise ValueError(f'Name must be at least 2 characters long: {name}')
    if not bool(re.match('^[a-z0-9_]+$', name)):
        raise ValueError(
            f'Name must only contain lowercase letters, '
            f'numbers or underscore: {name}'
        )
    if name[0].isnumeric():
        raise ValueError(f'Name must not start with a numerical character: {name}')


def safe_name_check(name: str, max_length: int, strict_mode: bool = True):
    if strict_mode:
        _name_check(name, max_length)


def is_greater_than_max_value(value, limit, epsilon=1e-9):
    """Check if 'value' is significantly larger than 'limit'.
    Where significantly means theres a greater difference than epsilon.
    """
    max_arg = abs(max(value, limit))
    tolerance = max_arg * epsilon
    # make sure that a is "significantly" smaller than b before declaring it
    # identified in DI for hired
    return value - tolerance > limit


def is_less_than_min_value(value, limit, epsilon=1e-9):
    """Check if 'value' is significantly smaller than 'limit'.
    Where significantly means theres a greater difference than epsilon.
    """
    max_arg = abs(max(value, limit))
    tolerance = max_arg * epsilon
    # make sure that a is "significantly" smaller than b before declaring it
    # identified in DI for hired
    return value + tolerance < limit


def type_enforce(param_name: str, param_val, required_type):
    """
    :param param_name: Name of parameter being type enforced. Used for valid error
    :param param_val: Value being type enforced
    :param required_type: Casted type that is being enforced
    """
    if isinstance(param_val, required_type):
        return param_val  # should perhaps be required_type(param_val)?
    else:
        try:
            return required_type(param_val)
        except ValueError:
            raise ValueError(
                f'Parameter `{param_name}` must be of type {required_type}'
            )


def is_int_type(value):
    if isinstance(value, int):
        return True, value
    try:
        int_val = int(value)
        return True, int_val
    except ValueError:
        return False, None


def do_not_proceed(query: str):
    """
    Returns True if the users inputs n/no, False for yes/y

    :param query: Message displayed to the user

    Raises ValueError for invalid inputs
    """
    user_str = input(query)
    user_str = user_str.strip().lower()
    if user_str in ['y', 'yes']:
        return False
    elif user_str in ['n', 'no']:
        return True
    else:
        err_msg = 'Invalid response to the prompt, expecting one of y, n'
        raise ValueError(err_msg)
