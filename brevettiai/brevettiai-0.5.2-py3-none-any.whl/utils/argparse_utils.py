import argparse
import json
from distutils.util import strtobool

argparse_types = {
    dict: lambda x: json.loads(x),
    list: lambda x: json.loads(x),
    bool: lambda x: bool(strtobool(x))
}


def parse_args_from_dict(args, target):
    parser = argparse.ArgumentParser()
    args = [arg for arg_str in args for arg in arg_str.split("=")]
    for arg in args:
        if arg.startswith("--"):
            uri = arg[2:].split(".")
            try:
                x = target
                for key in uri:
                    x = x[key]
                type_ = argparse_types.get(type(x), type(x))
            except KeyError:
                type_ = str

            parser.add_argument(arg, type=type_)
    target_args, _ = parser.parse_known_args(args)
    return target_args


def overload_dict_from_args(args, target, errors_ok=True):
    for k, v in vars(args).items():
        uri = k.split(".")
        try:
            x = target
            for key in uri[:-1]:
                x = x[key]
            x[uri[-1]] = v
        except KeyError as ex:
            if not errors_ok:
                raise ex
