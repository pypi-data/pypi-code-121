# bayesianAUC.py
# Copyright 2020 André Carrington, Ottawa Hospital Research Institute
# Use is subject to the Apache 2.0 License
# Written by André Carrington and Franz Mayr
#
from   scipy.interpolate     import interp1d
import scipy.integrate       as     integrate
import numpy                 as     np
import sys
import bayesianroc.Helpers.rocInputHelp  as     rip


def getInputsFromUser():

    # the preface and input prompts _p (one is a function _f)
    preface       = 'This notebook computes AUC and C measures for the whole ROC curve\n'+ \
                    'or part of an ROC curve.  It computes variations of AUC and C for\n'+ \
                    'more optimal, equitable and personalized decision-making.\n'
                    
    C_p           = 'Compute C measures (equal to AUC)? [y]/n'
    
    pArea_p       = 'Compute partial area/AUC measures? y/[n]'
    pArea_type_p  = 'Partial area range by TPR or FPR? [FPR]'
    pArea_range_p = 'Partial area range? e.g. [0:0.33],[0.33:0.66],[0.66:1.0]'
    pArea_tie_f   = lambda: f'For multiple points at {pArea_type}=x use the SouthWest or NorthEast point? [SW]/NE'
    #             note: pArea_tie_f above, is secure re app/SQL injection, XSS

    bAUC_p        = 'Compute Bayesian AUC? [y]/n'
    
    preface2      = '\nThe Bayesian AUC uses a prior, the prevalence and costs.\n'+ \
                    'Costs automatically include prevalence, regardless of the prior.\n'+ \
                    'It compares performance against the prior, a point in ROC that represents either:\n'+ \
                    '    the prevalence of data, i.e. π,π or\n'+ \
                    '    a person, or\n'+ \
                    '    another classifier.\n'
    
    which_prev_p  = 'Use the sample prevalence? [y]/n'
    pop_prev_p    = 'What is the known/population prevalence?'
    prev_prior_p  = 'Use prevalence for the Bayesian prior? [y]/n'
    prior_p       = 'What is your Bayesian prior (FPR,TPR)? e.g. 0.2,0.5'

    preface3      = '\nThe Bayesian AUC should use costs of errors and procedures.\n'+ \
                    'Typically it uses average (or median) costs.\n'
        
    cost_p        = 'Specify costs of errors and procedures for Bayesian AUC? [y]/n'
    cost_mode_p   = 'Are costs for individuals or rates? [individuals]'
    cost_prefix   = 'What is the average cost of'
    #             note: each_cost_f above, is secure re app/SQL injection, XSS

    personalB_p   = 'Compute the personalized threshold and benefit using personalized costs? y/[n]'   # ADD ME!!
    pcost_mode_p  = 'Are personal costs by individuals or rates? [individuals]'
    pcost_prefix  = 'What is the personal cost of'
    #             note: each_cost_f above, is secure re app/SQL injection, XSS
    
    def makeTieList(policy,num_parts):
        # using pArea_tie, set the tie break policy for each end of each partial curve
        pArea_tie = []
        for i in np.arange(0,num_parts):
            pArea_tie.append([policy,policy])
        #endfor
        pArea_tie[-1][1]='NE'
        return pArea_tie
    #enddef

    # logic
    print(preface)
    fh = sys.stdout
    fh.flush()
    
    do_C            = rip.getYes(C_p,default='y')
    print('')

    do_pArea        = rip.getYes(pArea_p,default='n')
    if  do_pArea   == 'n':
        pArea_type  = 'FPR'
        pArea_range = [[0,1]]
        pArea_tie   = [['SW','NE']]
    else:
        pArea_type                  = rip.getYes(pArea_type_p,yes='FPR',no='TPR',default='FPR')
        pArea_range, pArea_complete = rip.getROCranges(pArea_range_p)
        # print(f'pArea_type: {pArea_type}')
        a=pArea_tie_f()
        # print(f'pArea_tie_f: {a}')
        policy                      = rip.getYes(a,yes='SW' ,no='NE' ,default='SW' )
        # print(f'policy: {policy}')
        pArea_tie                   = makeTieList(policy,len(pArea_range))        
        # print(f'pArea_tie: {pArea_tie}')
    #endif
    print('')
    
    do_bAUC         = rip.getYes(bAUC_p,default='y')
    if  do_bAUC    == 'n':
        sample_prev = 'y'
        prev_prior  = 'y'
        prev        = 0
        prior       = (0.5,0.5)
        do_costs    = 'n'
        cost_mode   = 'individuals'
        costs       = {'FP' :1, 'FN' :1, 'TP' :0, 'TN' :0, 'mode':'individuals'}
        do_personalB= 'n'
        pcost_mode  = None
        pcosts      = None
    else:
        print(preface2)
        sample_prev = rip.getYes(which_prev_p,default='y')
        if sample_prev == 'n':
            prev    = rip.getFraction(pop_prev_p)
        else:
            prev    = 0 # set this later
        #endif
        
        prev_prior  = rip.getYes(prev_prior_p,default='y')
        if prev_prior == 'n':
            prior   = rip.getROCpoint(prior_p)
        else:
            prior   = 0 # set this later
        #endif

        print(preface3)        
        do_costs          = rip.getYes(cost_p,default='y')
        if do_costs       =='y':  
            cost_mode     = rip.getYes(cost_mode_p,yes='individuals',no='rates',default='individuals')
            costs         = rip.getROCcosts(cost_prefix,cost_mode)            
            costs['mode'] = cost_mode   # add cost_mode into costs dictionary
        else:
            cost_mode     = 'individuals'
            costs         = {'FP' :1, 'FN' :1, 'TP' :0, 'TN' :0, 'mode':'individuals'}
        #endif
        print('')
        
        do_personalB      = rip.getYes(personalB_p,default='n')
        if do_personalB   =='y':  
            pcost_mode    = rip.getYes(pcost_mode_p,yes='individuals',no='rates',default='individuals')
            pcosts        = rip.getROCcosts(pcost_prefix,pcost_mode)            
            pcosts['mode']= pcost_mode  # add cost_mode into costs dictionary
        else:
            pcost_mode  = None
            pcosts      = None
        #endif
        
    #endif
    
    # return values
    pArea_settings = {'do_pArea'    :do_pArea,
                      'pArea_type'  :pArea_type,
                      'pArea_range' :pArea_range,
                      'pArea_tie'   :pArea_tie   }
    
    bAUC_settings  = {'do_bAUC'     :do_bAUC,
                      'sample_prev' :sample_prev,
                      'prev_prior'  :prev_prior,
                      'prev'        :prev,
                      'prior'       :prior,
                      'do_costs'    :do_costs,
                      'do_personalB':do_personalB}
    
    return pArea_settings, bAUC_settings, costs, pcosts
