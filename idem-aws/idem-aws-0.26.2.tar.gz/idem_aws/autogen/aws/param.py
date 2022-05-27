import botocore.client
import botocore.docs.docstring
import botocore.exceptions
import botocore.model

__func_alias__ = {"type_": "type"}


def parse(hub, param: "botocore.model.Shape", required: bool):
    docstring = hub.tool.format.html.parse(param.documentation)
    return {
        "required": required,
        "default": None,
        "target_type": "mapping",
        "target": "kwargs",
        "param_type": hub.pop_create.aws.param.type(param.type_name),
        "doc": "\n            ".join(
            hub.tool.format.wrap.wrap(
                docstring,
                width=96,
            )
        ),
    }


def type_(hub, type_name: str):
    if type_name == "string":
        return "Text"
    elif type_name == "map":
        return "Dict"
    elif type_name == "structure":
        return "Dict"
    elif type_name == "list":
        return "List"
    elif type_name == "boolean":
        return "bool"
    elif type_name in ("integer", "long"):
        return "int"
    elif type_name in ("float", "double"):
        return "float"
    elif type_name == "timestamp":
        return "Text"
    elif type_name == "blob":
        return "ByteString"
    else:
        raise NameError(type_name)
