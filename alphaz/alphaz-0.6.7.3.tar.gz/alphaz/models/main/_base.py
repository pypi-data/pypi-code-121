import enum, inspect, operator, re
from dataclasses import dataclass, field, is_dataclass, _MISSING_TYPE
from collections import OrderedDict

from typing import Dict, List
from typing_extensions import Annotated

from ..logger import AlphaLogger
from ...libs import py_lib, json_lib, string_lib

from ._exception import AlphaException
class AlphaEnum(enum.Enum):
    def __str__(self):
        return str(self.value)

    def to_json(self):
        return str(self.value)


class AlphaMappingAttribute:
    def __init__(
        self,
        name: str,
        key: str = None,
        fct: object = None,
        required: bool = False,
        flat: bool = False,
    ):
        self.name = name
        self.key = key or name
        self.fct = fct
        self.required = required
        self.flat = flat


def get_score_dict_best_match(score_dict: Dict[str, int]) -> str:
    max_keys = [
        x
        for x, y in score_dict.items()
        if y == max(score_dict.items(), key=lambda k: k[1])[1]
    ]
    min_size = min(max_keys, key=len)
    best_matchs = [x for x in max_keys if len(x) == len(min_size)]
    if len(best_matchs) > 1:
        print(f"ERROR: multiple match {best_matchs}")
    return best_matchs[0]


class AlphaClass:
    def __init__(self, *args, log: AlphaLogger = None, **kwargs):
        self.init_args: dict = {"args": args, "kwargs": kwargs}
        self.children: list = []

        self.log: AlphaLogger = log

        self.__piles: Dict[str, List[str]] = {}

    def make_child(self, child_cls, *args, **kwargs):
        if args is None:
            args = self.init_args["args"]
        if kwargs is None:
            kwargs = self.init_args["kwargs"]
        child = child_cls(self, *args, **kwargs)
        self.children.append(child)
        return child

    def get_attributes(self):
        return py_lib.get_attributes(self)

    def to_json(self):
        rejected = ["_AlphaClass__piles", "init_args", "children", "log"]
        dict_output = {
            x: y if not hasattr(y, "to_json") or inspect.isclass(y) else y.to_json()
            for x, y in self.get_attributes().items()
            if not x in rejected
        }
        return dict_output

    def __log(self, stack, message, ex=None, out: bool = False):
        if not stack in self.__piles:
            self.__piles[stack] = []
        pile = self.__piles[stack]

        if self.log is not None:
            method = getattr(self.log, stack)
            if len(pile) != 0:
                for deb in pile:
                    method(deb, ex=ex)
                stack = []
            method(message, ex=ex)
        else:
            pile.append(message)
            if out:
                for stack, msg in self.__piles.items():
                    print(f"{stack}: {msg}")
                if ex:
                    print(ex)

    def debug(self, message, ex=None):
        self.__log(inspect.stack()[0][3], message=message, ex=ex)

    def info(self, message, ex=None):
        self.__log(inspect.stack()[0][3], message=message, ex=ex)

    def warning(self, message, ex=None):
        self.__log(inspect.stack()[0][3], message=message, ex=ex)

    def error(self, message, out=False, ex=None):
        self.__log(inspect.stack()[0][3], message=message, ex=ex, out=out)
        if out:
            exit()

    def critical(self, message, out=False, ex=None):
        self.__log(inspect.stack()[0][3], message=message, ex=ex, out=out)
        if out:
            exit()

    def map_from_inputs(
        self, map_entries: List[AlphaMappingAttribute], inputs: Dict[str, object]
    ):
        mapped = []
        for key in inputs:
            for mapping_attribute in map_entries:
                if mapping_attribute.name in mapped:
                    continue

                if key.endswith(mapping_attribute.key):
                    value = inputs[key]
                    if mapping_attribute.fct is not None and value is not None:
                        value = mapping_attribute.fct(value)

                    setattr(self, mapping_attribute.name, value)
                    mapped.append(mapping_attribute.name)


DATACLASS_AUTO_MAP_MATCHS = {}


def convert_value(value: object, type_):
    if value is None:
        return None
    if type_ != bool:
        try:
            value = type_(value)
        except:
            pass
        if str(value).lower() in ["none", "null", "undefined"]:
            value = None
        return None if value is None else value
    else:
        str_val = str(value).upper()
        return (
            False
            if value is None
            else ("Y" in str_val or "T" in str_val or "1" in str_val)
        )