#enddef

def PeirceMetzCost(neg, pos, cost):
    # costs for individuals -- the approach/paradigm found in the literature
    # Peirce 1884, Metz 1978
    cost_P    =    cost['FN']  - cost['TP']
    cost_N    =    cost['FP']  - cost['TN']
    m         =    (neg/pos)   * (cost_N/cost_P)
    return m
#enddef

def CarringtonCost(neg, pos, cost):
    # costs for rates is an alternative paradigm which reveals a squared effect 
    # Carrington 2020
    cost_P    =   cost['FNR']  - cost['TPR']
    cost_N    =   cost['FPR']  - cost['TNR']
    m         = ((neg/pos)**2) * (cost_N/cost_P)
    return m
#enddef

def bayesian_iso_lines(prior_point, neg, pos, costs):
    # iso performance line that passes through a point representing a Bayesian prior (e.g., prevalence)
    x_bayesian    = prior_point[0]
    y_bayesian    = prior_point[1]
    
    if  costs['mode'] =='individuals' or costs['mode'] != 'rates':
        m = PeirceMetzCost(neg, pos, costs)
    else: # cost['mode'] =='rates':
        m = CarringtonCost(neg, pos, costs)
    #endif

    def line_y(x):
        return m*(x-x_bayesian)+y_bayesian
    #enddef

    def line_x(y):
        return (y-y_bayesian)/m + x_bayesian
    # enddef

    return line_y, line_x  # return a function of x, not a value
#enddef

# modified slightly:
def bayesian_auc(fpr, tpr, neg, pos, partial_area_settings, costs):
    approximate_y = interp1d(fpr, tpr)  # x,y; to estimate y=f(x)
    approximate_x = interp1d(tpr, fpr)  # y,x; to estimate x=f_inverse(y)
    prev          = pos/(neg+pos)
    prior_point   = (prev, prev)
    
    b_iso_line_y, \
    b_iso_line_x  = bayesian_iso_lines(prior_point, neg, pos, costs)
    
    def roc_over_bayesian_iso_line(x):
        res       = approximate_y(x) - b_iso_line_y(x)
        if(res>0):
            return res
        else:
            return 0
        #endif
    #enddef

    def roc_left_of_bayesian_iso_line(y):
        # use (1 - ...) in both terms to flip FPR into TNR
        res       = (1-approximate_x(y)) - (1-b_iso_line_x(y))
        #if(res>0):
        #    return res
        #else:
        #    return 0
        ##endif
        return res
    #enddef

    AUC      = integrate.quad(lambda x: approximate_y(x), 0, 1)[0]
    pAUC_pi  = integrate.quad(lambda x: roc_over_bayesian_iso_line(x), 0, 1)[0]
    pAUCx_pi = integrate.quad(lambda y: roc_left_of_bayesian_iso_line(y), 0, 1)[0]
    return pAUC_pi, pAUCx_pi, AUC
#enddef
