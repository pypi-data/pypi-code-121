# (c) 2015-2017 Acellera Ltd http://www.acellera.com
# All Rights Reserved
# Distributed under HTMD Software License Agreement
# No redistribution in whole or part
#
from difflib import get_close_matches
import abc
import textwrap


def ensurelist(tocheck, tomod=None):
    if tomod is None:
        tomod = tocheck
    if type(tocheck).__name__ == "ndarray":
        return list(tomod)
    if not isinstance(tocheck, list) and not isinstance(tocheck, tuple):
        return [tomod]
    return tomod


def _islist(value, istuple=True):
    if (
        isinstance(value, list)
        or (istuple and isinstance(value, tuple))
        or (type(value).__name__ == "ndarray")
    ):
        return True
    return False


def _isnone(value):
    if value is None or (isinstance(value, str) and value.lower() == "none"):
        return True
    return False


class ProtocolInterface:
    def __init__(self):
        # Stores the information on the arguments. Not the values. Values are stored in __dict__
        self._commands = {}
        # Dictionary of deprecated commands and their replacements
        self._deprecated = {}
        # Total number of commands
        self._numCommands = 0
        # The order in which commands are added for nicer doc prints
        self._commandsOrder = {}

    def _castAndSetAttr(self, key, value):
        key, value = self._validate(key, value, cast=True)
        self.__setattr__(key, value)

    def __setattr__(self, key, value):
        if key[0] != "_":
            key = self._validate(key, value)
        if key:
            self.__dict__[key] = value

    def __str__(self):
        sortedkeys = [
            x[0] for x in sorted(self._commandsOrder.items(), key=lambda x: x[1])
        ]
        s = ""
        for cmd in sortedkeys:
            if isinstance(self.__dict__[cmd], str):
                s += f"{cmd} = '{self.__dict__[cmd]}'\n"
            else:
                s += f"{cmd} = {self.__dict__[cmd]}\n"
        return s

    def _arg(
        self,
        key,
        datatype,
        descr,
        default=None,
        validator=None,
        valid_values=None,
        nargs="?",
        required=False,
        inout="input",
        shortdescr=None,
    ):
        if shortdescr is None:
            shortdescr = descr
        validator = ensurelist(validator)
        self._commands[key] = {
            "datatype": datatype,
            "description": descr,
            "default": default,
            "validator": validator,
            "valid_values": valid_values,
            "nargs": nargs,
            "required": required,
            "inout": inout,
            "shortdesc": shortdescr,
        }
        self._commandsOrder[key] = self._numCommands
        self._numCommands += 1
        self.__dict__[key] = default

    def _cmdDeprecated(self, key, newkey=None):
        self._deprecated[key] = newkey

    def _printDocString(self, returndoc=False):
        def _docString(command):
            from .validators import Dictionary

            doc1 = ""
            if command["valid_values"] is not None:
                doc1 += f"{command['valid_values']}, "
            doc1 += f"{command['datatype']}"
            if isinstance(command["default"], str):
                doc1 += f", default='{command['default']}'"
            else:
                doc1 += f", default={command['default']}"
            if command["required"]:
                doc1 += ", required"
            doc2 = command["description"]
            for v in command["validator"]:
                if isinstance(v, Dictionary) and v.valid_keys is not None:
                    doc2 += " (valid dict entries: "
                    for i, vk in enumerate(v.valid_keys):
                        vv = "<value>"
                        if v.valid_values is not None and vk in v.valid_values:
                            vall = " or ".join(
                                (f"'{i}'" if isinstance(i, str) else f"{i}")
                                for i in v.valid_values[vk]
                            )
                            vv = f"<{vall}>"
                        doc2 += f"{{'{vk}': {vv}}}"
                        if i != len(v.valid_keys) - 1:
                            doc2 += ", "
                    doc2 += ")"
            return (
                doc1 + "\n\t" + textwrap.fill(doc2, width=112, subsequent_indent="\t")
            )

        sortedkeys = [
            x[0] for x in sorted(self._commandsOrder.items(), key=lambda x: x[1])
        ]
        docs = ""
        for k in sortedkeys:
            docs += f"{k} : {_docString(self._commands[k])}\n"
        if returndoc:
            return docs
        else:
            print(docs)

    def _validate(self, key, value, cast=False):
        if key in self._deprecated:
            newkey = self._deprecated[key]
            if not newkey:
                print(
                    f"Attribute '{key}' is deprecated and is no longer required. Modify your code appropriately."
                )
                return None
            else:
                print(
                    f"Attribute '{key}' is deprecated and replaced by '{newkey}'. Modify your code appropriately."
                )
                key = newkey

        if key not in self._commands:
            strerror = f"Attribute '{key}' not allowed in this class."
            match = get_close_matches(key, self._commands)
            if match:
                strerror += f" Try '{match[0]}'"
            raise ValueError(strerror)

        validator = ensurelist(self._commands[key]["validator"])

        castvalues = value
        islist = False
        if validator is not None:
            try:
                self._checknargs(value, self._commands[key]["nargs"])
                if not _isnone(value):
                    islist = _islist(value)
                    value = ensurelist(value)
                    for vv in validator:
                        if vv is None:
                            continue
                        # Adding an exception for Function val which can get a tuple of (func, arg, dict) or (func, arg)
                        from .validators import Function

                        if isinstance(vv, Function):
                            value = Function.fixDelayedTuples(value)
                        # Finished with exception, continuing
                        castvalues = []
                        for v in value:
                            if cast:
                                v = vv.cast(v)
                                castvalues.append(v)
                            vv.validate(v)
            except Exception as e:
                raise TypeError(f'Failed to set attribute "{key}" with error: {e}')

        valid_values = self._commands[key]["valid_values"]
        if valid_values is not None:
            if not _isnone(value):
                value = ensurelist(value)
                for v in value:
                    if v not in valid_values:
                        raise ValueError(
                            f"Attribute {key} only accepts following values: {valid_values}"
                        )
        if not cast:
            return key
        else:
            return key, castvalues if islist else castvalues[0]

    def _checknargs(self, value, nargs):
        if isinstance(nargs, str) and nargs.lower() == "any":
            return
        elif isinstance(nargs, str):
            if nargs == "?" and _islist(value):
                raise ValueError("it does not accept lists.")
            # elif nargs == '*' and not _isnone(value) and not _islist(value):
            #     raise ValueError('it only accepts single values, lists or None')
            elif nargs == "+" and _isnone(value):
                raise ValueError("it only accepts single values or lists, not None.")
            elif nargs != "?" and nargs != "*" and nargs != "+":
                raise RuntimeError(
                    'it has unknown nargs parameter "{}". Only accepted values are "?", "+", "*" and integers'.format(
                        nargs
                    )
                )
        elif isinstance(nargs, int):
            if not _islist(value) or (_islist(value) and len(value) != nargs):
                raise ValueError(f"it only accepts lists of {nargs} elements")
        else:
            raise RuntimeError(
                "nargs contains an invalid value type (should be string or integer)"
            )

    def _checkRequired(self):
        for cmd in self._commands:
            if self._commands[cmd]["required"] is True and self.__dict__[cmd] is None:
                raise ValueError(
                    'Attribute "{}" is a required attribute for executing this protocol. Its value cannot '
                    'be "None"'.format(cmd)
                )

    def _toArgParse(self, description, parser=None):
        import argparse
        from .validators import Number, Boolean

        if parser is None:
            parser = argparse.ArgumentParser(description=description)
            # TODO: Add add_boolean_argument function to parser (see acetk)

        sortedkeys = [
            x[0] for x in sorted(self._commandsOrder.items(), key=lambda x: x[1])
        ]
        for k in sortedkeys:
            cmd = self._commands[k]
            # on testing cuzzo87 --> to fix #2
            validator = (
                cmd["validator"][0] if len(cmd["validator"]) == 1 else cmd["validator"]
            )

            defstr = (
                " (default: %(default)s)"
                if cmd["required"] is not True
                else " (MANDATORY)"
            )

            # on testing cuzzo87 --> cmd['validator'] --> validator. for fixing #2
            if validator is not None and isinstance(validator, Number):
                parser.add_argument(
                    f"--{k}",
                    help=f"{cmd['description']}{defstr}",
                    default=cmd["default"],
                    required=cmd["required"],
                    type=validator.datatype,
                    nargs=cmd["nargs"],
                )
            elif validator is not None and isinstance(validator, Boolean):
                parser.add_boolean_argument(
                    f"{k}",
                    arghelp=f"{cmd['description']}{defstr}",
                    default=cmd["default"],
                    required=cmd["required"],
                )
            else:
                parser.add_argument(
                    f"--{k}",
                    help=f"{cmd['description']}{defstr}",
                    default=cmd["default"],
                    required=cmd["required"],
                    nargs=cmd["nargs"],
                    choices=cmd["valid_values"],
                )

        return parser

    def _fromArgParse(self, args):
        argsdict = vars(args)
        for k in argsdict:
            self.__setattr__(k, argsdict[k])

    def _fromJSON(self, fname):
        import json

        with open(fname, "r") as f:
            config = json.load(f)

        for k in config:
            self.__setattr__(k, config[k])

    def _describe(self, outf=None):
        from copy import deepcopy
        from .validators import _Validator
        import inspect

        # Have to convert validator objects to strings to be able to dump it as json
        desc = deepcopy(self._commands)

        def substituteClasses(d):  # Substitute classes with their string descriptions
            for k, v in d.items():
                if isinstance(v, dict):
                    substituteClasses(v)
                else:
                    if _islist(v, istuple=False):
                        for i, vv in enumerate(v):
                            if inspect.isclass(vv) or isinstance(vv, _Validator):
                                d[k][i] = str(vv)
                    if inspect.isclass(v) or isinstance(v, _Validator):
                        d[k] = str(v)

        substituteClasses(desc)

        if outf is None:
            return desc
        else:
            import json

            with open(outf, "w") as fp:
                json.dump(desc, fp, indent=4)


class RunnableProtocol(ProtocolInterface):
    def __init__(self, description):
        super().__init__()
        self._description = description

    @abc.abstractmethod
    def run(self):
        pass

    def _describe(self, outf=None):
        desc = super()._describe()
        desc["description"] = self._description
        desc["classname"] = self.__class__.__name__

        if outf is None:
            return desc
        else:
            import json

            with open(outf, "w") as fp:
                json.dump(desc, fp, indent=4)


class WebProtocol(RunnableProtocol):
    def _arg(
        self,
        key,
        datatype,
        descr,
        default=None,
        validator=None,
        valid_values=None,
        nargs="?",
        required=False,
        inout="input",
        shortdescr=None,
        weboptions=None,
    ):
        super()._arg(
            key,
            datatype,
            descr,
            default,
            validator,
            valid_values,
            nargs,
            required,
            inout,
            shortdescr,
        )
        self._commands[key]["weboptions"] = weboptions


def weboptions(ignore=False, visualize=False):
    return {"ignore": ignore, "visualize": visualize}
