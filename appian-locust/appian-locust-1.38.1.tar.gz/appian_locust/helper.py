import functools
import random
import re
from typing import Any, Callable, Dict, Generator, List, Union, Optional
from .exceptions import ComponentNotFoundException

import gevent  # type: ignore
from locust.env import Environment

from . import logger

ENV = Environment()
log = logger.getLogger(__name__)


def format_label(label: str, delimiter: str = None, index: int = 0) -> str:
    """
    Simply formats the string by replacing a space with underscores

    Args:
        label: string to be formatted
        delimiter: If provided, string will be split by it
        index: used with delimiter parameter, which item will be used in the "split"ed list.

    Returns:
        formatted string

    """
    if delimiter:
        if not str(index).isnumeric():
            index = 0
        label = label.split(delimiter)[int(index)]

    return label.replace(" ", "_")


def extract(obj: Any, key: str, val: Any) -> Generator:
    """Recursively search for values of key in JSON tree."""
    if isinstance(obj, dict):
        for k, v in obj.items():
            if isinstance(v, (dict, list)):
                yield from extract(v, key, val)
            elif k == key and v == val:
                yield obj

    elif isinstance(obj, list):
        for item in obj:
            yield from extract(item, key, val)


def extract_values(obj: Dict[str, Any], key: str, val: Any) -> List[Dict[str, Any]]:
    """
    Pull all values of specified key from nested JSON.

    Args:
        obj (dict): Dictionary to be searched
        key (str): tuple of key and value.
        value (any): value, which can be any type

    Returns:
        list of matched key-value pairs

    """
    return list(extract(obj, key, val))


def extract_item_by_label(obj: Union[dict, list], label: str) -> Generator:
    """
    Recursively search for all fields with a matching label in JSON tree.
    And return as a generator
    """
    if isinstance(obj, dict):
        for k, v in obj.items():
            if k == label:
                yield v
            yield from extract_item_by_label(v, label)
    elif isinstance(obj, list):
        for v in obj:
            yield from extract_item_by_label(v, label)


def extract_all_by_label(obj: Union[dict, list], label: str) -> list:
    """Recursively search for all fields with a matching label in JSON tree."""
    return [elem for elem in extract_item_by_label(obj, label)]


def get_random_item(list_of_items: List[Any], exclude: List[Any] = []) -> Any:
    """
    Gets a random item from the given list excluding the items if any provided

    Args:
        list_of_items: list of items of any data type
        exclude: if any items needs to be excluded in random pick

    Returns:
        Randomly picked Item

    Raises:
        In case of no item to pick, Exception will be raised
    """
    count = len(list_of_items)
    while count != 0:
        selected_item = random.SystemRandom().choice(list_of_items)
        if selected_item not in exclude:
            return selected_item
        else:
            count = count - 1
    raise(Exception("There is no item to select randomly"))


def list_filter(list_var: List[str], filter_string: str, exact_match: bool = False) -> List[str]:
    """
    from the given list, return the list with filtered values.

    Args:
        list_var (list): list of strings
        filter_string (str): string which will be used to filter
        exact_match (bool, optional): filter should be based on exact match or partial match. default is partial.

    Returns:
        List with filtered values

    """
    # Exact Matches gets priority even when exact match is set to false
    return_list = list(filter(lambda current_item: (
        current_item == filter_string), list_var))
    if not exact_match:
        return_list = list(filter(lambda current_item: (
            current_item == filter_string), list_var))
        return_list.extend(list(filter(lambda current_item: (
            bool(re.search(".*" + re.escape(filter_string) + ".*", current_item)) and current_item not in return_list),
            list_var)))
    return return_list


def _validate_component_found(component: Optional[Dict[str, Any]], label: str, type: Optional[str] = None) -> None:
    if not component:
        optional_type_info = f" of type '{type}'" if type else ''
        msg = f"Could not find the component with label '{label}'{optional_type_info} in the provided form"
        raise ComponentNotFoundException(msg)


def _validate_component_found_by_index(component: Optional[Dict[str, Any]], index: int, type: Optional[str] = None) -> None:
    if not component:
        optional_type_info = f" of type '{type}'" if type else ''
        msg = f"Could not find the component at index '{index}'{optional_type_info} in the provided form"
        raise ComponentNotFoundException(msg)


