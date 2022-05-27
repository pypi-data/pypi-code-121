# -*- coding: utf-8 -*-
"""
Created on Thu Jul 23 19:18:05 2020

@author: msmsa
"""
import pandas as pd
import numpy as np
from .Flow import Flow


def mix(*args):
    mix = Flow(args[0]._CommonData)

    def add_helper(x, y):
        if x is None and y is None:
            return(None)
        elif x is None:
            return(y)
        elif y is None:
            return(x)
        else:
            return(x + y)
    for F in args:
        mix.mass = add_helper(mix.mass, F.mass)
        mix.ts = add_helper(mix.ts, F.ts)
        mix.moist = add_helper(mix.moist, F.moist)
        mix.C = add_helper(mix.C, F.C)
        mix.PFAS += F.PFAS

    if all(['vol' in F.__dict__ for F in args]):
        mix.vol = sum([F.vol for F in args])

    if all(['VS' in F.__dict__ for F in args]):
        mix.VS = sum([F.VS for F in args])

    if all(['FlowType' in F.__dict__ for F in args]):
        if len(set([F.FlowType for F in args])) == 1:
            mix.FlowType = F.FlowType
        else:
            raise ValueError('Type of the mixed flow are not the same: {}'.format(set(['FlowType' in F.__dict__ for F in args])))
    return mix


def split(InputFlow, **kwargs):
    if sum(kwargs.values()) < 0.999 or sum(kwargs.values()) > 1.001:
        raise ValueError('Sum of fractions is not 1')

    output = {}
    if len(kwargs) == 1:
        output[list(kwargs.keys())[0]] = InputFlow
    else:
        for name, frac in kwargs.items():
            output[name] = Flow(InputFlow._CommonData)
            output[name].mass = None if InputFlow.mass is None else InputFlow.mass * frac
            output[name].ts = None if InputFlow.ts is None else InputFlow.ts * frac
            output[name].moist = None if InputFlow.moist is None else InputFlow.moist * frac
            output[name].C = None if InputFlow.C is None else InputFlow.C * frac
            output[name].PFAS = InputFlow.PFAS * frac

            if 'vol' in InputFlow.__dict__:
                output[name].vol = InputFlow.vol * frac

            if 'VS' in InputFlow.__dict__:
                output[name].VS = InputFlow.VS * frac

            if 'bulk_dens' in InputFlow.__dict__:
                output[name].bulk_dens = InputFlow.bulk_dens

            if 'FlowType' in InputFlow.__dict__:
                output[name].FlowType = InputFlow.FlowType
    return(output)


def solid_water_partition(mixture, water_vol, LogPartCoef_data):
    solid_mass = mixture.ts

    C_Water = pd.Series(index=mixture._PFAS_Index, dtype='float64')
    C_Solid = pd.Series(index=mixture._PFAS_Index, dtype='float64')

    for i, j in enumerate(mixture._PFAS_Index):
        C_Water[i] = mixture.PFAS[j] / (water_vol + mixture.get_Ccont() * solid_mass * 10**LogPartCoef_data[j]['amount'])
        C_Solid[i] = C_Water[i] * 10**(LogPartCoef_data[j]['amount']) * mixture.get_Ccont()
    return C_Solid, C_Water


def soil_sorption(mixture, LogPartCoef_data, Leachate_vol, Runoff_vol):
    water_mass = mixture.moist
    water_vol = water_mass * 1

    PFAS_remain = pd.Series(index=mixture._PFAS_Index, dtype='float64')
    for i, j in enumerate(mixture._PFAS_Index):
        K = 1 / (water_vol + mixture.C * 10**LogPartCoef_data[j]['amount'])
        A = (Leachate_vol + Runoff_vol) / 365 * K
        PFAS_remain[i] = mixture.PFAS[j] * np.exp(-A * 365)

    Remaining = Flow(mixture._CommonData)
    Remaining.PFAS = PFAS_remain
    Leachate = Flow(mixture._CommonData)
    Leachate.vol = Leachate_vol
    Leachate.PFAS = (Leachate_vol / (Runoff_vol + Leachate_vol)) * (mixture.PFAS - PFAS_remain)
    Runoff = Flow(mixture._CommonData)
    Runoff.vol = Runoff_vol
    Runoff.PFAS = (Runoff_vol / (Runoff_vol + Leachate_vol)) * (mixture.PFAS - PFAS_remain)

    return Remaining, Leachate, Runoff


