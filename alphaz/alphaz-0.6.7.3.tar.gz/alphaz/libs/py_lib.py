import sys, imp, inspect, os, glob, copy

from ..models.watcher import ModuleWatcher
from typing import List, Dict, OrderedDict

myself = lambda: inspect.stack()[1][3]


def get_modules_infos(name: str = None, url: str = None):
    from importlib_metadata import version
    import pkgutil

    data = {}
    for item in pkgutil.iter_modules():
        if name is not None and name.lower() != item.name.lower():
            continue
        try:
            data[item.name] = version(item.name)
        except:
            continue

    if url:
        from . import api_lib

        params = {}
        if name:
            params["name"] = name
        answer = api_lib.get_api_answer(f"{url}/modules", params)
        data_url = answer.data

        K = [
            "local",
            "local_up",
            "local_down",
            "distant",
            "distant_up",
            "distant_down",
            "up",
            "down",
            "distant_align",
        ]
        updates, out = {x: [] for x in K}, {}
        keys = list(set(list(data_url.keys()) + list(data.keys())))
        for key in keys:
            if key in data_url and key in data and data_url[key] == data[key]:
                continue

            out[key] = [
                data[key] if key in data else None,
                data_url[key] if key in data_url else None,
            ]

            if key in data:
                updates["distant"].append(f"{key}=={data[key]}")
            if key in data and key in data_url:
                updates["distant_align"].append(f"{key}=={data[key]}")

            if key in data_url:
                updates["local"].append(f"{key}=={data_url[key]}")
            if key in data and key in data_url:
                updates["up"].append(
                    f"{key}=={data[key] if data[key] > data_url[key] else data_url[key]}"
                )
            if key in data and key in data_url:
                updates["down"].append(
                    f"{key}=={data[key] if data[key] < data_url[key] else data_url[key]}"
                )

            if key in data and key in data_url and data[key] < data_url[key]:
                updates["local_up"].append(f"{key}=={data_url[key]}")
                updates["distant_down"].append(f"{key}=={data[key]}")
            if key in data and key in data_url and data[key] > data_url[key]:
                updates["local_down"].append(f"{key}=={data_url[key]}")
                updates["distant_up"].append(f"{key}=={data[key]}")

        for key, items in updates.items():
            out[key] = " ".join(items)
        return out
    return data


def myself(fct=None):
    name = inspect.stack()[1][3]
    if fct:
        name = fct(name)
    return name


def get_project_name_from_stack(stack: inspect.FrameInfo):
    calling_module = inspect.getmodule(stack[0])
    module_path = calling_module.__name__.replace(".", os.sep) + ".py"
    root = calling_module.__file__.replace(module_path, "").split(os.sep)
    project_name = "Unknow"
    for name in root[::-1]:
        if name.strip() != "" and name.strip() != "backend":
            project_name = name
            break
    return project_name


def reload_modules(root, log=None):
    root = root.replace("\\", "\\\\")

    modules = [x for x in sys.modules.values()]

    for module in modules:
        if root in str(module) and not "core" in str(module).lower():
            if log:
                log.debug("   Reload %s" % module)
            try:
                imp.reload(module)
            except:
                pass


def watch_modules(roots: list = [], log=None):
    mw = ModuleWatcher()
    roots = [root.replace("\\", "\\\\") for root in roots]

    modules = [x for x in sys.modules.values()]
    for module in modules:
        for root in roots:
            if root in str(module) and not "core" in str(module).lower():
                if log:
                    log.debug(f"Add <{module}> to the watcher")
                mw.watch_module(str(module))
    mw.start_watching()


def execute_cmd(cmd="", root=None, log=None):
    current_folder = os.getcwd()
    if root is not None:
        os.chdir(root)
    if log:
        log.info("Execute: <%s>" % cmd)
    os.system(cmd)
    os.chdir(current_folder)


def get_directory_log_files(directory):
    return glob.glob(directory + os.sep + "*.log*")


def try_except(success, failure, *exceptions):
    try:
        return success()
    except exceptions or Exception:
        return failure() if callable(failure) else failure


def getsize(obj):
    """sum size of object & members."""
    if isinstance(obj, BLACKLIST):
        raise TypeError("getsize() does not take argument of type: " + str(type(obj)))
    seen_ids = set()
    size = 0
    objects = [obj]
    while objects:
        need_referents = []
        for obj in objects:
            if not isinstance(obj, BLACKLIST) and id(obj) not in seen_ids:
                seen_ids.add(id(obj))
                size += sys.getsizeof(obj)
                need_referents.append(obj)
        objects = get_referents(*need_referents)
    return size


def get_attributes(obj):
    attributes = inspect.getmembers(obj, lambda a: not (inspect.isroutine(a)))
    return {
        a[0]: a[1]
        for a in attributes
        if not (a[0].startswith("__") and a[0].endswith("__"))
    }


