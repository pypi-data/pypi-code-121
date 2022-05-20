import json
import os
from dataclasses import dataclass
from pathlib import Path
from typing import List


config_encoding = "utf-8"


def get_configfile(filename_base: str) -> Path:
    for envvar, filename in [
        ("APPDATA", f"{filename_base}.json"),
        ("HOME", f".{filename_base}.json"),
    ]:
        userdir = os.getenv(envvar, None)
        if userdir is None:
            continue
        return Path(userdir, filename)

    raise FileNotFoundError("Could not determine user directory")


@dataclass
class LockMyResourceConfig:
    user: str
    dbfile: str


def dataclass_fieldnames(dataclass: type) -> List[str]:
    return tuple(dataclass.__dataclass_fields__.keys())


class ConfigFile:
    def __init__(self, filename_base: str, dataclass: type):
        self.configfile = get_configfile(filename_base)
        self.dataclass = dataclass
        self.fieldnames = dataclass_fieldnames(dataclass)

    def read_config_dict(self):
        if self.configfile.exists() is False:
            return {}
        return json.loads(self.configfile.read_text(encoding=config_encoding))

    def read_config(self):
        config_dict = self.read_config_dict()
        field_values = (config_dict.get(fieldname, None)
                        for fieldname in self.fieldnames)
        return self.dataclass(*field_values)

    def write_config(self, dataobj):
        assert isinstance(dataobj, self.dataclass)
        config_dict = {
            fieldname: getattr(dataobj, fieldname)
            for fieldname in self.fieldnames
        }
        self.configfile.write_text(json.dumps(
            config_dict), encoding=config_encoding)


class LockMyResourceConfigFile(ConfigFile):
    def __init__(self):
        super().__init__("lockmyresource", LockMyResourceConfig)
