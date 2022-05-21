import inspect
from pydoc import locate
from types import CodeType, FunctionType

from serializers_v.src.constants import *


def get_type(item):
    item_type = str(type(item))

    return item_type[8:len(item_type) - 2]


def serialize(item):
    if isinstance(item, (int, float, complex, bool, str, type(None))):
        return serialize_ifcbsn(item)
    if isinstance(item, (list, tuple, set, bytes)):
        return serialize_ltsb(item)
    if isinstance(item, dict):
        return serialize_dict(item)
    if inspect.isfunction(item):
        return serialize_function(item)
    if inspect.isclass(item):
        return serialize_class(item)
    if inspect.iscode(item):
        return serialize_code(item)
    if inspect.ismodule(item):
        return serialize_module(item)
    if inspect.ismethoddescriptor(item) or inspect.isbuiltin(item):
        return serialize_instance(item)
    if inspect.isgetsetdescriptor(item) or inspect.ismemberdescriptor(item):
        return serialize_instance(item)
    if isinstance(item, type(type.__dict__)):
        return serialize_instance(item)

    return serialize_object(item)


def serialize_ifcbsn(item):
    result = {TYPE: get_type(item), VALUE: item}

    return result


def serialize_ltsb(item):
    result = {TYPE: get_type(item), VALUE: [serialize(obj) for obj in item]}

    return result


def serialize_dict(item):
    result = {TYPE: get_type(item), VALUE: [[serialize(key), serialize(item[key])] for key in item]}

    return result


def serialize_object(item):
    result = {TYPE: OBJECT, VALUE: serialize({OBJECT_TYPE: type(item), FIELDS: item.__dict__})}

    return result


def serialize_function(item):
    members = inspect.getmembers(item)
    result = {TYPE: get_type(item)}
    value = {}
    for obj in members:
        if obj[0] in FUNC_ATTRIBUTES:
            value[obj[0]] = (obj[1])
        if obj[0] == CODE:
            co_names = obj[1].__getattribute__(CO_NAMES)
            globs = item.__getattribute__(GLOBALS)
            value[GLOBALS] = {}
            for obj2 in co_names:
                if obj2 == item.__name__:
                    value[GLOBALS][obj2] = item.__name__
                elif obj2 in globs and not inspect.ismodule(obj2) and obj2 not in __builtins__:
                    value[GLOBALS][obj2] = globs[obj2]
    result[VALUE] = serialize(value)

    return result


def serialize_instance(item):
    members = inspect.getmembers(item)
    result = {TYPE: get_type(item), VALUE: serialize({obj[0]: obj[1] for obj in members if not callable(obj[1])})}

    return result


def serialize_code(item):
    if get_type(item) is None:
        return None

    members = inspect.getmembers(item)
    result = {TYPE: get_type(item), VALUE: serialize({obj[0]: obj[1] for obj in members if not callable(obj[1])})}

    return result


def serialize_module(item):
    temp_item = str(item)
    result = {TYPE: get_type(item), VALUE: temp_item[9:len(temp_item) - 13]}

    return result


def serialize_class(item):
    result = {TYPE: CLASS}
    value = {NAME: item.__name__}
    members = inspect.getmembers(item)
    for obj in members:
        if not (obj[0] in NOT_CLASS_ATTRIBUTES):
            value[obj[0]] = obj[1]
    result[VALUE] = serialize(value)

    return result


def deserialize(item):
    if item[TYPE] in [FLOAT, INT, COMPLEX, NONE_TYPE, BOOL, STRING]:
        return deserialize_ifcbsn(item)
    if item[TYPE] in [LIST, TUPLE, SET, BYTES]:
        return deserialize_ltsb(item)
    if item[TYPE] == DICT:
        return deserialize_dict(item)
    if item[TYPE] == OBJECT:
        return deserialize_object(item)
    if item[TYPE] == MODULE:
        return deserialize_module(item)
    if item[TYPE] == CLASS:
        return deserialize_class(item)
    if item[TYPE] == FUNCTION:
        return deserialize_function(item)


def deserialize_ifcbsn(item):  # done
    if item[TYPE] == NONE_TYPE:
        return None

    if item[TYPE] == BOOL and isinstance(item[VALUE], str):
        return item[VALUE] == TRUE

    return locate(item[TYPE])(item[VALUE])


def deserialize_ltsb(item):  # done
    if item[TYPE] == LIST:
        return list(deserialize(obj) for obj in item[VALUE])

    if item[TYPE] == TUPLE:
        return tuple(deserialize(obj) for obj in item[VALUE])

    if item[TYPE] == SET:
        return set(deserialize(obj) for obj in item[VALUE])

    if item[TYPE] == BYTES:
        return bytes(deserialize(obj) for obj in item[VALUE])


def deserialize_dict(item):  # done
    return {deserialize(obj[0]): deserialize(obj[1]) for obj in item[VALUE]}


def deserialize_object(item): # done
    value = deserialize(item[VALUE])
    result = value[OBJECT_TYPE](**value[FIELDS])

    for key, value in value[FIELDS].items():
        result.key = value

    return result


def deserialize_module(item):  # done
    return __import__(item[VALUE])


def deserialize_class(item): # done
    class_dict = deserialize(item[VALUE])
    name = class_dict[NAME]
    del class_dict[NAME]

    return type(name, (object,), class_dict)


def deserialize_code(item):  # done
    objs = item[VALUE][VALUE]

    for obj in objs:
        if obj[0][VALUE] == CODE:
            args = deserialize(obj[1][VALUE])
            code_dict = {}
            for arg in args:
                arg_val = args[arg]
                if arg != DOC:
                    code_dict[arg] = arg_val

            code_list = [0] * 16
            for name in code_dict:
                code_list[CODE_ARGS.index(name)] = code_dict[name]
            return CodeType(*code_list)


def deserialize_function(item):  # done
    result_dict = deserialize(item[VALUE])
    result_dict["code"] = deserialize_code(item)
    result_dict.pop(CODE)
    result_dict[GLOBALS][BUILTINS] = __builtins__
    result_dict["globals"] = result_dict[GLOBALS]
    result_dict.pop(GLOBALS)
    result_dict["name"] = result_dict[NAME]
    result_dict.pop(NAME)
    result_dict["argdefs"] = result_dict[DEFAULTS]
    result_dict.pop(DEFAULTS)

    result = FunctionType(**result_dict)
    if result.__name__ in result.__getattribute__(GLOBALS):
        result.__getattribute__(GLOBALS)[result.__name__] = result

    return result