def aerobic_composting(mixture, ProcessData, LogPartCoef_data, PrecipitationData):
    water_vol = mixture.moist * 1  # L/kg

    # Decomposition
    C_loss = mixture.C * ProcessData['frac_C_lost']['amount']  # KgC
    Solid_loss = C_loss * ProcessData['sol_loss_per_C_loss']['amount']  # Kg

    # Calculating the volume of Precipitation (includes collected and uncollected Contact Water)
    Area_windrow = mixture.mass / ProcessData['bulk_dens']['amount'] * 2 / ProcessData['wind_ht']['amount']  # m^2   area/volume=(L*W)/(H*W/2*L)=2/H
    Precip_Vol = Area_windrow * PrecipitationData['ann_precip']['amount'] * 1000 * ProcessData['ac_time']['amount'] / 365  # L/yr

    if ProcessData['is_covered']['amount']:
        CW_vol = 0
        CW_Col_vol = 0
    else:
        if ProcessData['is_cw_col']['amount']:
            CW_Col_vol = Precip_Vol * ProcessData['frac_cw_col']['amount']
            CW_vol = Precip_Vol - CW_Col_vol
        else:
            CW_Col_vol = 0
            CW_vol = Precip_Vol

    # PFAS balance
    PFAS_remain = pd.Series(index=mixture._PFAS_Index, dtype='float64')
    for i, j in enumerate(mixture._PFAS_Index):
        K = 1 / (water_vol + mixture.C * 10**LogPartCoef_data[j]['amount'])
        A = (CW_Col_vol + CW_vol) / ProcessData['ac_time']['amount'] * K
        PFAS_remain[i] = mixture.PFAS[j] * np.exp(-A * ProcessData['ac_time']['amount'])

    # Initialize products
    Remaining = Flow(mixture._CommonData)
    Remaining.ts = mixture.ts - Solid_loss
    Remaining.C = mixture.C - C_loss
    Remaining.moist = Remaining.ts * (1 / ProcessData['ts_end']['amount'] - 1)
    Remaining.mass = Remaining.moist + Remaining.ts

    epsilon = 0.00000000001  # to solve the devide by zero error

    Contact_water = Flow(mixture._CommonData)
    Contact_water.vol = CW_vol
    Contact_water.ts = mixture.ts * ProcessData['frac_sol_to_cw']['amount'] * (CW_vol / (CW_Col_vol + CW_vol + epsilon))
    Contact_water.C = mixture.C * ProcessData['frac_sol_to_cw']['amount'] * (CW_vol / (CW_Col_vol + CW_vol + epsilon))
    Contact_water.moist = Contact_water.vol * 1
    Contact_water.mass = Contact_water.ts + Contact_water.moist

    Collected_Contact_water = Flow(mixture._CommonData)
    Collected_Contact_water.vol = CW_Col_vol
    Collected_Contact_water.ts = mixture.ts * ProcessData['frac_sol_to_cw']['amount'] * (CW_Col_vol / (CW_Col_vol + CW_vol + epsilon))
    Collected_Contact_water.C = mixture.C * ProcessData['frac_sol_to_cw']['amount'] * (CW_Col_vol / (CW_Col_vol + CW_vol + epsilon))
    Collected_Contact_water.moist = Collected_Contact_water.vol * 1
    Collected_Contact_water.mass = Collected_Contact_water.ts + Collected_Contact_water.moist

    # Allocating PFAS to products
    Remaining.PFAS = PFAS_remain
    Contact_water.PFAS = (mixture.PFAS - PFAS_remain) * (CW_vol / (CW_Col_vol + CW_vol + epsilon))
    Collected_Contact_water.PFAS = (mixture.PFAS - PFAS_remain) * (CW_Col_vol / (CW_Col_vol + CW_vol + epsilon))
    return Remaining, Contact_water, Collected_Contact_water


def curing(mixture, ProcessData, LogPartCoef_data, PrecipitationData):
    water_vol = mixture.moist * 1  # L/kg

    # Calculating the volume of Precipitation (Contact Water)
    Area_windrow = mixture.mass / ProcessData['bulk_dens']['amount'] * 2 / ProcessData['wind_ht']['amount']  # m^2   area/volume=(L*W)/(H*W/2*L)=2/H
    Precip_Vol = Area_windrow * PrecipitationData['ann_precip']['amount'] * 1000 * ProcessData['curing_time']['amount'] / 365  # L/yr
    CW_vol = Precip_Vol

    # Decomposition
    C_loss = mixture.C * ProcessData['frac_C_lost']['amount']  # KgC
    Solid_loss = C_loss * ProcessData['sol_loss_per_C_loss']['amount']  # Kg

    # PFAS balance
    PFAS_remain = pd.Series(index=mixture._PFAS_Index, dtype='float64')
    for i, j in enumerate(mixture._PFAS_Index):
        K = 1 / (water_vol + mixture.C * 10**LogPartCoef_data[j]['amount'])
        A = CW_vol / ProcessData['curing_time']['amount'] * K
        PFAS_remain[i] = mixture.PFAS[j] * np.exp(-A * ProcessData['curing_time']['amount'])

    # Initialize products
    Remaining = Flow(mixture._CommonData)
    Remaining.ts = mixture.ts - Solid_loss
    Remaining.C = mixture.C - C_loss
    Remaining.moist = Remaining.ts * (1 / ProcessData['ts_end']['amount'] - 1)
    Remaining.mass = Remaining.moist + Remaining.ts

    Contact_water = Flow(mixture._CommonData)
    Contact_water.vol = CW_vol

    # Allocating PFAS to products
    Remaining.PFAS = PFAS_remain
    Contact_water.PFAS = mixture.PFAS - PFAS_remain

    return Remaining, Contact_water