def identify(search_key: str, dict_keys: List[str], dataclass_type):
    identified_k = None
    for dict_key in dict_keys:
        if search_key in dict_key or dict_key in search_key:
            identified_k = dict_key
            dict_keys.remove(identified_k)
            break
    score = 100
    if identified_k is None:
        identified_k, score = string_lib.found_best_match(
            search_key, dict_keys, threshold=50
        )

        if identified_k is None:
            # print(f"{dataclass_type}: Cannot find a match for {search_key}")
            return None, score
    return identified_k, score


def get_association(key: str, associations: Dict[str, str] = {}):
    associations = {
        x: y if type(associations[x]) != AlphaMappingAttribute else y.key
        for x, y in associations.items()
    }
    ass_matchs = [x for x, y in associations.items() if y == key]

    if len(ass_matchs) != 0:
        return ass_matchs[0]
    return None


def full_identify(
    dataclass_type,
    dict_key: str,
    fields_keys: List[str],
    associations: Dict[str, str] = {},
    no_match: List[str] = [],
):
    patterns = {}
    required = False

    for x in fields_keys:
        if x in no_match:
            continue
        if x in associations:
            if type(associations[x]) == AlphaMappingAttribute:
                required = associations[x].required
                patterns[x] = associations[x].key
            else:
                patterns[x] = associations[x]
        else:
            patterns[x] = x

    patterns = OrderedDict(sorted(patterns.items(), key=lambda x: x[1], reverse=True))
    for field_name, k in patterns.items():
        if dict_key == field_name:
            return field_name, 100

    for field_name, k in patterns.items():
        matchs = re.findall(k, dict_key)
        if len(matchs) != 0:
            return field_name, 100

    identified_v, score = identify(dict_key, list(patterns.values()), dataclass_type)
    # print(f"    Idenfitied {dict_key} to {identified_v} with score {score}")

    if identified_v is None:
        if required:
            return None, 0
        return None, 0  # "CONTINUE"

    ass_matchs = [x for x, y in associations.items() if y == identified_v]
    if identified_v in associations.values() and dict_key not in ass_matchs:
        return None, 0

    set_1 = set(identified_v.split("_"))
    set_2 = set(dict_key.split("_"))
    is_common_part = len(list(set_1 & set_2)) != 0

    if not is_common_part:
        # print(f"{dataclass_type}: Weird match for {dict_key} with {identified_k}")
        return None, 0

    identified_k = [x for x, y in patterns.items() if y == identified_v][0]

    if identified_k in patterns:
        matchs = re.findall(patterns[identified_k], dict_key)
        if len(matchs) == 0:
            return None, 0

    return identified_k, score


