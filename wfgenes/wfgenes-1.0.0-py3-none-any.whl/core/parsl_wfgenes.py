
""" wfGenes: Automatic workflow generator."""


__author__ = 'Mehdi Roozmeh'
__email__ = 'mehdi.roozmeh@kit.edu'
__copyright__ = 'Copyright 2020, Karlsruhe Institute of Technology'

import os
import os.path
import sys
from copy import deepcopy
from collections import OrderedDict
import json
import yaml
from wfgenes.core.builtin_wfgenes import merge_dic
from wfgenes.core.initial_wfgenes import BasewfGenes

ROOT_DIR = os.path.dirname(os.path.abspath(__file__)) 
class ParslwfGenes():
    """Generate Python wrapper for wConfig nodes orignized to run parallel with DASK delayed decorators"""
    def __init__(self, wfgenes_init, args):
        self.parsl_generation(wfgenes_init, args)

    def parsl_generation(self, wfgenes_init, args):  
        self.wfg_parsl = ""
        self.indent="    " 
        lazy_str = 'parsl_'
        parsl_path = os.path.join(wfgenes_init.workflow_path, 'Parsl')
        if not os.path.exists(parsl_path):
            os.makedirs(parsl_path)
        self.wrapper_path = os.path.join(parsl_path,
        wfgenes_init.interface_dict['workflow_name'] + '_parsl.py')
        parsl_import_path = os.path.join(ROOT_DIR, 'parsl_import.cfg')
        parsl_import = open(parsl_import_path, 'r')
        self.wfg_parsl += parsl_import.read()
        self.wfg_parsl +='\n'
              
        for i in range(wfgenes_init.routine_number):
            for j in range(wfgenes_init.subroutine_number[i]):
                # Cache variables inside loop
                func_file = wfgenes_init.func[i][j][0]
                func_module = wfgenes_init.func[i][j][1]
                func_nodup  =  wfgenes_init.func_nodup[i][j][0]
                func_global_nodup= wfgenes_init.func_global_nodup[i][j][0] 
                if func_file != 'BUILTIN' and func_nodup != 'duplicate' and func_global_nodup != 'global_duplicate':
                    self.wfg_parsl += 'from ' + str(func_file) + ' import ' + str(func_module) + ' as __' + str(func_module) +'\n'
        
        for i in range(wfgenes_init.routine_number):
            for j in range(wfgenes_init.subroutine_number[i]):
                # Cache variables inside loop
                func_file = wfgenes_init.func[i][j][0]
                func_module = wfgenes_init.func[i][j][1]
                func_nodup  =  wfgenes_init.func_nodup[i][j][0]
                func_global_nodup= wfgenes_init.func_global_nodup[i][j][0] 
                if func_file != 'BUILTIN' and func_nodup != 'duplicate' and func_global_nodup != 'global_duplicate':
                    self.wfg_parsl += str(func_module) + ' = python_app(__' + str(func_module) + ')' +'\n'
        

        if args['embedded'] == False:
            executor_arg_parser_path = os.path.join(ROOT_DIR, 'executor_arg_parser.cfg')
            executor_arg_parser = open(executor_arg_parser_path, 'r')
            self.wfg_parsl += self.indent
            self.wfg_parsl += executor_arg_parser.read()
        else:
            pass

        if args['embedded'] == True:
            self.wfg_parsl += "\n" + "def main(**resource):\n\n"
            
        else:
            self.wfg_parsl += "\nif __name__ == '__main__':\n\n" 
            self.wfg_parsl += "\n"+self.indent+"resource = wfgenes_argparser(args)\n\n"
                        
        self.wfg_parsl += "\n"+ self.indent+"start_time = time.time()"

        parsl_config_path = os.path.join(ROOT_DIR, 'parsl_config.cfg')
        parsl_config = open(parsl_config_path, 'r')
        self.wfg_parsl += self.indent
        self.wfg_parsl += parsl_config.read()

        for i in range(wfgenes_init.routine_number):
            for j in range(wfgenes_init.subroutine_number[i]):
                # Cache variables inside loop j loop
                self.func_builtin = 'NORMALFUNCTION'
                func_file = wfgenes_init.func[i][j][0]
                func_module = wfgenes_init.func[i][j][1]
                split_array = 'NULL'  # The varaiable which FOREACH iterates over
                zip_inputs = []
                if len(wfgenes_init.func[i][j]) > 2:
                    if wfgenes_init.func[i][j][2] == 'FOREACH':
                        self.func_builtin = 'FOREACH'
                        split_array = wfgenes_init.func[i][j][3]
                        chunk_size = str(wfgenes_init.func[i][j][4])
                        index_split = ''
                        
                        if len(wfgenes_init.func[i][j]) > 5:
                            for elements in wfgenes_init.func[i][j][5]['zip_inputs']:
                                zip_inputs.append(elements)    
                        
                        len_inputs = len(wfgenes_init.inputs[i][j])
                        for k in range(len_inputs):
                            if wfgenes_init.inputs[i][j][k] == split_array and self.func_builtin == 'FOREACH':
                                index_split = wfgenes_init.inputs_links[i][j][k][2]
                        
                func_global_nodup_0= wfgenes_init.func_global_nodup[i][j][0]
                len_inputs = len(wfgenes_init.inputs[i][j])
                len_outputs=len(wfgenes_init.outputs[i][j])
                for k in range(len_inputs):
                    # Cache variables inside loop k loop
                    input_k = wfgenes_init.inputs[i][j][k]
                    inputs_nodup_k = wfgenes_init.inputs_nodup[i][j][k]
                    inputs_global_nodup_k = wfgenes_init.inputs_global_nodup[i][j][k]
                    inputs_no_locdep_k = wfgenes_init.inputs_no_locdep[i][j][k][0]
                    input_gdependent = wfgenes_init.inputs_links[i][j][k][0].isnumeric()
                          
                    if inputs_global_nodup_k != 'global_duplicate' and inputs_nodup_k!= 'duplicate' and inputs_no_locdep_k!= 'inner_dependent' and input_gdependent == False:
                        # Load wfgenes_init.inputs
                        self.wfg_parsl += '\n'+ self.indent +'#Read Input #' + str(k + 1)  + 'from subroutine #' + str(j + 1) + ' in routine #' + str(i) + '\n'
                        self.wfg_parsl += self.indent+"yaml_stream = open('" + input_k  + ".yaml', 'r')\n"
                        self.wfg_parsl += self.indent + input_k  + " = yaml.load(yaml_stream, Loader=yaml.Loader)\n\n"
        self.wfg_parsl += "\n"+ self.indent+"end_memtime = time.time()"
                            
        # Start of computation phase                    
        
        func_done = []
        step_simulation = 1
        wfgenes_init.wfgenes_scheduler(func_done)
        previously_computed = [] # Keep track of launched task to avoid repeated computation
        steps_width = []
        while wfgenes_init.func_waiting == True:        
            self.wfg_parsl += '\n\n'+self.indent+'#### Start Step #'+ str(step_simulation)
            width_counter = 0
            for i in range(wfgenes_init.routine_number):
                for j in range(wfgenes_init.subroutine_number[i]):
                    # Cache variables inside loop j loop
                    self.func_builtin = ''
                    func_file = wfgenes_init.func[i][j][0]
                    self.func_module = wfgenes_init.func[i][j][1]                             
                    func_global_nodup_0= wfgenes_init.func_global_nodup[i][j][0]
                    len_inputs = len(wfgenes_init.inputs[i][j])
                    len_outputs=len(wfgenes_init.outputs[i][j])
        
                    if wfgenes_init.foreach_output[i][j][0] != 'null':
                        # Dependent foreach
                        output_number =  len(wfgenes_init.outputs[wfgenes_init.foreach_output[i][j][1]][wfgenes_init.foreach_output[i][j][2]])

                    elif wfgenes_init.foreach_output[i][j][1] == 'null':
                        # independent foreach
                        output_number = len_outputs



                    if func_global_nodup_0 == 'global_duplicate': 
                        func_suffix = '_id' + str(i)
                    else:
                        func_suffix = ''     
                    self.split_array = 'NULL'  # The varaiable which FOREACH iterates over
                    self.zip_inputs = []
                    coordinate = [[i,j]]  # Routine and subroutine indexes
                    if len(wfgenes_init.func[i][j]) > 2:
                        if wfgenes_init.func[i][j][2] == 'FOREACH':
                            self.func_builtin = 'FOREACH'
                            self.split_array = wfgenes_init.func[i][j][3]
                            self.chunk_size = str(wfgenes_init.func[i][j][4])
                            self.index_split = ''
                            
                            if len(wfgenes_init.func[i][j]) > 5:
                                for elements in wfgenes_init.func[i][j][5]['zip_inputs']:
                                    self.zip_inputs.append(elements)    
                            
                            for k in range(len_inputs):
                                if wfgenes_init.inputs[i][j][k] == self.split_array and self.func_builtin == 'FOREACH':
                                    self.index_split = wfgenes_init.inputs_links[i][j][k][2]
                            
                            if self.chunk_size == 'full' and wfgenes_init.foreach_output[i][j][0] == 'null' :
                                self.chunk_size = 'len('+self.split_array+')'
                                self.step= '1'
                            elif self.chunk_size == 'full' and wfgenes_init.foreach_output[i][j][0] != 'null' :
                                self.chunk_size = 'len('+ lazy_str + wfgenes_init.foreach_output[i][j][0]+')'
                                self.step= '1'
                            elif self.chunk_size != 'full' and wfgenes_init.foreach_output[i][j][0] == 'null' :   
                                self.step= ' int(len('+self.split_array+')/'+self.chunk_size+')'
                            elif self.chunk_size != 'full' and wfgenes_init.foreach_output[i][j][0] != 'null' :
                                if output_number > 1:
                                    self.step = ' int(len('+ lazy_str +wfgenes_init.foreach_output[i][j][0]+'['+ self.index_split +'])/'+self.chunk_size+')'
                                elif output_number == 1:
                                    self.step = ' int(len('+ lazy_str +wfgenes_init.foreach_output[i][j][0]+')/'+self.chunk_size+')'


                            if wfgenes_init.foreach_output[i][j][0] == 'null':
                                foreach_len = 'range(0 , len('+self.split_array+'),'+self.step+')'
                            elif wfgenes_init.foreach_output[i][j][0] != 'null':
                                if output_number > 1:
                                    foreach_len = 'range(0, len('+ lazy_str +wfgenes_init.foreach_output[i][j][0]+'['+ self.index_split +'])'+','+self.step+ ')'         
                                elif output_number == 1:
                                    foreach_len = 'range(0, len('+ lazy_str +wfgenes_init.foreach_output[i][j][0]+')'+','+self.step+ ')'

                    if len(wfgenes_init.func_depid[i][j]) == 1 and coordinate[0] not in func_done:
                        if  self.func_module != 'MERGE':
                            wfgenes_init.func[i][j][1] = wfgenes_init.func[i][j][1] + func_suffix
                        # check if func is Ready and not computed already 
                        self.wfg_parsl += '\n'+self.indent+'# Call subroutine #' + str(j + 1) + ' from routine #' +str(i)+ '\n'
                        self.wfg_parsl += self.indent    
                    # Call functions
                        if self.func_module != 'MERGE' and self.func_builtin != 'FOREACH':
                            self.wfg_parsl += '\n'+self.indent+lazy_str+self.func_module+ func_suffix + ' = ' + self.func_module + '('
                            func_done.append([i ,j]) # Append implemented module
                            width_counter +=1
                            func_waiting = False     # Temporarily Set func_waiting  to False 
                            input_slice = ''   
                        elif self.func_module == 'MERGE' and self.func_builtin != 'FOREACH':
                            self.wfg_parsl += '\n'+self.indent +lazy_str+ wfgenes_init.outputs[i][j][0] + ' = ' +self.func_module+'('
                            func_done.append([i ,j]) # Append implemented module
                            width_counter +=1
                            func_waiting = False     # Temporarily Set func_waiting  to False 
                            input_slice = ''
                        elif self.func_builtin == 'FOREACH':
                            # foreach implementation part 1/2 
                            self.wfg_parsl += '\n'+self.indent+lazy_str+self.func_module+func_suffix+'= []'
                            self.wfg_parsl += '\n'+self.indent+lazy_str+self.func_module+func_suffix+'_future= []'
                            for k in range(len(wfgenes_init.foreach_output[i][j])):
                                if wfgenes_init.foreach_output[i][j][0] != 'null' and len(wfgenes_init.func[wfgenes_init.foreach_output[i][j][1]][wfgenes_init.foreach_output[i][j][2]]) == 2: 
                                    # Check if foreach computation depends on a lazy object
                                    compute_now = wfgenes_init.foreach_output[i][j][0] + func_suffix
                                    if compute_now not in previously_computed:
                                        previously_computed.append(compute_now) # Append computed lazy task- Avoid extra computation 
                                        self.wfg_parsl += '\n'+self.indent+lazy_str + compute_now+  '='+ lazy_str + compute_now+ '.result()' # Compute lazy objects   
                            self.wfg_parsl += '\n'+self.indent + 'for i in ' + foreach_len + ' :'
                            self.wfg_parsl += '\n'+self.indent+self.indent+lazy_str+self.func_module+func_suffix+ '_foreach=' +self.func_module + '('
                            # end of foreach implementation part 1/2
                        self.write_arguments(wfgenes_init, lazy_str, i, j)  # write argument list                                  
                        if self.func_builtin == 'FOREACH': # foreach implementation Part 2/2
                            self.wfg_parsl += '\n'+self.indent+self.indent+lazy_str+self.func_module+func_suffix+'_future.append('+lazy_str+self.func_module+func_suffix+'_foreach)'
                            previously_computed.append(self.func_module)
                            self.wfg_parsl += '\n'+self.indent + 'for i in range(len('+lazy_str+self.func_module+func_suffix+'_future)):'
                            self.wfg_parsl += '\n'+self.indent + self.indent+lazy_str+self.func_module+func_suffix+'.append('+lazy_str+self.func_module+func_suffix+'_future[i].result())'
                            if len(wfgenes_init.outputs[i][j]) > 1:
                                self.wfg_parsl += '\n'+self.indent+lazy_str + self.func_module + func_suffix + '= flat_tuple( '+ lazy_str + self.func_module + func_suffix + ', ' + str(len(wfgenes_init.outputs[i][j])) +')'
                            elif len(wfgenes_init.outputs[i][j]) == 1:    
                                self.wfg_parsl += '\n'+self.indent+lazy_str + self.func_module + func_suffix +  '= flat_list( '+ lazy_str + self.func_module + func_suffix + ')'
                            func_done.append([i ,j]) ## Append implemented module
                            width_counter +=1
            self.wfg_parsl += '\n'+self.indent+'#End of step ' + str(step_simulation) + ' with the width ' + str(width_counter)
            step_simulation = step_simulation + 1
            steps_width.append(width_counter)
            wfgenes_init.wfgenes_scheduler(func_done)

        if wfgenes_init.func[func_done[-1][0]][func_done[-1][1]][1] != 'MERGE':
            self.wfg_parsl += '\n'+self.indent+'print('+lazy_str+wfgenes_init.func[func_done[-1][0]][func_done[-1][1]][1]+'.result())'
        else:
            self.wfg_parsl += '\n'+self.indent+'print('+lazy_str+wfgenes_init.outputs[func_done[-1][0]][func_done[-1][1]][0]+ func_suffix+'.result())'                
        self.wfg_parsl += "\n"+ self.indent+"end_time = time.time()"
        self.wfg_parsl += "\n"+ self.indent+"total_time = end_time - start_time"
        self.wfg_parsl += "\n"+ self.indent+"total_memtime = end_memtime - start_time"
        self.wfg_parsl += "\n"+ self.indent+"print(' The total time is' , round(total_time, 2), 'seconds')"
        self.wfg_parsl += "\n"+ self.indent+"print(' The total memory load time is' , round(total_memtime, 2), 'seconds')"
        self.wfg_parsl += "\n"+self.indent+"print('PARSL based workflow')"
        self.wfg_parsl += "\n"+ self.indent + "#The model has "+ str(len(steps_width)) + " step with the width of "    
        for step in steps_width:
            self.wfg_parsl += str(step) + ", "
        with open(self.wrapper_path, 'w') as file:
                file.write(self.wfg_parsl)
        cmd = 'autopep8 --in-place --aggressive --aggressive '+ self.wrapper_path      
        os.system(cmd)                 



    
    def write_arguments(self, wfgenes_init, lazy_str, i , j):
        """ Writing argument list for a module call"""
        len_inputs = len(wfgenes_init.inputs[i][j])
        if bool(wfgenes_init.kwargs[i][j]) and wfgenes_init.kwargs[i][j] != 'null':
            kwargs = wfgenes_init.kwargs[i][j]
            last_key = list(kwargs)[-1]
            kwargs_string = ''
            for key, value in kwargs.items():
                kwargs_string +=  key + " = '" + str(value) + "'"      
                if key != last_key:
                    kwargs_string += ', '
                else:
                    kwargs_string += ')'
        for k in range(len_inputs):
            # Writing arguments of each function
            # Cache variables inside loop k loop
            inputs = wfgenes_init.inputs_py[i][j][k]
            inputs_nodup_k= wfgenes_init.inputs_nodup[i][j][k]
            inputs_no_locdep_k= wfgenes_init.inputs_no_locdep[i][j][k][0]
            if len(wfgenes_init.inputs_links[i][j][k]) == 3:
                input_gdependent = wfgenes_init.inputs_links[i][j][k][0].isnumeric()
            else:
                input_gdependent = False    
            argument_key = ''
            func_gloab = ''
            func_loc = ''
            func_loc_dep = ''
            func_gloab_dep = ''
            parsl_barrier = ''
            slice = '' # Slice only will be set for FOREACH method       
            if self.func_module == 'MERGE':
                argument_key = wfgenes_init.inputs_locname[i][j][k]+'=' # This prefix is set only for merge function
            
            if len(wfgenes_init.func[i][j]) > 2:
                if wfgenes_init.func[i][j][2] == 'FOREACH':
                    if inputs == self.split_array or inputs in self.zip_inputs:
                        slice = '[i:i+'+self.step+']'    
            if inputs_no_locdep_k== 'inner_dependent':
                input_index = wfgenes_init.inputs_no_locdep[i][j][k][2]
                func_loc = wfgenes_init.func[i][int(wfgenes_init.inputs_no_locdep[i][j][k][1])][1]
                func_loc_dep = func_loc 
                output_number = len(wfgenes_init.outputs[i][int(wfgenes_init.inputs_no_locdep[i][j][k][1])])
                if self.func_builtin == 'FOREACH' and inputs == self.split_array :
                    # Rewrite the value if it is split array
                    func_loc_dep = wfgenes_init.foreach_output[i][j][0]
                if self.func_builtin != 'FOREACH':
                    parsl_barrier = '.result()' 
                
            if input_gdependent == True:
                input_index = wfgenes_init.inputs_links[i][j][k][2]          
                func_gloab = wfgenes_init.func[int(wfgenes_init.inputs_links[i][j][k][0])][int(wfgenes_init.inputs_links[i][j][k][1])][1]
                func_gloab_dep = func_gloab 
                output_number= len(wfgenes_init.outputs[int(wfgenes_init.inputs_links[i][j][k][0])][int(wfgenes_init.inputs_links[i][j][k][1])])
                if self.func_builtin == 'FOREACH' and inputs == self.split_array :
                    # Rewrite the value if it is split arry
                    parsl_barrier = '' 
                    func_gloab_dep = wfgenes_init.foreach_output[i][j][0]
                elif self.func_builtin != 'FOREACH':
                    parsl_barrier = '.result()' 
                    

            # Writing arguments - 4 different scenarios
            if inputs_no_locdep_k != 'inner_dependent' and input_gdependent == False :
                #1 No dependency at all
                self.wfg_parsl += argument_key+ inputs  + parsl_barrier+slice+', '   
            elif inputs_no_locdep_k== 'inner_dependent' and func_loc != 'MERGE' :
                #2 Inner-dependent for users function
                self.wfg_parsl += argument_key+lazy_str + func_loc_dep  
                if output_number > 1:
                    self.wfg_parsl += parsl_barrier+'[' + input_index + '] ' + slice + ', '
                elif output_number == 1:
                    self.wfg_parsl += slice + ', '
            elif input_gdependent == True and func_gloab != 'MERGE' :
                #3 Gloab dependent for users function
                self.wfg_parsl += argument_key+lazy_str + func_gloab_dep  
                if output_number != 1:
                    self.wfg_parsl += parsl_barrier+'[' + input_index + ']'  + slice + ', '
                else:
                    self.wfg_parsl += slice + ', '
                        
            elif (func_loc == 'MERGE' or func_gloab == 'MERGE') and (input_gdependent == True or inputs_no_locdep_k== 'inner_dependent')  :
                #4 Dependent to Merge function
                    self.wfg_parsl += argument_key+lazy_str + inputs + ', '    
         
        if not bool(wfgenes_init.kwargs[i][j]) or wfgenes_init.kwargs[i][j] == 'null' : 
            if len_inputs !=0:
                self.wfg_parsl = self.wfg_parsl[:-2]
            self.wfg_parsl += ')'                 
        elif bool(wfgenes_init.kwargs[i][j]) and wfgenes_init.kwargs[i][j] != 'null' :
            self.wfg_parsl += kwargs_string

        

   
                            
                                
                                            
                    
                                    
                                        
                      

                                                                   
                   


                