def landfil_sorption(mixture, LogPartCoef_data, LF_Leachate_Vol, Leachate_Vol):
    water_mass = mixture.moist
    water_vol = water_mass * 1

    PFAS_remain = pd.Series(index=mixture._PFAS_Index, dtype='float64')
    for i, j in enumerate(mixture._PFAS_Index):
        K = 1 / (water_vol + mixture.C * 10**LogPartCoef_data[j]['amount'])
        A = (LF_Leachate_Vol + Leachate_Vol) / 365 * K
        PFAS_remain[i] = mixture.PFAS[j] * np.exp(-A * 365)

    LF_storage = Flow(mixture._CommonData)
    LF_storage.PFAS = PFAS_remain

    epsilon = 0.00000000001  # to solve the devide by zero error
    LF_Leachate = Flow(mixture._CommonData)
    LF_Leachate.vol = LF_Leachate_Vol
    LF_Leachate.moist = LF_Leachate.vol * 1
    LF_Leachate.ts = 0
    LF_Leachate.C = 0
    LF_Leachate.mass = LF_Leachate.moist + LF_Leachate.ts
    LF_Leachate.PFAS = (mixture.PFAS - PFAS_remain) * (LF_Leachate_Vol / (LF_Leachate_Vol + Leachate_Vol + epsilon))

    Leachate = Flow(mixture._CommonData)
    Leachate.vol = Leachate_Vol
    Leachate.PFAS = (mixture.PFAS - PFAS_remain) * (Leachate_Vol / (LF_Leachate_Vol + Leachate_Vol + epsilon))

    return LF_storage, LF_Leachate, Leachate


def landfil_sorption_plus(mixture, LogPartCoef_data, Additive_LogPartCoef, Additive_mass, LF_Leachate_Vol, Leachate_Vol):
    water_mass = mixture.moist
    water_vol = water_mass * 1

    # PFAS balance
    PFAS_remain = pd.Series(index=mixture._PFAS_Index, dtype='float64')
    for i, j in enumerate(mixture._PFAS_Index):
        K = 1 / (water_vol + mixture.C * 10**LogPartCoef_data[j]['amount']
                 + Additive_mass * 10**Additive_LogPartCoef[j]['amount'])
        A = (LF_Leachate_Vol + Leachate_Vol) / 365 * K
        PFAS_remain[i] = mixture.PFAS[j] * np.exp(-A * 365)

    # Initialize products
    LF_Leachate = Flow(mixture._CommonData)
    LF_Leachate.vol = LF_Leachate_Vol
    LF_Leachate.moist = LF_Leachate.vol * 1
    LF_Leachate.ts = 0
    LF_Leachate.C = 0
    LF_Leachate.mass = LF_Leachate.moist + LF_Leachate.ts

    Leachate = Flow(mixture._CommonData)
    Leachate.vol = Leachate_Vol

    Remaining = Flow(mixture._CommonData)
    Remaining.ts = mixture.ts
    Remaining.C = mixture.C
    Remaining.moist = mixture.moist
    Remaining.mass = Remaining.moist + Remaining.ts

    # Allocating PFAS to products
    epsilon = 0.00000000001  # to solve the devide by zero error
    Remaining.PFAS = PFAS_remain
    LF_Leachate.PFAS = (mixture.PFAS - PFAS_remain) * (LF_Leachate_Vol / (Leachate_Vol + LF_Leachate_Vol + epsilon))
    Leachate.PFAS = (mixture.PFAS - PFAS_remain) * (Leachate_Vol / (Leachate_Vol + LF_Leachate_Vol + epsilon))

    return Remaining, LF_Leachate, Leachate


