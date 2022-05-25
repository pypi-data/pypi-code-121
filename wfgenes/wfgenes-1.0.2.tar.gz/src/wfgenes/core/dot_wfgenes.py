
""" wfGenes: Automatic workflow generator."""


__author__ = 'Mehdi Roozmeh'
__email__ = 'mehdi.roozmeh@kit.edu'
__copyright__ = 'Copyright 2020, Karlsruhe Institute of Technology'

import os
import os.path
import sys
from collections import OrderedDict
import json
import yaml
from wfgenes.core.initial_wfgenes import BasewfGenes
import time

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))


class DotwfGenes():
    """ DOT file generation from a wconfig file """

    def __init__(self,  wfgenes_init):
        self.dot_generation(wfgenes_init)

    def dot_generation(self, wfgenes_init):
        wfgenes_init.dot_path = os.path.join(wfgenes_init.workflow_path, 'DOT')
        def_color = 'none'
        def_edgecolor = ''
        if not os.path.exists(wfgenes_init.dot_path):
            os.makedirs(wfgenes_init.dot_path)
        dot_file = os.path.join(
            wfgenes_init.dot_path, wfgenes_init.interface_dict['workflow_name'] + '.dot')
        dot_string = 'digraph {\n'
        dot_string += '  graph[\n'
        dot_string += '\tname=' + wfgenes_init.interface_dict['workflow_name'] + '\n'
        dot_string += '  ]; \n'
        for i in range(wfgenes_init.routine_number):
            dot_string += str(i) + ' [' + '\n'
            dot_string += 'state=NONE \n'
            dot_string += 'name="' + wfgenes_init.routine_name[i] + '"\n'
            dot_string += 'label="' + wfgenes_init.routine_name[i] + '"\n'
            dot_string += ' style=filled \n'
            dot_string += 'color="' + def_edgecolor + '"\n'
            dot_string += 'fillcolor="'+def_color+'"\n'
            dot_string += '  ]; \n'

        for i in range(wfgenes_init.routine_number):
            for j in range(wfgenes_init.subroutine_number[i]):
                for k in range(len(wfgenes_init.inputs[i][j])):
                    if wfgenes_init.inputs_nodup[i][j][k] != \
                        'duplicate' and wfgenes_init.inputs_no_locdep[i][j][k] != 'dependent'\
                            and wfgenes_init.inputs_links[i][j][k][0].isnumeric() and wfgenes_init.inputs_locname[i][j][k] != 'NULL':
                        dot_string += wfgenes_init.inputs_links[i][j][k][0] + \
                            '->' + str(i) + '[ \n'
                        dot_string += 'label="' + \
                            wfgenes_init.inputs_locname[i][j][k] + '"\n'
                        dot_string += '  ]; \n'

        dot_string += '  } \n'

        with open(dot_file, 'w') as file:
            file.write(dot_string)
        self.pdf_file = os.path.join(
            wfgenes_init.dot_path, wfgenes_init.interface_dict['workflow_name'] + '.pdf')
        self.png_file = os.path.join(
            wfgenes_init.dot_path, wfgenes_init.interface_dict['workflow_name'] + '.png')

        cmd = 'dot -Tpdf ' + dot_file + ' -o ' + self.pdf_file
        os.popen(cmd)
        cmd = 'dot -Tpng ' + dot_file + ' -o ' + self.png_file
        os.popen(cmd)

        