@dataclass
class AutoMapping(AlphaClass):
    dataclass_type: object
    associations: Dict[str, str] = field(default_factory=lambda: {})
    no_match: List[str] = field(default_factory=lambda: [])

    object_fields: Dict[str, object] = field(default_factory=lambda: {})
    dict_fields: Dict[str, object] = field(default_factory=lambda: {})
    list_fields: Dict[str, object] = field(default_factory=lambda: {})
    flat_fields: Dict[str, object] = field(default_factory=lambda: {})

    identified_object_fields: Dict[str, object] = field(default_factory=lambda: {})
    identified_dict_fields: Dict[str, object] = field(default_factory=lambda: {})
    identified_list_fields: Dict[str, object] = field(default_factory=lambda: {})

    matchs_object_fields: Dict[str, object] = field(default_factory=lambda: {})
    matchs_dict_fields: Dict[str, object] = field(default_factory=lambda: {})
    matchs_list_fields: Dict[str, object] = field(default_factory=lambda: {})

    already_assigned: List[str] = field(default_factory=lambda: [])

    is_identified: bool = False
    flat: bool = False

    def __post_init__(self):
        self.__set_fields_types()

    def __set_fields_types(self):
        for x, y in self.dataclass_type.__dataclass_fields__.items():
            if py_lib.is_subtype(y.type, List) or py_lib.is_subtype(y.type, list):
                self.list_fields[x] = y
            elif is_dataclass(y.type):
                self.dict_fields[x] = y
            else:
                self.object_fields[x] = y

    def identify(self, dict_values: Dict[str, object]):
        dict_elements = {
            x: y for x, y in dict_values.items() if type(y) == dict or y is None
        }
        list_elements = {
            x: y for x, y in dict_values.items() if type(y) == list or y is None
        }
        other_elements = {
            x: y for x, y in dict_values.items() if type(y) != list or type(y) != dict
        }

        fields_groups = [
            (
                list_elements,
                self.list_fields,
                self.identified_list_fields,
                self.matchs_list_fields,
            ),
            (
                dict_elements,
                self.dict_fields,
                self.identified_dict_fields,
                self.matchs_dict_fields,
            ),
            (
                other_elements,
                self.object_fields,
                self.identified_object_fields,
                self.matchs_object_fields,
            ),
        ]

        identified = []
        for sub_dict_values, fields_dict, identified_dict, matchs in fields_groups:
            for dict_key in sub_dict_values.keys():
                identified_k = get_association(dict_key, self.associations)
                if identified_k is not None:
                    if not identified_k in matchs:
                        matchs[identified_k] = {}
                    matchs[identified_k][dict_key] = 100
                    identified.append(dict_key)

            for dict_key in sub_dict_values.keys():
                if dict_key in identified:
                    continue
                identified_k, score = full_identify(
                    self.dataclass_type,
                    dict_key,
                    list(fields_dict.keys()),
                    self.associations,
                    self.no_match,
                )
                if identified_k is None:
                    continue
                if not identified_k in matchs:
                    matchs[identified_k] = {}
                matchs[identified_k][dict_key] = score

            for field_key, score_dict in matchs.items():
                best_match = get_score_dict_best_match(score_dict)
                if field_key in fields_dict:
                    identified_dict[best_match] = fields_dict[field_key]
                    identified.append(best_match)

    def __identify_flat(self, dict_values: Dict[str, object]):
        identified = []
        for dict_key in dict_values.keys():
            identified_k = get_association(dict_key, self.associations)
            if identified_k is not None:
                if not identified_k in self.matchs_object_fields:
                    self.matchs_object_fields[identified_k] = {}
                self.matchs_object_fields[identified_k][dict_key] = 100
                identified.append(dict_key)

        for dict_key in dict_values.keys():
            if dict_key in identified:
                continue
            identified_k, score = full_identify(
                self.dataclass_type,
                dict_key,
                list(self.object_fields.keys()),
                self.associations,
                self.no_match,
            )
            if identified_k is None:
                continue

            if not identified_k in self.matchs_object_fields:
                self.matchs_object_fields[identified_k] = {}
            self.matchs_object_fields[identified_k][dict_key] = score

        for field_key, score_dict in self.matchs_object_fields.items():
            best_match = get_score_dict_best_match(score_dict)
            self.identified_object_fields[best_match] = self.object_fields[field_key]

    def __map_flat(self, dict_values: Dict[str, object]):
        if not self.is_identified:
            self.__identify_flat(dict_values)

        field_values = {}
        for (
            key,
            fd,
        ) in self.identified_object_fields.items():
            field_values[fd.name] = convert_value(dict_values[key], fd.type)

        for fd in self.dict_fields.values():
            field_values[fd.name] = fd.type.auto_map_from_dict(
                dict_values={
                    x: y for x, y in dict_values.items() if not x in field_values
                }
            )

        return field_values

    def map(self, dict_values: Dict[str, object]):
        if self.flat:
            return self.__map_flat(dict_values)

        if not self.is_identified:
            self.identify(dict_values)

        field_values = {}
        for (
            key,
            fd,
        ) in self.identified_object_fields.items():
            field_values[fd.name] = convert_value(dict_values[key], fd.type)

        for (
            key,
            fd,
        ) in self.identified_dict_fields.items():
            field_values[fd.name] = (
                fd.type.auto_map_from_dict(dict_values=dict_values[key])
                if dict_values[key] is not None
                else None
            )

        for (
            key,
            fd,
        ) in self.identified_list_fields.items():
            sub_type = fd.type.__args__[0]
            if hasattr(sub_type, "auto_map_from_dict"):
                field_values[fd.name] = (
                    [
                        (
                            sub_type.auto_map_from_dict(dict_values=f)
                            if f is not None
                            else None
                        )
                        for f in dict_values[key]
                    ]
                    if dict_values[key] is not None
                    else []
                )
            else:
                field_values[fd.name] = (
                    [(sub_type(f) if f is not None else None) for f in dict_values[key]]
                    if dict_values[key] is not None
                    else []
                )
        return field_values

