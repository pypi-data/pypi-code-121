from typing import Optional, Union, Dict, List
import os
import json
import glob

from quickstats import semistaticmethod

class ConfigParser:
    @staticmethod
    def validate_file(filename:str):
        if not os.path.exists(filename):
            raise FileNotFoundError(f"configuration file \"{filename}\" does not exist")
    
    