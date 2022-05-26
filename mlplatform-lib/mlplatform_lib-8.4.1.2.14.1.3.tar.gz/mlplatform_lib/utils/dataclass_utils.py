from typing import Dict, List
import inspect
import inflection
from dataclasses import is_dataclass


# dataclass field(init=False)로 지정되어 있는 변수들은
# constructor에 넣어서 생성 할 수 없다.
# 따라서, 생성자에 넘겨줄 dictionary와 setattr로 설정할 변수를 나누어 설정한다.
def from_dict(dataclass, dict: Dict):
    sig = inspect.signature(dataclass.__init__)

    init_dict = {}
    init_false_dict = {}
    for key, val in dict.items():
        # camel case to snake case
        key = inflection.underscore(key)

        if key in sig.parameters.keys():
            key_class = sig.parameters[key].annotation
            if is_dataclass(key_class):
                init_dict[key] = from_dict(sig.parameters[key].annotation, val)
            # regard as typing hint
            elif hasattr(key_class, "__origin__") and (
                key_class.__origin__ == list or key_class.__origin__ == List
            ):
                if is_dataclass(sig.parameters[key].annotation.__args__[0]):
                    init_dict[key] = [
                        from_dict(sig.parameters[key].annotation.__args__[0], elem) for elem in val
                    ]
                else:
                    init_dict[key] = val

            else:
                init_dict[key] = val
        else:
            init_false_dict[key] = val

    instance = dataclass(**init_dict)
    for key, val in init_false_dict.items():
        setattr(instance, key, val)
    return instance


def to_dict(instance):
    result = {}
    for k, v in instance.__dict__.items():
        if is_dataclass(v):
            result[inflection.camelize(k, False)] = to_dict(v)
        elif isinstance(v, list):
            result[inflection.camelize(k, False)] = []
            for v_elem in v:
                if is_dataclass(v_elem):
                    result[inflection.camelize(k, False)].append(to_dict(v_elem))
                else:
                    result[inflection.camelize(k, False)].append(v_elem)
        else:
            result[inflection.camelize(k, False)] = v
    return result