def convert_value_from_field(field_type, value, automap:bool=False):
    if value is None:
        return None
    if is_dataclass(field_type):
        return field_type.map_from_dict(value, automap=automap)
    else:
        try:
            return field_type(value)
        except:
            return value
        
class AlphaDataclass(AlphaClass):
    def compare(self, other, attrs_list: List[str], attrs_eq: Dict[str, str] = None) -> bool:
        if not isinstance(other, self.__class__):
            raise AlphaException(f"Cannot compare {self.__class__} object with {other.__class__} object")
        
        [attrs_list.append(attr) for attr in (attrs_eq if attrs_eq is not None else [])]
        
        compared = []
        for attr in attrs_list:
            if hasattr(self, attr):                
                self_attr, other_attr = getattr(self, attr), getattr(other, attr)
                
                custom_eq = attrs_eq[attr] if attrs_eq is not None and attr in attrs_eq else None
                
                if (self_attr is None and other_attr is not None) or (other_attr is None and self_attr is not None):
                    compared.append(False)
                elif self_attr is None and other_attr is None:
                    compared.append(True)
                elif custom_eq is not None:
                    compared.append(getattr(self_attr,custom_eq)(other_attr))
                else:
                    compared.append(getattr(self_attr,"__eq__")(other_attr))
            else:
                raise AlphaException(f"{self.__class__} object has no attribute {attr}")

        return all(compared)

    def update_from_auto_map_from_dict(
        self,
        dict_values: Dict[str, object],
        associations: Dict[str, str] = {},
        no_match: List[str] = [],
        flat: bool = False,
    ):
        instance = self.auto_map_from_dict(
            dict_values, associations, no_match, flat=flat
        )

        for key, fd in instance.__dict__.items():
            if fd is not None:
                setattr(self, key, fd)

    @classmethod
    def auto_map_from_dict(
        dataclass_type,
        dict_values: Dict[str, object],
        associations: Dict[str, str] = {},
        no_match: List[str] = [],
        flat: bool = False,
    ):
        global DATACLASS_AUTO_MAP_MATCHS
        if dict_values is None:
            return dataclass_type()

        dataclass_name = str(dataclass_type).split(".")[-1].replace("'>", "")
        uuid = f"{dataclass_name}({','.join(list(dict_values.keys()))})"

        # FIELDS
        if not uuid in DATACLASS_AUTO_MAP_MATCHS:
            DATACLASS_AUTO_MAP_MATCHS[uuid] = AutoMapping(
                dataclass_type, associations=associations, no_match=no_match, flat=flat
            )

        fields_values = DATACLASS_AUTO_MAP_MATCHS[uuid].map(dict_values)

        instance = None
        required_fields = [
            x
            for x, y in dataclass_type.__dataclass_fields__.items()
            if type(y.default) == _MISSING_TYPE
            and type(y.default_factory) == _MISSING_TYPE
        ]
        is_required_fields = set(required_fields).intersection(
            fields_values.keys()
        ) == set(required_fields)
        if not is_required_fields:
            return None
        try:
            instance = dataclass_type(**fields_values)
        except Exception as ex:
            print(f"Error mapping {dataclass_type}")
            raise ex
        return instance

    @classmethod
    def map_from_json(dataclass_type, json_values: str, automap: bool = False):
        dict_value = json_lib.load_json(json_values)
        return dataclass_type.map_from_dict(dict_value, automap=automap)

    @classmethod
    def map_from_dict(
        dataclass_type, dict_value: Dict[str, object], automap: bool = False
    ):
        if automap and hasattr(dataclass_type, "auto_map_from_dict"):
            return dataclass_type.auto_map_from_dict(dict_values=dict_value)
        
        if not py_lib.is_subtype(type(dict_value), Dict) and not py_lib.is_subtype(type(dict_value), dict) and not type(dict_value) == dict:
            return None
        if dict_value is None:
            return None
        
        field_values = {}
        for key, value in dict_value.items():
            if key in dataclass_type.__dataclass_fields__:
                field = dataclass_type.__dataclass_fields__[key]
                field_type = field.type
                
                if py_lib.is_subtype(field_type, List) or py_lib.is_subtype(field_type, list):
                    if value is not None:
                        field_values[key] = [convert_value_from_field(py_lib.get_subtype(field_type), v, automap=automap) for v in value]
                    else:
                        field_values[key] = []
                else:
                    field_values[key] = convert_value_from_field(field_type, value, automap=automap)
        return dataclass_type(**field_values)
