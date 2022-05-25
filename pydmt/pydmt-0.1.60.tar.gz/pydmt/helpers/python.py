import os
import os.path
import importlib
from typing import Callable, List, Dict


def make_console_script(package_name: str, main: Callable):
    """
    return a string suitable to be used as the section 'console_scripts'
    of the 'entry_points' parameters of setup.py.

    example: 'pycmdtools=pycmdtools.endpoints.main:main'
    :param package_name:
    :param main:
    :return:
    """
    return f"{package_name}={getattr(main, '__module__')}:{main.__name__,}"


def array_indented(level: int, array: List[str], quote_char='\'', comma_after=False) -> str:
    """
    return an array indented according to indent level
    :param level:
    :param array:
    :param quote_char:
    :param comma_after:
    :return:
    """
    out = "[\n"
    for x in array:
        out += (((level + 1) * 4) * " ") + '{qc}{x}{qc}'.format(qc=quote_char, x=x) + ",\n"
    out += ((level * 4) * " ") + "]"
    if comma_after:
        out += ","
    return out


def dict_indented(level: int, dictionary: Dict[str, List[int]], quote_char='\'', comma_after=False) -> str:
    """
    return an dict indented according to indent level
    :param level:
    :param dictionary:
    :param quote_char:
    :param comma_after:
    :return:
    """
    out = "{\n"
    for k, v in dictionary.items():
        spaces = (((level + 1) * 4) * " ")
        out += '{spaces}{qc}{k}{qc}: {v},\n'.format(
            spaces=spaces,
            qc=quote_char,
            k=k,
            v=v,
        )
    spaces = ((level * 4) * " ")
    out += f"{spaces}}}"
    if comma_after:
        out += ","
    return out


def find_packages(path: str) -> List[str]:
    """
    A better version of find_packages than what setuptools offers
    This function needs to be deterministic.
    :param path:
    :return:
    """
    ret = []
    for root, _dir, files in os.walk(path):
        if '__init__.py' in files:
            ret.append(root.replace("/", "."))
    return sorted(ret)


def get_list_unquoted(a_list: List[str]) -> str:
    """
    The exact format of this output is to be used in python code from templates,
    that is why the left bracket ([) does not have space following it and the
    same for the right bracker (]).
    """
    s = "["
    s += ", ".join(a_list)
    s += "]"
    return s


def get_list_quoted(a_list: List[str]) -> str:
    """
    The exact format of this output is to be used in python code from templates,
    that is why the left bracket ([) does not have space following it and the
    same for the right bracker (]).
    """
    quoted = map(lambda x: f"\"{x}\"", a_list)
    s = "["
    s += ", ".join(quoted)
    s += "]"
    return s


def get_package_name():
    mod = importlib.import_module("config.python")
    if hasattr(mod, "package_name"):
        return getattr(mod, "package_name")
    return os.path.basename(os.getcwd())


def get_attr(attr: str):
    mod = importlib.import_module("config.python")
    if hasattr(mod, attr):
        return getattr(mod, attr)
    mod = importlib.import_module("default.python")
    if hasattr(mod, attr):
        return getattr(mod, attr)
    # FIXME - need a better exception type (make my own)
    raise ValueError(f"cannot find {attr}")


def get_license_type():
    return get_attr("license_type")


def get_platforms():
    return get_attr("platforms")


def get_classifiers():
    return get_attr("classifiers")
