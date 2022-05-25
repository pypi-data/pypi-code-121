
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


class PywrapperwfGens(BasewfGenes):
    """Generate Python wrapper for wconfig nodes"""

    def __init__(self, wfgenes_init , blueargs):
        #BasewfGenes.__init__(wfgenes_init, blueargs)
        self.pywrapper_simstack(wfgenes_init)
    
    
    def pywrapper_simstack(self, wfgenes_init):

        first_i = 0
        for i in range(wfgenes_init.routine_number):
            wfg_task_wrapper = ""
            wfg_task_wrapper += "import yaml\n"
            wfg_task_wrapper += "import numpy as np\n"
            simstack_path = os.path.join(wfgenes_init.workflow_path, 'SimStack')
            wano_path = os.path.join(simstack_path, 'wanos', wfgenes_init.routine_name[i])
            if not os.path.exists(wano_path):
                os.makedirs(wano_path)
            wfgenes_init.wrapper_path = os.path.join(
                wano_path, wfgenes_init.routine_name[i] + '_wrapper.py')
            for j in range(wfgenes_init.subroutine_number[i]):
                if wfgenes_init.func[i][j][0] != 'BUILTIN' and wfgenes_init.func_nodup[i][j] != 'duplicate' and wfgenes_init.func_nodup[i][j] != 'duplicate':
                    wfg_task_wrapper += 'from ' + str(wfgenes_init.func[i][j][0]) + ' import ' + str(wfgenes_init.func[i][j][1]) + '\n'
                    first_i +=1
            wfg_task_wrapper += "\nif __name__ == '__main__':\n\n"
            for j in range(wfgenes_init.subroutine_number[i]):
                for k in range(len(wfgenes_init.inputs_nodup[i][j])):
                    if wfgenes_init.inputs_nodup[i][j][k] != 'duplicate' and wfgenes_init.inputs_no_locdep[i][
                            j][k] != 'inner_dependent' and wfgenes_init.inputs_links[i][j][k][0].isnumeric() == False:
                        wfg_task_wrapper += '\n \t#Read Input #' + str(k + 1) + ' from subroutine #' + str(j + 1) + ' in routine #' + str(i) + '\n'
                        wfg_task_wrapper += "\tyaml_stream = open('" + wfgenes_init.inputs[i][j][k] + ".yaml', 'r')\n"
                        wfg_task_wrapper += "\t" + wfgenes_init.inputs[i][j][k] + " = yaml.load(yaml_stream, Loader=yaml.Loader)\n\n"
                    if wfgenes_init.inputs_nodup[i][j][k] != 'duplicate' and wfgenes_init.inputs_no_locdep[i][j][k] != 'inner_dependent' and wfgenes_init.inputs_links[i][j][k][0].isnumeric():
                        wfg_task_wrapper += '\n \t#Read Input #' + str(k +1) + ' from subroutine #' + str(j +1) + ' in routine #' + str(i) + '\n'
                        wfg_task_wrapper += "\tyaml_stream = open('" + wfgenes_init.inputs_locname[i][j][k] + ".yaml', 'r')\n"
                        wfg_task_wrapper +=  "\t" + wfgenes_init.inputs_locname[i][j][k] + " = yaml.load(yaml_stream, Loader=yaml.Loader)\n\n"

                if wfgenes_init.func[i][j][0] != 'BUILTIN':
                    wfg_task_wrapper += '\n\t# Call subroutine #' + str(j + 1) + '\n'
                    wfg_task_wrapper += '\t'
                    for k in range(len(wfgenes_init.outputs[i][j])):
                        if k != len(wfgenes_init.outputs[i][j]) - 1:
                            wfg_task_wrapper += wfgenes_init.outputs_locname[i][j][k] + ", "
                        else:
                            wfg_task_wrapper += wfgenes_init.outputs_locname[i][j][k] + " = "
                    wfg_task_wrapper += wfgenes_init.func[i][j][1] + "("
                    for k in range(len(wfgenes_init.inputs[i][j])):
                        if k != len(
                                wfgenes_init.inputs[i][j]) - 1 and wfgenes_init.inputs_no_locdep[i][j][k] != 'inner_dependent' and wfgenes_init.inputs_links[i][j][k][0].isnumeric() == False:
                            wfg_task_wrapper += str(wfgenes_init.inputs[i][j][k]) + ', '
                        elif k != len(wfgenes_init.inputs[i][j]) - 1 and (wfgenes_init.inputs_no_locdep[i][j][k] == 'inner_dependent' or wfgenes_init.inputs_links[i][j][k][0].isnumeric()):
                            wfg_task_wrapper += str(wfgenes_init.inputs_locname[i][j][k]) + ', '
                        elif k == len(wfgenes_init.inputs[i][j]) - 1 and wfgenes_init.inputs_no_locdep[i][j][k] != 'inner_dependent' and wfgenes_init.inputs_links[i][j][k][0].isnumeric() == False:
                            wfg_task_wrapper += str(wfgenes_init.inputs[i][j][k]) + ")\n\n"
                        elif k == len(wfgenes_init.inputs[i][j]) - 1 and (wfgenes_init.inputs_no_locdep[i][j][k] == 'inner_dependent' or wfgenes_init.inputs_links[i][j][k][0].isnumeric()):
                            wfg_task_wrapper += str(wfgenes_init.inputs_locname[i][j][k]) + ")\n\n"

                    wfg_task_wrapper += "\n\t# Dump outputs into yaml files from subroutine #" + str(j + 1) + '\n'

                    for k in range(len(wfgenes_init.outputs[i][j])):
                        wfg_task_wrapper += '\n\t#Dump Output #' + str(k + 1) + ' from subroutine #' + str(j + 1) + ' in routine # ' + str(i) +'\n'
                        wfg_task_wrapper += "\tfile=open('" + wfgenes_init.outputs_locname[i][j][k] + ".yaml', 'w')\n"
                        wfg_task_wrapper +=  "\tyaml.dump(" + wfgenes_init.outputs_locname[i][j][k] + ", file, default_flow_style=False)\n"
                        wfg_task_wrapper += "\tfile.close\n"
                    wfg_task_wrapper += "\t#End of subroutine #" + str(j + 1) + ' in routine # ' + str(i) + '\n'

                elif wfgenes_init.func[i][j][0] == 'BUILTIN' and wfgenes_init.func[i][j][1] == 'MERGE':
                    wfg_task_wrapper += "\t# Merge Multiple Dictionaries \n"
                    for k in range(len(wfgenes_init.inputs[i][j])):
                        if wfgenes_init.inputs_nodup[i][j][k] != 'duplicate' and wfgenes_init.inputs_no_locdep[i][
                                j][k] != 'inner_dependent' and wfgenes_init.inputs_links[i][j][k][0].isnumeric() == False:
                            wfg_task_wrapper += "if isinstance(" + wfgenes_init.inputs[i][j][k] + ", np.number):\n"
                            wfg_task_wrapper += '\t' + wfgenes_init.inputs_locname[i][j][k] + ' = dict(' + wfgenes_init.inputs_locname[i][j][k] + '= float(' + wfgenes_init.inputs[i][j][k] + ')) \n'
                        elif wfgenes_init.inputs_nodup[i][j][k] != 'duplicate' and (wfgenes_init.inputs_no_locdep[i][j][k] == 'inner_dependent' or wfgenes_init.inputs_links[i][j][k][0].isnumeric()):
                            wfg_task_wrapper += "if isinstance(" + wfgenes_init.inputs_locname[i][j][k] + ", np.number):\n"
                            wfg_task_wrapper += '\t' + wfgenes_init.inputs_locname[i][j][k] + ' = dict(' + wfgenes_init.inputs_locname[i][j][k] + '= float(' + wfgenes_init.inputs_locname[i][j][k] + ')) \n'
                        if wfgenes_init.inputs_nodup[i][j][k] != 'duplicate' and wfgenes_init.inputs_no_locdep[i][
                                j][k] != 'inner_dependent' and wfgenes_init.inputs_links[i][j][k][0].isnumeric() == False:
                            wfg_task_wrapper += "else:\n"
                            wfg_task_wrapper += '\t' + wfgenes_init.inputs_locname[i][j][k] + ' = dict(' + wfgenes_init.inputs_locname[i][j][k] + '= ' + wfgenes_init.inputs[i][j][k] + ') \n\n'
                        elif wfgenes_init.inputs_nodup[i][j][k] != 'duplicate' and (wfgenes_init.inputs_no_locdep[i][j][k] == 'inner_dependent' or wfgenes_init.inputs_links[i][j][k][0].isnumeric()):
                            wfg_task_wrapper += "else:\n"
                            wfg_task_wrapper += '\t' + wfgenes_init.inputs_locname[i][j][k] + ' = dict(' + wfgenes_init.inputs_locname[i][j][k] + '= ' + wfgenes_init.inputs_locname[i][j][k] + ') \n\n'

                    wfg_task_wrapper += '\t' + wfgenes_init.outputs_locname[i][j][0] + '={'
                    for k in range(len(wfgenes_init.inputs[i][j])):
                        if wfgenes_init.inputs_nodup[i][j][k] != 'duplicate':
                            if k != len(wfgenes_init.inputs[i][j]) - 1:
                                wfg_task_wrapper += '**' + wfgenes_init.inputs_locname[i][j][k] + ','
                            elif k == len(wfgenes_init.inputs[i][j]) - 1:
                                wfg_task_wrapper += '**' + wfgenes_init.inputs_locname[i][j][k] + '}'
                    wfg_task_wrapper += '\n\n\t#Dump Output from Merged Dictionaries #\n'
                    wfg_task_wrapper += "\tfile=open('" + wfgenes_init.outputs_locname[i][j][0] + ".yaml', 'w')\n"
                    wfg_task_wrapper += "\tyaml.dump(" + wfgenes_init.outputs_locname[i][j][0] + ", file, default_flow_style=False)\n"
                    wfg_task_wrapper += "\tfile.close()\n"
                    wfg_task_wrapper += "\t#End of subroutine #" + str(j + 1) + ' in routine # ' + str(i) + '\n'
            with open(wfgenes_init.wrapper_path, 'w') as file:
                file.write(wfg_task_wrapper) 