def dewatering(mixture, final_sol_cont, cont_PFAS_water, is_active=True):
    solids = Flow(mixture._CommonData)
    rmvd_water = Flow(mixture._CommonData)

    if is_active:
        # Calc Water removed
        if mixture.mass > 0:
            solids.ts = mixture.ts
            solids.C = mixture.C
            solids.VS = mixture.VS
            solids.moist = mixture.ts / final_sol_cont * (1 - final_sol_cont)
            solids.mass = solids.ts + solids.moist

            # Calc vol of lost water
            vol_flow = (mixture.moist - solids.moist) * 1

            # Calc PFAS in the lost water
            kwargs = {}
            kwargs['PFAS_cont'] = {}
            for i in cont_PFAS_water.index:
                kwargs['PFAS_cont'][i] = cont_PFAS_water[i]

            # set the lost water flow
            rmvd_water.set_flow(mass_flow=vol_flow * 1, ts_cont=0, C_cont=0, **kwargs)
            rmvd_water.vol = vol_flow

            # PFAS Balance
            solids.PFAS = mixture.PFAS - rmvd_water.PFAS
    else:
        solids = mixture
        rmvd_water = Flow(mixture._CommonData, ZeroFlow=True)
        rmvd_water.vol = 0
    return solids, rmvd_water


def drying(mixture, dryer_param, cont_PFAS_water):
    solids = Flow(mixture._CommonData)
    DryerExhaust = Flow(mixture._CommonData)

    if dryer_param['is_sol_dry']['amount']:
        # Calc Water removed
        if mixture.mass > 0:
            solids.ts = mixture.ts
            solids.C = mixture.C
            solids.VS = mixture.VS
            solids.moist = mixture.ts / dryer_param['sol_cont_dry']['amount'] * (1 - dryer_param['sol_cont_dry']['amount'])
            solids.mass = solids.ts + solids.moist

            # Calc vol of evaporated water
            vol_flow = (mixture.moist - solids.moist) * 1

            # Calc PFAS in the evaporated water
            for i in cont_PFAS_water.index:
                DryerExhaust.PFAS[i] = cont_PFAS_water[i] * vol_flow * 1 / 1 * dryer_param['frac_PFAS_to_Vol']['amount']

            # PFAS Balance
            solids.PFAS = mixture.PFAS - DryerExhaust.PFAS
    else:
        solids = mixture
        DryerExhaust = Flow(mixture._CommonData, ZeroFlow=True)
    return solids, DryerExhaust


def stabilization(mixture, LogPartCoef_data, Additive_LogPartCoef, Additive_mass, Leachate_vol, Runoff_vol):
    water_mass = mixture.moist
    water_vol = water_mass * 1

    # PFAS balance
    PFAS_remain = pd.Series(index=mixture._PFAS_Index, dtype='float64')
    for i, j in enumerate(mixture._PFAS_Index):
        K = 1 / (water_vol + mixture.C * 10**LogPartCoef_data[j]['amount']
                 + Additive_mass * 10**Additive_LogPartCoef[j]['amount'])
        A = (Leachate_vol + Runoff_vol) / 365 * K
        PFAS_remain[i] = mixture.PFAS[j] * np.exp(-A * 365)

    # Initialize products
    Leachate = Flow(mixture._CommonData)
    Leachate.vol = Leachate_vol

    Runoff = Flow(mixture._CommonData)
    Runoff.vol = Runoff_vol

    Remaining = Flow(mixture._CommonData)
    Remaining.ts = mixture.ts
    Remaining.C = mixture.C
    Remaining.moist = mixture.moist
    Remaining.mass = Remaining.moist + Remaining.ts

    # Allocating PFAS to products
    epsilon = 0.00000000001  # to solve the devide by zero error
    Remaining.PFAS = PFAS_remain
    Leachate.PFAS = (mixture.PFAS - PFAS_remain) * (Leachate_vol / (Runoff_vol + Leachate_vol + epsilon))
    Runoff.PFAS = (mixture.PFAS - PFAS_remain) * (Runoff_vol / (Runoff_vol + Leachate_vol + epsilon))

    return Remaining, Leachate, Runoff


def AddWater(InputFlow, Final_Moist_Cont):
    Output = Flow(InputFlow._CommonData)
    Min_Output_water = Final_Moist_Cont * (InputFlow.ts / (1 - Final_Moist_Cont))
    if InputFlow.moist < Min_Output_water:
        Output.moist = Min_Output_water
        Output.vol = Min_Output_water * 1
        Output.ts = InputFlow.ts
        Output.mass = Output.ts + Output.moist
        Output.C = InputFlow.C
        if 'VS' in InputFlow.__dict__:
            Output.VS = InputFlow.VS
        Output.PFAS = InputFlow.PFAS
    else:
        Output = InputFlow
    return Output