def _validate_component_found_by_attribute(component: Dict[str, Any], attribute: str, value_for_attribute: str) -> None:
    if not component:
        raise ComponentNotFoundException(
            f'''Could not find the component with attribute '{attribute}' and
            its value: '{value_for_attribute}' in the provided form
            ''')


def find_component_by_attribute_in_dict(attribute: str, value: str, component_tree: Dict[str, Any], raise_error: bool = True,
                                        throw_attribute_exception: bool = False) -> Any:
    """
    Find a UI component by the given attribute (label for example) in a dictionary
    It only returns the first match in a depth first search of the json tree
    It returns the dictionary that contains the given attribute with the given value
    or throws an error when none is found.

    Args:
        attribute: an attribute to search ('label' for example)
        value: the value of the attribute ('Submit' for example)
        component_tree: the json response.
        raise_error: If set to False, will return None instead of raising an error. (Default: True)
        throw_attribute_exception: If set to False then if the component is not found an exception is
            thrown using the attribute and value in the exception.

    Returns:
        The json object of the component

    Raises:
        ComponentNotFoundException if the component cannot be found.

    Example:
        >>> find_component_by_attribute_in_dict('label', 'Submit', self.json_response)

        will search the json response to find a component that has 'Submit' as the label

    """
    component = find_component_by_type_and_attribute_and_index_in_dict(component_tree, attribute=attribute, value=value, raise_error=raise_error)
    if raise_error:
        if throw_attribute_exception:
            _validate_component_found_by_attribute(component, attribute, value)
        else:
            _validate_component_found(component, value)  # Does not return if component was not found.
    return component


def find_component_by_label_and_type_dict(attribute: str, value: str, type: str, component_tree: Dict[str, Any],
                                          raise_error: bool = True) -> Any:
    """
    Find a UI component by the given attribute (like label) in a dictionary, and the type of the component as well.
    (`#t` should match the type value passed in)
    It only returns the first match in a depth first search of the json tree.
    It returns the dictionary that contains the given attribute with the given label and type
    or throws an error when none is found if the raise_error value is True. Otherwise it will return None if the
    component cannot be found.

    Args:
        label: label of the component to search
        value: the value of the label
        type: Type of the component (TextField, StartProcessLink etc.)
        component_tree: the json response.
        raise_error: If set to False, will return None instead of raising an error. (Default: True)

    Returns:
        The json object of the component or None if the component cannot be found.

    Raises:
        ComponentNotFoundException if the component cannot be found.

    Example:
        >>> find_component_by_label_and_type_dict('label', 'MyLabel', 'StartProcessLink', self.json_response)

    """
    component = find_component_by_type_and_attribute_and_index_in_dict(component_tree, type=type, attribute=attribute,
                                                                       value=value, raise_error=raise_error)
    if raise_error:
        _validate_component_found(component, value, type=type)  # Method does not return if component is not found.
    return component


def find_component_by_index_in_dict(component_type: str, index: int, component_tree: Dict[str, Any]) -> Any:
    """
    Find a UI component by the index of a given type of component ("RadioButtonField" for example) in a dictionary
    Performs a depth first search and counts quantity of the component, so the 1st is the first one
    It returns the dictionary that contains the given attribute with the requested index
    or throws an error when none is found.

    Args:
        component_type: type of the component(#t in the JSON response, 'RadioButtonField' for example)
        index: the index of the component with the component_type ('1' for example - Indices start from 1)
        component_tree: the json response

    Returns:
        The json object of the component

    Raises:
        ComponentNotFoundException if the component cannot be found.

    Example:
        >>> find_component_by_index_in_dict('RadioButtonField', 1, self.json_response)

        will search the json response to find the first component that has 'RadioButtonField' as the type

    """
    component = find_component_by_type_and_attribute_and_index_in_dict(component_tree, type=component_type, index=index)
    _validate_component_found_by_index(component, index, type=component_type)
    return component


