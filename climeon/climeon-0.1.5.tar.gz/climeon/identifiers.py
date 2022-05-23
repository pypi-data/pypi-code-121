"""Checks for system identifier strings."""

# Standard modules
import re

# Regular expression patterns for ID strings
ID_STRING = r"^(0[1-9]00)\d{6}$"
HP_MODULE = r"^(0100)\d{6}$"
ST_MODULE = r"^(0200)\d{6}$"
ST_POWERBLOCK = r"^(0700)\d{6}$"
HP_POWERBLOCK = r"^(0800)\d{6}$"
HP_SYSTEM = r"^(0900)\d{6}$"

def valid_id(id_string):
    """Check if an ID string is valid."""
    return re.match(ID_STRING, id_string) is not None

def hp_module(id_string):
    """Check if an ID string matches HP module pattern."""
    return re.match(HP_MODULE, id_string) is not None

def st_module(id_string):
    """Check if an ID string matches ST module pattern."""
    return re.match(ST_MODULE, id_string) is not None

def st_powerblock(id_string):
    """Check if an ID string matches ST PowerBlock pattern."""
    return re.match(ST_POWERBLOCK, id_string) is not None

def hp_powerblock(id_string):
    """Check if an ID string matches HP PowerBlock pattern."""
    return re.match(HP_POWERBLOCK, id_string) is not None

def hp_system(id_string):
    """Check if an ID string matches HPSystem pattern."""
    return re.match(HP_SYSTEM, id_string) is not None

def module(id_string):
    """Check if an ID string matches any module pattern."""
    return st_module(id_string) or hp_module(id_string)

def powerblock(id_string):
    """Check if an ID string matches any PowerBlock pattern."""
    return st_powerblock(id_string) or hp_powerblock(id_string)
