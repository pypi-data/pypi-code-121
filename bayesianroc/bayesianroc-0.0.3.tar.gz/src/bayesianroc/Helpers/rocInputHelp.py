# rocInputHelp.py
# Copyright 2020 André Carrington, Ottawa Hospital Research Institute
# Use is subject to the Apache 2.0 License
# Written by André Carrington
#
# functions:
#   getYes
#   getFraction
#   getROCpoint
#   getROCranges
#   getROCcosts

import numpy             as np
import sys

def getYes(prompt,yes='y',no='n',default='y'):
    #print('*'+prompt+'   '+'*')
    response     = input(prompt+'  ')
    if default.isupper():
        response = response.upper()
    if default.islower():
        response = response.lower()
    if response != yes and response != no: 
        if response != '':
            print(f'Response not recognized, using default: {default}')
        response = default
    #endif
    return response
#enddef

def getFraction(prompt):
    invalid = True
    while invalid:
        try:
            response = float(input(prompt+'  '))
            if response>=0 and response<=1:
                invalid = False
            else:
                print('Value out of range, try again.')
            #endif
        except ValueError:
            print('Unrecognized decimal fraction, try again.')
        #endtry
    #endwhile
    return response
#enddef        

def getROCpoint(prompt):
    invalid = True
    while invalid:
        try:
            response = input(prompt+'  ').split(",")
            x        = float(response[0])
            y        = float(response[1])
            if x>=0 and x<=1 and y>=0 and y<=1:
                invalid = False
            #endif
        except ValueError:
            print('Unrecognized decimal fraction used, try again.')
        #endtry
    #endwhile
    return [x,y]
#enddef

def getROCranges(pArea_range_p):
    pArea_range_text = input(pArea_range_p+'  ')
    if pArea_range_text == '':
        print('Using default: [0:0.33],[0.33:0.66],[0.66:1.0]') 
        pArea_range=[[0,0.33],[0.33,0.66],[0.66,1.0]]
    else:
        # given input text:        '[0:0.2],[0.2:0.5],[0.5:1.0]'
        # create a list of lists: [[0.0,0.2], [0.2,0.5], [0.5,1.0]]
        pArea_rangex = [i for i in list(pArea_range_text.split(","))]
        pArea_range  = []
        all_parts    = [] # not used
        try:
            for j in pArea_rangex:
                j2 = j.strip('[ ]')
                one_part = []
                for k in j2.split(":"):
                    one_part  = one_part    + [float(k)]
                    all_parts = all_parts   + [float(k)] # not used
                pArea_range   = pArea_range + [one_part]
                #endfor
            #endfor
        except ValueError:
            print('Response not recognized')
            raise
        #endtry
    #endif
    
    # assume pArea_range is lowest to highest (not checked)

    # assess if pArea ranges completely span [0,1]
    num_parts      = len(pArea_range)        
    pArea_complete = 0
    if pArea_range[0][0]==0.0 and pArea_range[-1][-1]==1.0:
        pArea_complete = 1 # assume completeness unless we find otherwise...
        if num_parts > 1:
            for i in np.arange(0,num_parts-1):
                if pArea_range[i][1]!=pArea_range[i+1][0]:
                    pArea_complete = 0
                #endif
            #endfor
        #endif
    #endif
    return pArea_range, pArea_complete
#enddef

def getROCcosts(prompt_prefix,cost_mode):
    if  cost_mode  == 'individuals':
        costs      = {'FP' :1, 'FN' :1, 'TP' :0, 'TN' :0}
    else:
        costs      = {'FPR':1, 'FNR':1, 'TPR':0, 'TNR':0}
    #endif
    # fh = sys.stdout
    # fh.flush()
    
    prompt = lambda: f'{prompt_prefix} {cost_name}? [{costs[cost_name]}]'

    cost_names = list(costs)
    for cost_name in cost_names:
        try:
            input_text       = input(prompt()+'  ') # this prompt is a function call
            input_val        = float(input_text)    # on error use default val
            costs[cost_name] = input_val
        except ValueError:
            continue         # nop, leave cost at default value
        #endtry
    #endfor
    return costs
#enddef

