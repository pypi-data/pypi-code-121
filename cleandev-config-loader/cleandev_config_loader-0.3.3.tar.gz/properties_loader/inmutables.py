import os
from backports.strenum import StrEnum

class _EnvVars(StrEnum):
    ROOT_PATH = 'ROOT_PATH'
    CONFIG_FILE = 'CONFIG_FILE'

class _PriorityProperties(StrEnum):
    PARAMS = '1'
    ENVS_VARS = '2'
    DEFAULT = '3'


class _DfValues(StrEnum):
    DF_ROOT_PATH = str(os.getcwd())
    DF_PATH_FILE = 'properties.ini'


class _MsgError(StrEnum):
    ERROR_TO_LOAD_PROPERTIES_FILE = 'Error al cargar el archivo de properties'
    ROOT_PATH_VARIABLE_NOT_DEFINED = 'ROOT_PATH variable not defined'