def filter_kwargs(fct, args: list = [], kwargs: dict = {}) -> dict:
    """Remove kwargs that are not in function kwargs

    Args:
        fct ([type]): [description]
        args (List): [description]
        kwargs (Dict): [description]

    Returns:
        [type]: [description]
    """
    fargs = inspect.getfullargspec(fct)
    kwargs = {x: y for x, y in kwargs.items() if x in fargs.args}
    return kwargs

def get_subtype(parent_type):
    if hasattr(parent_type, "__args__"):
        if isinstance(parent_type.__args__[0], type):
            return parent_type.__args__[0]
    return None

def is_subtype(sub_type, parent_type):
    # TODO: fix
    """if not isinstance(sub_type,type):
        sub_type = type(sub_type)
    if not isinstance(parent_type,type):
        parent_type = type(parent_type)"""
    if sys.version_info >= (3, 7):
        if not hasattr(sub_type, "__origin__") or not hasattr(
            parent_type, "__origin__"
        ):
            return False

        if sub_type.__origin__ != parent_type.__origin__:
            return False

        if hasattr(parent_type, "__args__") and hasattr(sub_type, "__args__"):
            if isinstance(parent_type.__args__[0], type):
                return sub_type.__args__ == parent_type.__args__
        else:
            return sub_type._name == parent_type._name

        return True

    else:
        if not hasattr(sub_type, "__extra__") or not hasattr(parent_type, "__extra__"):
            return False

        if sub_type.__extra__ != parent_type.__extra__:
            return False

        if not parent_type.__args__ or parent_type.__args__ == sub_type.__args__:
            return True

    return False


def sort_by_key(input_dict):
    return OrderedDict(sorted(input_dict.items(), key=lambda x: x[0]))


def compare_dicts(dict_obj_1, dict_obj_2, sub_elements: dict = None):
    if not sub_elements:
        sub_elements = {}

    level_dict = {}

    if dict_obj_1 is None or dict_obj_2 is None:
        list_keys = list(dict_obj_1.keys() if dict_obj_2 is None else dict_obj_2.keys())
    else:
        list_keys = list(set(dict_obj_1.keys()).union(set(dict_obj_2.keys())))
    list_keys.sort()

    diffs = []

    for key in list_keys:
        value_1, value_2 = (
            dict_obj_1[key] if key in dict_obj_1 else None
        ) if dict_obj_1 is not None else None, (
            dict_obj_2[key] if key in dict_obj_2 else None
        ) if dict_obj_2 is not None else None
        ref_element = value_1 if value_1 is not None else value_2

        if key in sub_elements and value_1 is None and value_2 is None:
            level_dict[key] = None

        elif type(ref_element) == dict:
            level_dict[key] = compare_dicts(
                value_1,
                value_2,
                {} if not key in sub_elements else sub_elements[key]["sub_elements"],
            )
            diff = level_dict[key]["diff"]
            diffs.append(diff)
        elif type(ref_element) == list and key in sub_elements:
            sub_elements_1 = (
                {x[sub_elements[key]["key"]]: x for x in value_1}
                if value_1 is not None
                else None
            )
            sub_elements_2 = (
                {x[sub_elements[key]["key"]]: x for x in value_2}
                if value_2 is not None
                else None
            )
            sub_elements_1 = sub_elements_1 or {x: None for x in sub_elements_2.keys()}
            sub_elements_2 = sub_elements_2 or {x: None for x in sub_elements_1.keys()}
            list_keys = list(
                set(sub_elements_1.keys()).union(set(sub_elements_2.keys()))
            )

            dict_list = {}
            for list_key in list_keys:
                dict_list[list_key] = compare_dicts(
                    sub_elements_1[list_key] if list_key in sub_elements_1 else None,
                    sub_elements_2[list_key] if list_key in sub_elements_2 else None,
                    sub_elements[key]["sub_elements"],
                )

            if "key_type" in sub_elements[key]:
                dict_list = {
                    sub_elements[key]["key_type"](x): y for x, y in dict_list.items()
                }

            level_dict[key] = list(dict(sorted(dict_list.items())).values())
            diff = any(x["diff"] for x in dict_list.values())
            diffs.append(diff)
        else:
            diff = (value_1 is None or value_2 is None) or (
                value_1 != value_2 or key not in dict_obj_1 or key not in dict_obj_2
            )
            level_dict[key] = {"values": [value_1, value_2], "diff": diff}
            diffs.append(diff)

    level_dict = dict(sorted(level_dict.items()))

    level_dict["diff"] = any(diffs)
    return level_dict

def get_sub_lists(a_list:list, lenght:int):
    a_list = list(a_list)
    return [a_list[i:i+lenght] for i in range(0, len(a_list), lenght)]