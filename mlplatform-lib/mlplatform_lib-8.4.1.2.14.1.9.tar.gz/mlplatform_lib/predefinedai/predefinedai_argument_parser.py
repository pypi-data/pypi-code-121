import argparse
import json
import sys
import re
from decimal import Decimal


class PredefinedAIArgumentParser(argparse.ArgumentParser):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.predefinedai_args = {}
        self.predefinedai_support_args = (
            "PredefinedAIArgumentParser.int",
            "PredefinedAIArgumentParser.float",
            "PredefinedAIArgumentParser.str",
            "PredefinedAIArgumentParser.column",
            "PredefinedAIArgumentParser.columns",
            "PredefinedAIArgumentParser.bool",
        )
        self.predefinedai_inner_func = (
            "int_parse",
            "float_parse",
            "str_parse",
            "column_parse",
            "columns_parse",
            "bool_parse",
        )

    def add_argument(self, *args, **kwargs):
        if "action" in kwargs and kwargs["action"] == "help":
            super().add_argument(*args, **kwargs)
            return

        if "type" not in kwargs or not kwargs["type"][0].__name__ in self.predefinedai_inner_func:
            raise ValueError(f"type must be in {self.predefinedai_support_args}")

        if "action" in kwargs:
            raise ValueError("Cannot use action in PredefinedAIArgumentParser.")

        parse_func, local_params = kwargs["type"]
        kwargs["type"] = parse_func
        super().add_argument(*args, **kwargs)

        if not args[0].startswith("--"):
            raise ValueError("name must start with --")

        name = args[0][2:]
        default = None
        if "default" in kwargs:
            default = kwargs["default"]

        description = None
        if "help" in kwargs:
            description = kwargs["help"]
        else:
            description = ""

        required = None
        if "required" in kwargs:
            required = kwargs["required"]
        else:
            required = False

        choices = None
        if "choices" in kwargs:
            choices = kwargs["choices"]

        arg_dict = {"name": name, "default": default, "description": description, "required": required}
        if parse_func.__name__ == "int_parse":
            if default is None:
                default = local_params["max"] - local_params["min"]

            if choices is None and local_params["window"] == 0:
                raise ValueError("Please specify choices or window.")

            if choices is not None and local_params["window"] != 0:
                raise ValueError("Cannot use choices and window both.")

            arg_dict.update({"type": "int", "min": local_params["min"], "max": local_params["max"]})
            if choices is not None:
                arg_dict["choices"] = choices
            else:
                arg_dict["window"] = local_params["window"]
        elif parse_func.__name__ == "float_parse":
            if default is None:
                default = local_params["max"] - local_params["min"]

            if choices is None and local_params["window"] == 0.0:
                raise ValueError("Please specify choices or window.")

            if choices is not None and local_params["window"] != 0.0:
                raise ValueError("Cannot use choices and window both.")

            arg_dict.update({"type": "float", "min": local_params["min"], "max": local_params["max"]})
            if choices is not None:
                arg_dict["choices"] = choices
            else:
                arg_dict["window"] = local_params["window"]
        elif parse_func.__name__ == "str_parse":
            if default is None:
                default = ""

            arg_dict.update({"type": "str"})
            if choices is not None:
                arg_dict["choices"] = choices
        elif parse_func.__name__ == "column_parse":
            if default is None:
                default = ""

            arg_dict.update({"type": "column"})
        elif parse_func.__name__ == "columns_parse":
            if default is None:
                default = "[]"

            arg_dict.update(
                {
                    "type": "columns",
                    "name": name,
                    "default": default,
                    "description": description,
                    "required": required,
                }
            )
        elif parse_func.__name__ == "bool_parse":
            if default is None:
                default = True

            arg_dict.update({"type": "bool"})
        else:
            raise argparse.ArgumentTypeError(f"parse function {parse_func.__name__} cannot found.")

        self.predefinedai_args[arg_dict["name"]] = arg_dict

    @staticmethod
    def int(min: int = 0, max: int = sys.maxsize, window: int = 1):
        if min > max:
            raise argparse.ArgumentTypeError(f"min({min}) must be less than max({max})")

        def int_parse(arg):
            if isinstance(arg, str):
                arg = re.sub("[\\\"']", "", arg)

            try:
                val = int(arg)
            except ValueError:
                raise argparse.ArgumentTypeError(f"{arg} cannot cast to integer.")

            if val < min:
                raise argparse.ArgumentTypeError(f"{arg} must be greater than {min}.")
            elif val > max:
                raise argparse.ArgumentTypeError(f"{arg} must be less than {max}.")
            elif (val - min) % window > 1e-128:
                raise argparse.ArgumentTypeError(f"'({arg} - {min}) mod {window}' must be zero.")
            return val

        return int_parse, locals()

    @staticmethod
    def float(min: float = 0.0, max: float = sys.float_info.max, window: float = 1.0):
        if min > max:
            raise argparse.ArgumentTypeError(f"min({min}) must be less than max({max})")

        def float_parse(arg):
            if isinstance(arg, str):
                arg = re.sub("[\\\"']", "", arg)

            try:
                val = float(arg)
            except ValueError:
                raise argparse.ArgumentTypeError(f"{arg} cannot cast to float.")

            if val < min:
                raise argparse.ArgumentTypeError(f"{arg} must be greater than {min}.")
            elif val > max:
                raise argparse.ArgumentTypeError(f"{arg} must be less than {max}.")
            elif ((Decimal(str(val)) - Decimal(str(min))) % Decimal(str(window))) != 0:
                raise argparse.ArgumentTypeError(f"'({arg} - {min}) mod {window}' must be zero.")
            return val

        return float_parse, locals()

    @staticmethod
    def str():
        def str_parse(arg):
            try:
                val = str(arg)
            except ValueError:
                raise argparse.ArgumentTypeError(f"{arg} cannot cast to str.")

            return val

        return str_parse, locals()

    @staticmethod
    def column():
        def column_parse(arg):
            try:
                val = str(arg)
            except ValueError:
                raise argparse.ArgumentTypeError(f"{arg} cannot cast to str. column must be str.")

            return val

        return column_parse, locals()

    @staticmethod
    def columns():
        def columns_parse(arg):
            try:
                val = json.loads(arg)
            except Exception as e:
                print(e)
                raise argparse.ArgumentTypeError(
                    f"{arg} cannot cast to dictionary. columns must be json string."
                )

            return val

        return columns_parse, locals()

    @staticmethod
    def bool():
        def bool_parse(arg):
            if isinstance(arg, str):
                arg = re.sub("[\\\"']", "", arg)

            if isinstance(arg, bool):
                return arg
            if arg.lower() in ("yes", "true", "t", "y", "1"):
                return True
            elif arg.lower() in ("no", "false", "f", "n", "0"):
                return False
            else:
                raise argparse.ArgumentTypeError("Boolean value expected.")

        return bool_parse, locals()
