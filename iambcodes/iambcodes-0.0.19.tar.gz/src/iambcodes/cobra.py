import numpy as np
import csv
from cobra.io import read_sbml_model
from cobra import Reaction, Metabolite

def TestSubstrate(model, EX_Sub_Act:list, EX_Sub_Off=['EX_glc__D_e'], Rate=10):
    '''
    Simulation of growth rate with defined substrates for growth and substrates not used for growth.

    Parameters
    ----------
    model : cobra model
        Genome scale metabolic model.
    EX_Sub_Act : list of cobra exchange reaction
        List of the substrate exchange reactions to be tested, typically ['EX_glc__D_e'].
    EX_Sub_Off : list of cobra extracellular metabolite names, optional
        DESCRIPTION. The default is ['EX_glc__D'].
    Rate : TYPE, optional
        DESCRIPTION. The default is 10.

    Returns
    -------
    TYPE
        DESCRIPTION.

    '''

    with model:
        medium = model.medium
        # deactivating uptake from off substrates
        medium.update({mySub: 0.0 for mySub in EX_Sub_Off})
        # setting new substrate uptake rates
        medium.update({mySub: Rate for mySub in EX_Sub_Act})
        model.medium = medium
        return round(model.slim_optimize(),2)
# =============================================================================
# 
# =============================================================================
def MetNewFromExist(MetIn):
    '''
    Generate new cobra external metabolite object from input cobra metabolite.

    Parameters
    ----------
    MetIn : cobra metabolite object
        Internal metabolite for which an external metabolite is generated.

    Returns
    -------
    Metout : cobra metabolite object
        External metabolite object.

    '''
    Metout = Metabolite('{}_e'.format(MetIn.id[:-2]),
                       formula = MetIn.formula,
                       name = MetIn.name,
                       compartment = 'e',
                       charge = MetIn.charge)
    Metout.annotation = MetIn.annotation
    return Metout

def CreateTransReact(MetIn):
    '''
    Create transfer reaction from internal to external metabolite.

    Parameters
    ----------
    MetIn : cobra metabolite object
        Internal cobra metabolite object.

    Returns
    -------
    reaction : cobra reaction object
        Transport reaction from cytoplasm to extracellular.

    '''
    reaction = Reaction('Trans_{}'.format(MetIn.id),
                       name = 'Transport c<->e {}'.format(MetIn.name),
                       lower_bound = -1000,
                       upper_bound = 1000)
    MetOut = MetNewFromExist(MetIn)
    reaction.add_metabolites({MetIn:-1.0, MetOut:1.0})
    
    return reaction

def CSVexport(myDict, FName='BiologGrowthTest'):
    fields = ['id','name','id_e','id_c','growth','CL_Growth']
    with open(FName, 'w') as f:
        w = csv.DictWriter(f, fields)
        w.writeheader()
        for k in myDict:
            w.writerow({field: myDict[k].get(field) or k for field in fields})

def CheckPMinGSMM(model, PM_df, EX_Sub_Off=['EX_glc__D_e']):
    Substrate_list = list()
    ResultID = list()
    
    for Indx,Sub in enumerate(PM_df['BiGG'].astype(str)):
        Sub_e = '{}_e'.format(Sub)
        # Sub_c = '{}_c'.format(Sub)
        Sub_eIdx = np.where([Sub_e==met.id for met in model.metabolites])[0]
        # Sub_cIdx = np.where([Sub_c==met.id for met in model.metabolites])[0]
        # first testing whether growth was detected in biolog or not
        # if growth was detected, we give our best to check substrate metabolization, otherwise not
        # if PM_df['Growth'][Indx]:
            # testing whether biolog metabolite is extracellular or cytoplasmic
        if Sub_eIdx.size>0: # and Sub_cIdx.size>0 
            # metabolite is extracellular, 
            # existence of exchange reaction unclear
            EX_SubRct = 'EX_{}'.format(Sub_e)
            try: 
                myGrowth = TestSubstrate(model, [EX_SubRct], EX_Sub_Off)    
            except KeyError:
                myGrowth = 0
#                 model.reactions.get_by_id(EX_SubRct)
#             except KeyError:
# #                with model:
#                 model.add_boundary(model.metabolites.get_by_id(Sub_e), type='exchange', lb=0, ub=1000)
#                 myGrowth = TestSubstrate(model, [EX_SubRct], EX_Sub_Off)
#                     # Substrate_list.append(myGrowth)
#     #                 print('New exchange reaction for {} with growth: {}'.format(Substrate, myGrowth))        
#             else:
            # myGrowth = TestSubstrate(model, [EX_SubRct], EX_Sub_Off)    
                # Substrate_list.append(myGrowth)

