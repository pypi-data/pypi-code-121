
""" wfGenes: Automatic workflow generator."""


__author__ = 'Mehdi Roozmeh'
__email__ = 'mehdi.roozmeh@kit.edu'
__copyright__ = 'Copyright 2020, Karlsruhe Institute of Technology'


import os
import os.path
import sys
from copy import deepcopy
from collections import OrderedDict
import argparse
import json
import yaml
import fireworks_schema
from wfgenes.core.initial_wfgenes import BasewfGenes




class FireworkwfGenes():
    """ Automatic Fireworks generation from wconfig file """
    def __init__(self, wfgenes_init):
        self.firework_generation(wfgenes_init)
        self.workflow_generation(wfgenes_init)

    def firework_generation(self, wfgenes_init):
        self.fws = []
        for i in range(wfgenes_init.routine_number):
            fw = {}
            fw['fw_id'] = i
            fw['name'] = wfgenes_init.routine_name[i]
            fw['spec'] = {}
            fw['spec']['_tasks'] = []
            fw['spec']['_category'] = {}
            fw['spec']['_category'] = 'batch'
            
            #fw['spec']['_category'].append('batch')
            output_subroutine_iter = iter(wfgenes_init.outputs_locname[i])
            input_subroutine_iter = iter(wfgenes_init.inputs_locname[i])
            kwargs_subroutine_iter = iter(wfgenes_init.kwargs[i])
            resource_subroutine_iter = iter(wfgenes_init.resource[i])
            subroutine_iter = iter(wfgenes_init.func[i])
            # iterate over the tasklist
            for j in range(wfgenes_init.subroutine_number[i]):
                task = {}
                subroutine = next(subroutine_iter)
                kwargs = next(kwargs_subroutine_iter)
                resource = next(resource_subroutine_iter)
                if subroutine[0] != 'BUILTIN' and len(subroutine) <= 2:
                    task['_fw_name'] = 'PyTask'
                    task['func'] = str(subroutine[0]) + \
                        '.' + str(subroutine[1])
                elif subroutine[0] == 'BUILTIN' and subroutine[1] == 'MERGE':
                    task['_fw_name'] = 'JoinDictTask'
                elif subroutine[0] == 'BUILTIN' and subroutine[1] == 'callscript':
                    task['_fw_name'] = 'ScriptTask'
                    task['script'] = str (kwargs['command'])
                    if 'arguments' in kwargs:
                        task['script'] = task['script'] + ' '+ str (kwargs['arguments'])

                if len(subroutine) > 2 :
                    task['_fw_name'] = 'ForeachTask'
                    task['split'] = []
                    task['task'] = {}
                    task['split'] = subroutine[3]
                    if subroutine[4] == 'full':
                        pass
                    else:
                        task['number of chunks'] = []    
                        task['number of chunks'] = int(subroutine[4])
                    task['task']['_fw_name'] = []
                    task['task']['_fw_name'] = 'PyTask'
                    task['task']['func'] = str(subroutine[0]) + \
                        '.' + str(subroutine[1])

                inputs = next(input_subroutine_iter)
                if inputs and inputs[0] != 'NULL':   
                    if len(subroutine) == 2: # Normal task
                        task['inputs'] = []
                        task['inputs'] = inputs
                    elif len(subroutine) > 2 : # Data-flow Task. E.g foreach
                        task['task']['inputs'] = []
                        task['task']['inputs'] = inputs
                
                
                if bool(kwargs) and subroutine[0] != 'BUILTIN' and subroutine[1] != 'callscript' and kwargs != 'null' :   # Check if the dictionary is not empty
                    task['kwargs'] = {}
                    task['kwargs'] = kwargs
                if bool(resource) and subroutine[0] != 'BUILTIN' and subroutine[1] != 'callscript' and resource != 'null' :
                    if 'kwargs' not in task:
                        task['kwargs'] = {}
                        task['kwargs'] = resource
                    else:    
                        task['kwargs'].update(resource)
                    

                output = next(output_subroutine_iter)
                if len(output) > 0 and output[0] != 'NULL':
                    if subroutine[0] != 'BUILTIN' and len(subroutine) <= 2 :
                        task['outputs'] = []
                        task['outputs'] = output
                    elif subroutine[1] == 'MERGE' and len(subroutine) <= 2:
                        task['output'] = []
                        task['output'] = output[0]
                    elif len(subroutine) > 2:
                        task['task']['outputs'] = output          
                fw['spec']['_tasks'].append(task)
                # end of tasklist iterator

            for j in range(wfgenes_init.subroutine_number[i]):
                for k in range(len(wfgenes_init.inputs[i][j])):
                    if (wfgenes_init.inputs_no_locdep[i][j][k][0] != 'inner_dependent' and
                        wfgenes_init.inputs_nodup[i][j][k] != 'duplicate' and
                            wfgenes_init.inputs_links[i][j][k][0].isnumeric() == False and 
                            wfgenes_init.inputs_nodup[i][j][k] != 'NULL'):
                        input_string = os.path.join(
                            wfgenes_init.args_inputpath, str(
                                wfgenes_init.inputs[i][j][k]) + '.yaml')
                        with open(input_string, 'r') as input_stream:
                            fw['spec'][wfgenes_init.inputs_locname[i][j]
                                    [k]] = yaml.safe_load(input_stream) 
            self.fws.append(fw)

    def workflow_generation(self, wfgenes_init):
        firework_path = os.path.join(wfgenes_init.workflow_path, 'FireWorks')
        if not os.path.exists(firework_path):
            os.makedirs(firework_path)

        links = {}
        links_dot = {}

        for M in range(wfgenes_init.routine_number):
            links[str(M)] = []
            links_dot[str(M)] = []
            for i in range(wfgenes_init.routine_number):
                for j in range(wfgenes_init.subroutine_number[i]):
                    for k in range(len(wfgenes_init.inputs_links[i][j])):
                        if isinstance(
                                wfgenes_init.inputs_links[i][j][k],
                                list) and wfgenes_init.inputs_links[i][j][k][0] == str(M):
                            links[str(M)].append(i)
            links_dot[str(M)] = links[str(M)]
            links[str(M)] = list(OrderedDict.fromkeys(links[str(M)]))
        metadata = {}
        metadata = wfgenes_init.metadata

        workflow = {'fws': self.fws, 'links': links, 'metadata': metadata,
                    'name': wfgenes_init.interface_dict['workflow_name'] + '_wfGenes'}

#        fireworks_schema.validate(workflow, 'Workflow')
        pad_path = os.path.join(firework_path,
                                wfgenes_init.interface_dict['workflow_name'] + '.yaml')
        with open(pad_path, 'w') as output_stream:
            yaml.dump(workflow, output_stream)        
