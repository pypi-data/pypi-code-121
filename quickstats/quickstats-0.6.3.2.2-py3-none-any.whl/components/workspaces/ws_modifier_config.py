import os
import re
import json
import time
from typing import Optional, Union, List, Dict


from quickstats.parsers import ConfigParser
    
    
class WSModifierConfig(ConfigParser):
    
    kConfigFormat = {
        'input_file': {
            'required': True,
            'type': str
        },
        'output_file': {
            'required': False,
            'description': 'Path to the location of training scripts ' +\
                           ' (or the directory containing the training scripts)',
            'required': True,
            'type': str
        },
        'model_config': {
            'abbr': 'm',
            'description': 'Name of the model configuration to use',
            'required': True,
            'type': dict
        },
        'search_space': {
            'abbr': 's',
            'description': 'Name of the search space configuration to use',
            'required': True,
            'type':dict
        },
        'hpo_config': {
            'abbr': 'o',
            'description': 'Name of the hpo configuration to use',
            'required': True,
            'type':dict
        },
        'grid_config': {
            'abbr': 'g',
            'description': 'Name of the grid configuration to use',
            'required': True,
            'type':dict
        }
    }
    
    def __init__(self, source:Union[str, Dict]):
        pass
    
    def parse_config(self, source:Union[str, Dict]):
        pass
    
    @classmethod
    def read_json(cls, filename:str):
        self.validate_file(filename)
    
    @classmethod
    def read_xml(cls, filename:str):
        self.validate_file(filename)
    
    def to_json(self, path:str):
        pass
    
    def to_xml(self, path:str):
        pas