#         elif Sub_cIdx.size>0 and Sub_eIdx.size<1: 
#             # metabolite is cytoplasmic but not extracellular
#             myMet = model.metabolites.get_by_id(Sub_c)
#             myTransport = CreateTransReact(myMet)
#             EX_SubRct = 'EX_{}'.format(Sub_e)
# #            with model:
#             model.add_reactions([myTransport])
#             model.add_boundary(model.metabolites.get_by_id(Sub_e), type='exchange', lb=0, ub=1000)
#             myGrowth = TestSubstrate(model, [EX_SubRct], EX_Sub_Off)
#                 # Substrate_list.append(myGrowth)

        # if Sub_cIdx.size<1 and Sub_eIdx.size>0:
        #     metabolite is only extracellular (unlikely)
        #     Substrate_list.append('Z')
                                       
        # if Sub_cIdx.size<1 and Sub_eIdx.size<1:
        #     # metabolite not in GSMM
        #     Substrate_list.append('Z')

#         else:
#             myGrowth = -1
#     # no growth occured in Biolog:
#     else:
#         if Sub_eIdx.size>0: # and Sub_cIdx.size>0 
#             # metabolite is extracellular, 
#             # existence of exchange reaction unclear
#             EX_SubRct = 'EX_{}'.format(Sub_e)
#             try: 
#                 model.reactions.get_by_id(EX_SubRct)
#             except KeyError:
# #                with model:
#                 model.add_boundary(model.metabolites.get_by_id(Sub_e), type='exchange', lb=0, ub=1000)
#                 myGrowth = TestSubstrate(model, [EX_SubRct], EX_Sub_Off)
#                     # Substrate_list.append(myGrowth)
#     #                 print('New exchange reaction for {} with growth: {}'.format(Substrate, myGrowth))        
#             else:
#                 myGrowth = TestSubstrate(model, [EX_SubRct], EX_Sub_Off)
#                 # Substrate_list.append(myGrowth)
        else:
            myGrowth = 0
            
        Substrate_list.append(myGrowth)
        ResultID.append(CheckWellinGSMM(myGrowth,PM_df.loc[Indx, 'Growth']))
    return Substrate_list, ResultID, model


def CheckWellinGSMM(myGrowth, myBool):
    '''
    Return categorical number how the substrate is used in the model.
    0: not in model, missing in model
    1: bio:-; model:+, false positive
    2: bio:+; model:-, false negative
    3: bio:-; model:-, true negative
    4: bio:+; model:+, true positive

    Parameters
    ----------
    myGrowth : number
        model growth rate on substrates in biolog.
    myBool : boolean
        growth in biolog.

    Returns
    -------
    categorical of correlation Biolog+GSMM.

    '''
    if myBool and myGrowth >= .01:
#         growth occured in well and model
        return 4
    elif not myBool and any([myGrowth < .01, np.isnan(myGrowth)]):
#         no growth in well and no growth in model
        return 3
    elif myBool and any([myGrowth < .01, np.isnan(myGrowth)]):
#       growth occured in well not model
        return 2
    elif not myBool and myGrowth >= .01:
#         no growth in well but growth in model
        return 1
#     elif myGrowth < 0:
# #        no growth in well and model lacks metabolite     
#         return 0

def MetSharedRcts(model, Met1, Met2):
    '''
    This function lists all reactions which are shared by two metabolites
    
    Parameters
    ----------
    model : cobra model
        The cobra model for analysis.
    Met1 : str
        Metabolite id.
    Met2 : str
        Metabolite id.

    Returns
    -------
    list, List of shared reactions.

    '''
    return [reaction for reaction in model.metabolites.get_by_id(Met1).reactions if reaction in model.metabolites.get_by_id(Met2).reactions]

def MetFluxConnect(model, Met1, Met2, SubOff='EX_glc__D_e', ngam=False, slim=True):
    '''
    Test whether there exists a flux between two metabolites. The first metabolite is set as source and FBA is optimized to the second metabolite.

    Parameters
    ----------
    model : cobra model
        .
        The cobra model for analysis.
    Met1 : str
        Metabolite id.
    Met2 : str
        Metabolite id.
    SubOff: str
        Substrate id to be set to zero
    ngam: str
        non growth associated maintenance to be set to zero, because checking close metabolites might not fullfill the base ATP demand in ngam
    slim : Boolean
        Decision whether only the value of the objective is reported via slim_optimize, or the full flux-reaction list.

    Returns
    -------
    list, List of reactions and flux values.

    '''
    with model:
        # medium = dict.fromkeys(model.medium, 0)
        medium = model.medium
        medium[SubOff] = 0
        model.medium = medium
        model.add_boundary(model.metabolites.get_by_id(Met1), type='sink')        
        model.add_boundary(model.metabolites.get_by_id(Met2), type='sink')
        if ngam:
            model.reactions.get_by_id(ngam).lower_bound = 0
        model.objective = 'SK_{}'.format(Met2)
        if slim:
            flux = model.slim_optimize()
        else:
            flux = model.optimize()
            
        return flux