def find_component_by_type_and_attribute_and_index_in_dict(
        component_tree: Dict[str, Any], type: str = '', attribute: str = '', value: str = '', index: int = 1, raise_error: bool = True) -> Any:
    """
    Find a UI component by the given type and/or attribute with 'value' in a dictionary
    Returns the index'th match in a depth first search of the json tree
    Returns the dictionary that contains the given attribute with the given value
    or throws an error when none is found
    Note: Both type and attribute matching are optional, which will cause this
    function to return the index'th component in the tree

    Args:
        component_tree: the json response

    Keyword Args:
        type(str): the component type to match against (default: '')
        attribute(str): an attribute to search (default: '')
        value(str): the value of the attribute (default: '')
        index(int): the index of the component to find if multiple components match the above criteria, 1-indexed (default: 1)
        raise_error(bool): if this is set to false, it will return None instead of raising an error.

    Returns:
        The json object of the component or None if 'raise_error' is set to false.

    Raises:
        ComponentNotFoundException if the attribute or type checks fail.

    Example:
        >>> find_component_by_attribute_and_index_in_dict('label', 'Submit', 1, self.json_response)

        will search the json response to find the first component that has 'Submit' as the label

    """
    if index == 0:
        raise Exception(f"Invalid index: '{index}'. Please enter a positive number. Indexing is 1-based to match SAIL indexing convention")
    if index < 0:
        raise Exception(f"Invalid index: '{index}'. Please enter a positive number")

    type_check_passed_once = False
    attribute_check_passed_once = False
    originial_index = index
    trees_to_search = [component_tree]
    while trees_to_search:
        tree = trees_to_search.pop(0)

        if not isinstance(tree, (dict, list)):
            continue

        if isinstance(tree, list):
            trees_to_search = tree + trees_to_search
            continue

        type_check = not type or tree.get('#t', '') == type
        type_check_passed_once = type_check_passed_once if type_check_passed_once else type_check
        attribute_check = not attribute or tree.get(attribute, '') == value
        attribute_check_passed_once = attribute_check_passed_once if attribute_check_passed_once else attribute_check
        if type_check and attribute_check:
            if index == 1:
                return tree
            index -= 1

        trees_to_search = list(tree.values()) + trees_to_search

    if not raise_error:
        return None
    if not type_check_passed_once:
        raise ComponentNotFoundException(f"No components with type '{type}' found on page")
    if not attribute_check_passed_once:
        raise ComponentNotFoundException(f"No components with {attribute} '{value}' found on page")
    raise Exception(f"Index: '{originial_index}' out of range")


def find_component_by_attribute_and_index_in_dict(attribute: str, value: str, index: int, component_tree: Dict[str, Any]) -> Any:
    """
    Find a UI component by the given attribute (label for example) in a dictionary
    It returns the index'th match in a depth first search of the json tree
    It returns the dictionary that contains the given attribute with the given value
    or throws an error when none is found

    Args:
        attribute: an attribute to search ('label' for example)
        value: the value of the attribute ('Submit' for example)
        index: the index of the component to find if multiple components are found with the same 'value' for 'attribute' (1 for example)
        component_tree: the json response.

    Returns:
        The json object of the component

    Raises:
        ComponentNotFoundException if the component cannot be found.

    Example:
        >>> find_component_by_attribute_and_index_in_dict('label', 'Submit', 1, self.json_response)

        will search the json response to find the first component that has 'Submit' as the label

    """
    component = find_component_by_type_and_attribute_and_index_in_dict(component_tree, attribute=attribute, value=value, index=index)
    _validate_component_found(component, value)  # Does not return if the component is not found
    return component


def repeat(num_times: int = 2, wait_time: float = 0.0) -> Callable:
    """
    This function allows an arbitrary function to be executed an arbitrary number of times
    The intended use is as a decorator:

    >>> @repeat(2)
    ... def arbitrary_function():
    ...     print("Hello World")
    ... arbitrary_function()
    Hello World
    Hello World

    Args:
        num_times (int): an integer

    Implicit Args:
        arbitrary_function (Callable): a python function

    Returns:
        A reference to a function which performs the decorated function num_times times

    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper_decorator(*args: Any, **kwargs: Any) -> Any:
            for _ in range(num_times):
                value = func(*args, **kwargs)
                gevent.sleep(wait_time)
            return value
        return wrapper_decorator
    return decorator


def get_username(auth: list) -> str:
    if auth and len(auth) >= 1 and auth[0]:
        return auth[0]
    else:
        return ""
