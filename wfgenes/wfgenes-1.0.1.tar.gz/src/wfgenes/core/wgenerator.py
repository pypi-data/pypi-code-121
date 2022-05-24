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
import xmlschema
import yaml
import fireworks_schema
from wfgenes.core.initial_wfgenes import BasewfGenes
from wfgenes.core.pywrapper_wfgenes import PywrapperwfGens
from wfgenes.core.simstack_wfgenes import SimstackwfGenes
from wfgenes.core.fireworks_wfgenes import FireworkwfGenes
from wfgenes.core.dot_wfgenes import DotwfGenes
from wfgenes.core.clean_wfgenes import CleanwfGenes
from wfgenes.core.dask_wfgenes import DaskwfGenes
from wfgenes.core.parsl_wfgenes import ParslwfGenes
import time
import signal
import jsonschema
from jsonschema import validate
import subprocess



def keyboardInterruptHandler(signal, frame):
    print("KeyboardInterrupt (ID: {}) has been caught. Cleaning up...".format(signal))
    exit(0)

def wconfig_validator(BasewfGenes, args, wconfig ):
    last_error = ''
    verified = 'null'
    i = 'null'
    #time.sleep(1) # Avoid extra cpu load
    try:
        wfgenes_init = BasewfGenes(args)
        verified = True
        i = 'recent_verified'
        return wfgenes_init , verified, i
    except jsonschema.ValidationError as e:
        if e.message != last_error:
            last_error = e.message
            print(e.instance)
            print (last_error)
            verified = False
            print('Press ctrl+c to exit or modify ' + wconfig)
            return 'not_verified' , verified, i


def modified(wconfig, wconfig_stat):
    if wconfig_stat[0] == 'null' and wconfig_stat[1] == 'null':
        wconfig_stat[1] = os.stat(wconfig).st_mtime
        wconfig_stat[0] = wconfig_stat[1]
        return True        
    elif wconfig_stat[0] == wconfig_stat[1]:
        wconfig_stat[1] = os.stat(wconfig).st_mtime
        return False
    else:
        wconfig_stat[0] = wconfig_stat[1]
        return True
    
def glue_args(*blueargs):
    argdic = {"workflowconfig": "", "inputpath":"", "outputpath":"", "wms":""}
    if bool(blueargs) == False:      
        parser = argparse.ArgumentParser()
        parser.add_argument(
            '--workflowconfig',
            default='workflow.yaml',
            help='workflowconfig file contains data of each'
            ' routine in yaml format. i.e.'
            ' Input/Outputfile, modules and arguments list, the default is workflow.yaml.'
            ' For more information check README file.')

        parser.add_argument('--inputpath', default='',
                            help='Set input directory of WMS.'
                            ' It is not necessary for all WMS,'
                            ' please refer to related manual in repository.')


        parser.add_argument('--wms', default='all',
                            help='Choose specific workflow management system.'
                            'The default behavior produces all supported WMSs.')

        parser.add_argument('--embedded', default='False',
                    help='If True the generated script for Dask/Parsl should be run by FireWorks')
                    
        args = parser.parse_args()

        argdic ["workflowconfig"] = args.workflowconfig
        argdic ["inputpath"] = args.inputpath
        argdic ["wms"] = args.wms
        argdic ["embedded"] = args.embedded


    elif bool(blueargs) == True:
        pass
    return argdic

def run_wfgenes(args):
    png = ''
    wconfig = args['workflowconfig']
    wconfig_stat = ['null', 'null']
    signal.signal(signal.SIGINT, keyboardInterruptHandler)   
    i = 'null' # Entrance token to wconfig_validator func
    valid_wms = {'FireWorks','SimStack', 'Dask','Parsl'}
    if args['wms'] in valid_wms:
        print("wfGenes start converting WConfig to", args['wms'])
    else:    
        print("The selected argument for --wms is not in the list. Posiible options.", valid_wms)
        exit()    
    while True:
        # while user using wfGenes
        time.sleep(1) # Avoid extra cpu load
        if modified(wconfig, wconfig_stat) == True:
            #init= BasewfGenes (args)
            validator = wconfig_validator(BasewfGenes, args ,wconfig)
            wfgenes_init = validator[0]
            verified =  validator[1]
            i =  validator[2]
            if verified == True:
                model = wfgenes_init.wconfig_checker()
                wconfig_status = model[0]
                wconfig_version = model[2]
                if wconfig_status == 'active': 
                    # modeling phase
                    print('Model is verified and Graph generation is active. Remove "active" suffix to proceed with code generation or continue with modling')
                    i = 'null'
                    print('Press ctrl+c to exit')
                    try:
                        graphics = DotwfGenes(wfgenes_init)
                        png = graphics.png_file
                    except Exception as error:
                        print('unexpected error:'+error.args[0])

                else:
                    try:
                        graphics = DotwfGenes(wfgenes_init)
                        png = graphics.png_file
                    except Exception as error:
                        print('unexpected error:'+error.args[0])
                    try : 
                        if args['wms'] == 'FireWorks' or args['wms'] == 'all':
                            graphics = DotwfGenes(wfgenes_init)
                            png = graphics.png_file    
                            fireworks_dict=FireworkwfGenes(wfgenes_init)
                            print('wfGenes succeeded with model generation using FireWorks')
                    except FileNotFoundError as error:
                        print('wfGenes failed with model generation using FireWorks')
                        print(error)
                        pass
                    except Exception as error:
                        print('wfGenes failed with model generation using FireWorks')
                        print('unexpected error:'+ error.args[0])   
                    try:            
                        if args['wms'] == 'SimStack' or args['wms'] == 'all':
                            graphics = DotwfGenes(wfgenes_init)
                            png = graphics.png_file                            
                            simstack_wrapper = PywrapperwfGens(wfgenes_init, args)
                            test2=SimstackwfGenes(args)
                            print('wfGenes succeeded with model generation using SimStack')

                    except Exception as error:
                        print('wfGenes failed with model generation using SimStack')
                        print('unexpected error:'+error.args[0])       
                    try:
                        if args['wms'] == 'Dask' or args['wms'] == 'all':  
                            graphics = DotwfGenes(wfgenes_init)
                            png = graphics.png_file    
                            dask_wf = DaskwfGenes(wfgenes_init, args) 
                            print('wfGenes succeeded with model generation using Dask')
                    except Exception as error:
                        print('wfGenes failed with model generation using Dask')
                        print('unexpected error:'+ error.args[0])
                    try:
                        if args['wms'] == 'Parsl' or args['wms'] == 'all':
                            graphics = DotwfGenes(wfgenes_init)
                            png = graphics.png_file    
                            parsl_wf= ParslwfGenes(wfgenes_init, args)
                            print('wfGenes succeeded with model generation using Parsl')
                    except Exception as error:
                        print('wfGenes failed with model generation using Parsl')
                        print('unexpected error:' + error.args[0])

                    print("Outputs is saved in:", wfgenes_init.wconfig_checker()[1] )
                    return png


            
def main():
    start_time= time.time()
    arg_dic = glue_args()
    png= run_wfgenes(arg_dic)
    end_time = time.time()
    execution_time = end_time - start_time 
    print("wfGenes finished ",arg_dic["wms"], "in",execution_time,"seconds")

def gui():
    cmd = 'jupyter-lab ../wfgenes_gui.ipynb'
    proc = subprocess.call(cmd, shell=True)
    

if __name__ == '__main__':
    main()
                
        
    
   


    