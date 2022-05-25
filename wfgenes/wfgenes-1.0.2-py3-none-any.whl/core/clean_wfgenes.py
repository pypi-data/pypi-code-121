
""" wfGenes: Automatic workflow generator."""


__author__ = 'Mehdi Roozmeh'
__email__ = 'mehdi.roozmeh@kit.edu'
__copyright__ = 'Copyright 2020, Karlsruhe Institute of Technology'

import os
import os.path
from copy import deepcopy
from collections import OrderedDict
import shutil
import argparse
import json
import xmlschema
import yaml
from wfgenes.core.initial_wfgenes import BasewfGenes



class CleanwfGenes(BasewfGenes):
    """"Clean up previous files for old wConfig"""
    def __init__(self, blueargs):
        #BasewfGenes.__init__(self, blueargs)
        self.clean_wfgenes()


    def clean_wfgenes(self):
        if os.path.exists(self.workflow_path):
            shutil.rmtree(self.workflow_path)   