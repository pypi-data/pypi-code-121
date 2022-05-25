
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
import jsonschema
from jsonschema import validate
ROOT_DIR = os.path.dirname(os.path.abspath(__file__)) 

class BasewfGenes():
    """ Perform array initialization and data-flow analysis """
    def __init__(self, blueargs):
        self.args_workflowconfig = blueargs['workflowconfig']
        self.args_inputpath = blueargs['inputpath']
        self.args_wms = blueargs['wms']
        self.previous_stamp = os.stat(self.args_workflowconfig).st_mtime
        # List declaration
        schema_path = os.path.join(ROOT_DIR, 'wconfig_schema.json')
        with open(self.args_workflowconfig) as input_stream:
            schema = json.load(open(schema_path))
            config_name_split = self.args_workflowconfig.split('.')
            num_dot = len(config_name_split) - 1
            if config_name_split[num_dot] == 'yaml' or config_name_split[num_dot] == 'yml':
                self.interface_dict = yaml.load(input_stream, Loader=yaml.Loader)
                validate(self.interface_dict , schema=schema)
            elif config_name_split[num_dot] == 'json':
                self.interface_dict = json.load(input_stream)
                validate(self.interface_dict , schema=schema)
              
            for k, v in self.interface_dict.items():
                if k == 'nodes':
                    routine_interface = deepcopy(v)
            
            if 'metadata' in self.interface_dict: 
                self.metadata = self.interface_dict['metadata']
            else: 
                self.metadata = {'type of generation': 'By wfGenes'}
            self.routine_number = len(self.interface_dict['nodes'])
            self.subroutine_number = [0 for y in range(self.routine_number)]
            self.routine_name = [0 for y in range(self.routine_number)]
            self.routine_dir = [0 for y in range(self.routine_number)]
            self.routine_gdep = [0 for y in range(self.routine_number)]
            for i in range(self.routine_number):
                self.subroutine_number[i] = len(routine_interface[i]['tasks'])
            self.func = [['null' for x in range(self.subroutine_number[y])]
                        for y in range(self.routine_number)]
            self.func_nodup = [['null' for x in range(self.subroutine_number[y])]
                                    for y in range(self.routine_number)]
            self.func_global_nodup = [['null' for x in range(self.subroutine_number[y])]
                                    for y in range(self.routine_number)]
            self.func_no_locdep = [['null' for x in range(self.subroutine_number[y])]
                                for y in range(self.routine_number)]        
            self.func_depid = [['null' for x in range(self.subroutine_number[y])]
                                for y in range(self.routine_number)]
            self.func_localdepid = [['null' for x in range(self.subroutine_number[y])]
                                for y in range(self.routine_number)]                    
            self.inputs = [['null' for x in range(self.subroutine_number[y])]
                        for y in range(self.routine_number)]

            self.inputs_py = [[0 for x in range(self.subroutine_number[y])]
                        for y in range(self.routine_number)]

            self.inputs_nodup = [['null' for x in range(self.subroutine_number[y])]
                                    for y in range(self.routine_number)]
            self.inputs_no_locdep = [['null' for x in range(self.subroutine_number[y])]
                                        for y in range(self.routine_number)]
            self.inputs_locname = [['null' for x in range(self.subroutine_number[y])]
                                    for y in range(self.routine_number)]
            self.inputs_links = [['null' for x in range(self.subroutine_number[y])]
                                for y in range(self.routine_number)]
            
            self.inputs_global_nodup = [['null' for x in range(self.subroutine_number[y])]
                                for y in range(self.routine_number)]

            self.outputs = [['null' for x in range(self.subroutine_number[y])]
                            for y in range(self.routine_number)]
            self.outputs_py = [['null' for x in range(self.subroutine_number[y])]
                            for y in range(self.routine_number)]

            self.outputs_nodup = [['null' for x in range(self.subroutine_number[y])]
                                        for y in range(self.routine_number)]
            self.outputs_no_locdep = [['null' for x in range(self.subroutine_number[y])]
                                        for y in range(self.routine_number)]
            self.outputs_locname = [['null' for x in range(self.subroutine_number[y])]
                                    for y in range(self.routine_number)]
            self.foreach_output = [[['null' for k in range(3)] for x in range(self.subroutine_number[y])]
                                    for y in range(self.routine_number)]
            self.kwargs = [['null' for x in range(self.subroutine_number[y])]
                    for y in range(self.routine_number)]
            self.kwargs_nodup = [['null' for x in range(self.subroutine_number[y])]
                                for y in range(self.routine_number)]

            self.resource = [['null' for x in range(self.subroutine_number[y])]
                    for y in range(self.routine_number)]                    
            
            self.firstround_scheduling = True                  

                               

            # Start of yaml parser
            for i in range(self.routine_number):
                for j in range(len(routine_interface[i]['tasks'])):
                    if 'func' in  routine_interface[i]['tasks'][j]:
                        self.func[i][j] = deepcopy(
                            routine_interface[i]['tasks'][j]['func'])
                    elif 'script' in  routine_interface[i]['tasks'][j]:
                        self.func[i][j] = 'ScriptTask'
            for i in range(self.routine_number):
                for j in range(len(routine_interface[i]['tasks'])):
                    self.func_nodup[i][j] = deepcopy(self.func[i][j])
                    self.func_global_nodup[i][j]= deepcopy(self.func[i][j])
                    self.func_no_locdep[i][j]= deepcopy(self.func[i][j])
                    #self.func_depid[i][j]= deepcopy(routine_interface[i]['tasks'][j]['func'][1])  
                self.func_nodup[i][:] = self.extractlist(self.func_nodup[i][:])
                self.func_global_nodup[i][:] = self.extractlist(self.func_global_nodup[i][:])
                self.func_depid[i][:] = self.extractlist(self.func_depid[i][:])
                self.func_localdepid[i][:] = self.extractlist(self.func_localdepid[i][:])
                self.func_no_locdep[i][:] = self.extractlist(self.func_no_locdep[i][:])

            for i in range(self.routine_number):
                self.func_nodup[i][:] = self.duplicate_finder(
                    self.func_nodup[i][:])

            for i in range(self.routine_number):
                for j in range(len(routine_interface[i]['tasks'])):
                    if 'inputs' in routine_interface[i]['tasks'][j]:
                        self.inputs[i][j] = deepcopy(
                            routine_interface[i]['tasks'][j]['inputs'])
                        self.inputs_py[i][j] = deepcopy(
                            routine_interface[i]['tasks'][j]['inputs'])
                    elif 'inputs' not in routine_interface[i]['tasks'][j]:       
                        self.inputs[i][j] = ['NULL']
                        self.inputs_py[i][j] = ['NULL']
            self.pylist(self.inputs_py)      

            for i in range(self.routine_number):
                for j in range(len(routine_interface[i]['tasks'])):
                    self.inputs_nodup[i][j] = deepcopy( self.inputs_py[i][j])
                    self.inputs_global_nodup[i][j] =  deepcopy( self.inputs_py[i][j]) 
                    self.inputs_no_locdep[i][j] =  deepcopy( self.inputs_py[i][j])
                    self.inputs_links[i][j] =  deepcopy( self.inputs_py[i][j])
                    self.inputs_locname[i][j] =  deepcopy( self.inputs_py[i][j])
                    
            for i in range(self.routine_number):
                self.inputs_nodup[i][:] = self.duplicate_finder(
                    self.inputs_nodup[i][:])

            for i in range(self.routine_number):
                for j in range(len(routine_interface[i]['tasks'])):
                    if 'outputs' in routine_interface[i]['tasks'][j]:
                        self.outputs[i][j] = deepcopy(
                            routine_interface[i]['tasks'][j]['outputs'])
                        self.outputs_py[i][j] = deepcopy(
                            routine_interface[i]['tasks'][j]['outputs'])
                    elif 'outputs' not in routine_interface[i]['tasks'][j]:
                        self.outputs[i][j] = ['NULL']
                        self.outputs_py[i][j] = ['NULL']


            self.pylist(self.outputs_py)
            for i in range(self.routine_number):
                for j in range(len(routine_interface[i]['tasks'])):
                    self.outputs_nodup[i][j] = deepcopy(self.outputs_py[i][j])
                    self.outputs_locname[i][j] = deepcopy(self.outputs_py[i][j])         
            for i in range(self.routine_number):
                self.outputs_nodup[i][:] = self.duplicate_finder(
                    self.outputs_nodup[i][:])      

            for i in range(self.routine_number):
                for j in range(len(routine_interface[i]['tasks'])):
                    for k in range(len(self.inputs_locname[i][j])):
                        self.inputs_locname[i][j][k] = self.inputs_locname[i][j][k].rsplit('_id', 1)[
                            0]

            for i in range(self.routine_number):
                for j in range(len(routine_interface[i]['tasks'])):
                    for k in range(len(self.outputs_locname[i][j])):
                        self.outputs_locname[i][j][k] = self.outputs_locname[i][j][k].rsplit('_id', 1)[
                            0]

            for i in range(self.routine_number):
                for j in range(len(routine_interface[i]['tasks'])):
                    if 'kwargs' in routine_interface[i]['tasks'][j]:
                        self.kwargs[i][j] = deepcopy(routine_interface[i]['tasks'][j]['kwargs'])
                        self.kwargs_nodup[i][j] = deepcopy(
                            routine_interface[i]['tasks'][j]['kwargs'])

            
            for i in range(self.routine_number):
                for j in range(len(routine_interface[i]['tasks'])):
                    if 'resource' in routine_interface[i]['tasks'][j]:
                        self.resource[i][j] = deepcopy(routine_interface[i]['tasks'][j]['resource'])


          

            for i in range(self.routine_number):
                self.routine_name[i] = routine_interface[i]['name']
                self.routine_dir[i] = routine_interface[i]['name']
            self.pyvar(self.routine_dir)    


            for i in range(self.routine_number):
                self.inputs_no_locdep[i], self.func_no_locdep[i][:] = self.dependency_check(
                    self.inputs_no_locdep[i][:], self.outputs_py[i][:], i, self.func_localdepid[i][:])
                self.inputs_links[i], self.func_depid[i][:]  = self.dependency_check(
                    self.inputs_links[i][:], self.outputs_py[i][:], i, self.func_depid[i][:])
                        
            # Global dependency analysis
            for i in range(self.routine_number):
                for j in range(self.routine_number):
                    if i != j:
                        self.inputs_links[i][:], self.func_depid[i][:], self.routine_gdep[i] = self.link_check(
                            self.inputs_links[i][:], self.inputs_no_locdep[i][:], self.outputs_py[j][:], j, self.func_depid[i][:], self.routine_gdep[i])
                        
            for i in range(self.routine_number):
                for j in range(i+1, self.routine_number):
                    # Functions and input name dunplication is not allowed- Should be validate with schema            
                    self.func_global_nodup[i][:] = self.global_duplication_check(self.func_global_nodup[i][:], self.func_global_nodup[j][:])
                    self.inputs_global_nodup[i][:] = self.global_duplication_check(self.inputs_global_nodup[i][:], self.inputs_global_nodup[j][:])
                    
            self.foreach_dependency()
            self.link_generation()


            self.interface_dict['workflow_name'] = self.interface_dict['workflow_name'].replace(" ","_")
            wf_name_split = self.interface_dict['workflow_name'].split('.')
            last_dot_index = len(wf_name_split) - 1
            if last_dot_index > 0:
                self.interface_dict['workflow_name'] = wf_name_split[0] 
            self.workflow_path = os.path.join(
                os.path.dirname(os.path.abspath(self.args_workflowconfig)),
                'wfGenes_output',
                self.interface_dict['workflow_name'])

            if not os.path.exists(self.workflow_path):
                os.makedirs(self.workflow_path)

    def extractlist(self, lst):
        """ Return list of the list """
        return [[el] for el in lst]
            
    def pylist(self, input_py):
        """ Replace ' ' with '_' to be used for python wrappers """
        map_list = [[" ", "_"], ["*", "star"]]
        for couple in map_list:
            for i in range(len(input_py)):
                for j in range(len(input_py[i])):
                    for k in range(len(input_py[i][j])):
                        input_py[i][j][k] = input_py[i][j][k].replace(couple[0], couple[1])
    def pyvar(self, input_py):
        """ Replace ' ' with '_' to be used for python wrappers """
        map_list = [[" ", "_"], ["*", "star"]]
        for couple in map_list:
            for i in range(len(input_py)):
                input_py[i]= input_py[i].replace(couple[0], couple[1])

    def foreach_dependency(self):  
        """ Check dependency for split variable in foreach task """
        for i in range(self.routine_number):
            for j in range(self.subroutine_number[i]):                                    
                if len(self.func[i][j]) > 2:
                    if self.func[i][j][2] == 'FOREACH':
                        for k in range(self.routine_number):
                            if k != i:
                                for m in range(self.subroutine_number[k]):
                                    if self.func[i][j][3] in self.outputs[k][m]:
                                        # Iterable variable for dpendent foreach
                                        self.foreach_output[i][j] =  [self.func[k][m][1] , k , m]
                                            
    def duplicate_finder(self, target_list):
        """ Detect duplicates in multidimensional list  """
        for y in range(len(target_list)):
            for x in range(len(target_list[y])):
                for i in range(y, len(target_list) - 1):
                    for j in range(len(target_list[i + 1])):
                        if target_list[y][x] != target_list[i + 1][j]:
                            pass
                        else:
                            target_list[i + 1][j] = 'duplicate'
        return target_list

    def dependency_check(self, input_list, output_list, id, func):
        """ Check dependency between different subroutine in one routine """
        for y in range(len(input_list) - 1, -1, -1):
            for x in range(len(input_list[y])):
                for j in range(len(output_list) - 1):
                    for k in range(len(output_list[j])):
                        if input_list[y][x] != output_list[j][k]:
                            pass
                        else:
                            input_list[y][x] = ['inner_dependent', str(j) , str(k)]
                            func[y].append([id , j])
        return input_list, func

    def link_check(self, input_link, input_list, output_list, id, func, routine):
        """ Check dependency between different routines"""
        for y in range(len(input_list) - 1, -1, -1):
            for x in range(len(input_list[y])):
                for j in range(len(output_list) - 1, -1, -1):
                    for k in range(len(output_list[j])):
                        if input_list[y][x] != output_list[j][k]:
                            pass
                        else:
                            input_link[y][x] = [str(id), str(j) , str(k)]
                            func[y].append([id, j])
                            routine = True
        return input_link, func, routine

    def global_duplication_check(self, input_list, output_list):
        """ Check for duplication between diffrent nodes """
        for y in range(len(input_list) - 1, -1, -1):
            for x in range(len(input_list[y])):
                for i in range(len(output_list)):
                    for j in range(len(output_list[i])):
                        if input_list[y][x] != output_list[i][j]:
                            pass
                        else:
                            output_list[i][j] = 'global_duplicate'
        return input_list    

    def wfgenes_scheduler(self, done_func):
        """ Update dependency list to choose ready function(s)"""
        self.func_waiting = False
        for routine in self.func_depid :
            for subroutine in routine:
                for routine_name in subroutine:
                    if routine_name != 'null' or self.firstround_scheduling == True:
                        self.func_waiting= True
                        if self.firstround_scheduling == True:
                            self.firstround_scheduling = False
                        break
        for func in done_func:
            for i in range(self.routine_number):
                for j in range(self.subroutine_number[i]):
                    while func in self.func_depid[i][j]: 
                        self.func_depid[i][j].remove(func) 
                        # Remove implemented function from func_depid

    
    def wconfig_checker(self, args= 'none'):
        """ Check if wconfig is verified by user to proceed to code generation """
        modeling = 'default' #
        input_stream = open(self.args_workflowconfig, 'r')
        config_name_split = self.args_workflowconfig.split('.')
        if config_name_split[1] == 'yaml':
            interface_dict = yaml.load(input_stream, Loader=yaml.Loader)
        elif config_name_split[1] == 'json':
            interface_dict = json.load(input_stream)

        wf_name_split = self.interface_dict['workflow_name'].split('.')
        last_dot_index = len(wf_name_split) - 1
        
        if last_dot_index > 0:
            if wf_name_split[last_dot_index] == 'active':
                modeling = 'active'
                self.interface_dict['workflow_name'] = wf_name_split[0]    

            elif wf_name_split[last_dot_index] == 'done':
                modeling = 'done'
                self.interface_dict['workflow_name'] = wf_name_split[0]    
            else :
                modeling = 'default'
                self.interface_dict['workflow_name'] = wf_name_split[0]

        wf_path = os.path.join(os.path.dirname(os.path.abspath(self.args_workflowconfig)),
                'wfGenes_output',
                self.interface_dict['workflow_name'])

        if args == 'clean':
            if os.path.exists(wf_path):
                shutil.rmtree(wf_path)

        
        stamp = os.stat(self.args_workflowconfig).st_mtime
        if stamp != self.previous_stamp:
            self.previous_stamp = stamp
            wconfig_stat = 'modified'
        else:
            wconfig_stat = 'unchanged'    

        return modeling, wf_path, wconfig_stat

    def link_generation(self):
        self.links = {}
        for M in range(self.routine_number):
            self.links[str(M)] = []
            for i in range(self.routine_number):
                for j in range(self.subroutine_number[i]):
                    for k in range(len(self.inputs_links[i][j])):
                        if isinstance(
                                self.inputs_links[i][j][k],
                                list) and self.inputs_links[i][j][k][0] == str(M):
                            self.links[str(M)].append(i)             
            self.links[str(M)] = list(OrderedDict.fromkeys(self.links[str(M)]))

               
                                
        