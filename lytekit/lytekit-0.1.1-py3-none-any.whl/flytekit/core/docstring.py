import json
import re
import traceback
from typing import Callable, Dict, Optional

import yaml
from docstring_parser import parse

_yaml_metadata_regex = re.compile(r"(.*)__metadata__:(.*)", re.MULTILINE | re.DOTALL)


class Docstring(object):
    def __init__(self, docstring: str = None, callable_: Callable = None):
        if docstring is not None:
            self._parsed_docstring = parse(docstring)
        else:
            self._parsed_docstring = parse(callable_.__doc__)

    @property
    def input_descriptions(self) -> Dict[str, str]:
        res = {}
        for idx, x in enumerate(self._parsed_docstring.params):
            meta = _yaml_metadata_regex.match(x.description)

            if meta is not None:
                try:
                    res[x.arg_name] = {
                        "idx": idx,
                        "name": x.arg_name,
                        "default": x.default,
                        "description": meta.group(1),
                        "meta": yaml.safe_load(meta.group(2)),
                    }
                except:
                    pass

            if x.arg_name not in res:
                res[x.arg_name] = {"idx": idx, "name": x.arg_name, "default": x.default, "description": x.description}

            if idx == 0:
                if self._parsed_docstring.long_description is not None:
                    meta = _yaml_metadata_regex.match(self._parsed_docstring.long_description)
                    if meta is not None:
                        try:
                            res[x.arg_name]["__workflow_meta__"] = {
                                "short_description": self._parsed_docstring.short_description,
                                "long_description": meta.group(1),
                                "meta": yaml.safe_load(meta.group(2)),
                            }
                        except Exception:
                            print("Failed to parse workflow metadata:")
                            traceback.print_exc()
                            pass

                if "__workflow_meta__" not in res[x.arg_name]:
                    res[x.arg_name]["__workflow_meta__"] = {
                        "short_description": self._parsed_docstring.short_description,
                        "long_description": self._parsed_docstring.long_description,
                    }

        return {k: json.dumps(v) for k, v in res.items()}

    @property
    def output_descriptions(self) -> Dict[str, str]:
        return {p.return_name: p.description for p in self._parsed_docstring.many_returns}

    @property
    def short_description(self) -> Optional[str]:
        return self._parsed_docstring.short_description

    @property
    def long_description(self) -> Optional[str]:
        return self._parsed_docstring.long_description
