import inspect

swagger_json_project = []

swagger_json_class = []
python_column_type_dict = {
    "list": "array",
    "str": "string",
    "int": "integer",
    "dict": "object",
    "bool": "boolean",
    "float": "multipleOf"
}
definitions = {}


def parser_swagger(func, desc):
    if type(func).__name__ == "type":
        swagger_json_project.append(
            {
                "desc": desc,
                "route": func.__route_name__,
                "method_list": swagger_json_class.copy()
            }
        )
        swagger_json_class.clear()

    elif type(func).__name__ == "function":
        default_args = get_default_args(func)
        type_args = get_type_args(func)
        param_list = []
        func_params = func.__code__.co_varnames
        if func.__http_method__ == "get":
            for i in range(1, func.__code__.co_argcount):
                k = func_params[i]
                param = {
                    "required": True,
                    "name": k,
                    "in": "query",
                }
                if default_args.get(k):
                    param["required"] = False
                    param["default"] = default_args[k]["default"]
                param_list.append(param)
            swagger_json_class.append({
                "route": func.__route_name__,
                "summary": "Place an order for a pet",

                "operationId": "placeOrder",
                "consumes": ["application/json"],
                "produces": ["application/json", "application/xml"],
                "parameters": param_list,
                "description": desc,
                "http_method": func.__http_method__
            })
        elif func.__http_method__ == "post":

            schema = {
                "type": "object",
                "properties": {
                }
            }
            for i in range(1, func.__code__.co_argcount):
                k = func_params[i]
                param_type = python_column_type_dict[type_args.get(k, {}).get("type", str).__name__]
                if param_type in ["string", "integer"]:
                    schema["properties"][k] = {
                        "type": param_type,
                        "enum": [default_args.get(k, {}).get("default", "string")]
                    }
                elif param_type in ["array"]:
                    schema["properties"][k] = {
                        "type": "array",
                        "xml": {"wrapped": True},
                        "items": {"type": "string"},
                        "enum": [default_args.get(k, {}).get("default", "string")]
                    }
                elif param_type in ["object"]:
                    schema["properties"][k] = {
                        "type": "object",
                        "properties": {

                        }
                    }

            param = {
                "required": True,
                "name": "body",
                "in": "body",
                "schema": schema
            }
            swagger_json_class.append({
                "route": func.__route_name__,
                "parameters": [param],
                "description": desc,
                "http_method": func.__http_method__
            })
        else:
            pass


def get_type_args(func):
    signature = inspect.signature(func)
    return {
        k: {
            "type": v.annotation
        }
        for k, v in signature.parameters.items()
        if v.annotation is not inspect.Parameter.empty
    }


def get_default_args(func):
    signature = inspect.signature(func)
    return {
        k: {
            "default": v.default
        }
        for k, v in signature.parameters.items()
        if v.default is not inspect.Parameter.empty
    }
