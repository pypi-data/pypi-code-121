# -*- coding: utf-8 -*-
"""
Created on Tue Aug 18 10:44:45 2020

@author: msmsa
"""
import pandas as pd
from .Flow import Flow
from .SubProcesses import split
from PFAS_SAT_InputData import AdvWWTInput
from .ProcessModel import ProcessModel
import warnings


class AdvWWT(ProcessModel):
    """
    Assumptions:
        1. No volatilization or degradation of PFAS.
        2. Steady state.
        3. Concentration in water remains constant.
        4. Annual time horizon.
    """
    ProductsType = ['SpentGAC', 'ROConcentrate', 'SpentIER']

    def __init__(self, input_data_path=None, CommonDataObject=None, InventoryObject=None, Name=None):
        super().__init__(CommonDataObject, InventoryObject)
        self.InputData = AdvWWTInput(input_data_path)
        self.Name = Name if Name else 'Advanced WWT'

    def calc(self, Inc_flow):
        # Initialize the Incoming flow
        self.Inc_flow = Inc_flow

        # Allocation to RO and GAC
        Total = self.InputData.Trtmnt_optn['frac_to_RO']['amount'] + self.InputData.Trtmnt_optn['frac_to_GAC']['amount'] + \
            self.InputData.Trtmnt_optn['frac_to_IonEx']['amount']
        if abs(Total - 1) > 0.01:
            warnings.warn("Sum of allocation factors to RO, GAC and Ion Exchange is not 1 \n Factors are normalized.")

            self.InputData.Trtmnt_optn['frac_to_RO']['amount'] /= Total
            self.InputData.Trtmnt_optn['frac_to_GAC']['amount'] /= Total
            self.InputData.Trtmnt_optn['frac_to_IonEx']['amount'] /= Total

        self.Allocted_vol = split(self.Inc_flow, **{'RO': self.InputData.Trtmnt_optn['frac_to_RO']['amount'],
                                                    'GAC': self.InputData.Trtmnt_optn['frac_to_GAC']['amount'],
                                                    'IonEx': self.InputData.Trtmnt_optn['frac_to_IonEx']['amount']})

        # RO
        # RO PFAS balance
        self.RO_effluent = Flow(self.CommonData)
        self.RO_concentrate = Flow(self.CommonData)
        for i in self.Inc_flow._PFAS_Index:
            self.RO_concentrate.PFAS[i] = self.Allocted_vol['RO'].PFAS[i] * self.InputData.RO_RemEff[i]['amount']
            self.RO_effluent.PFAS[i] = self.Allocted_vol['RO'].PFAS[i] * (1 - self.InputData.RO_RemEff[i]['amount'])

        # RO volume balance
        self.RO_concentrate.vol = self.Allocted_vol['RO'].vol * self.InputData.RO['frac_effl_rem_med']['amount']
        self.RO_effluent.vol = self.Allocted_vol['RO'].vol - self.RO_concentrate.vol

        # RO Concentrate properties
        self.RO_concentrate.moist = self.RO_concentrate.vol * 1
        self.RO_concentrate.ts = self.InputData.RO['ts_rem_med']['amount'] * self.RO_concentrate.moist /\
            (1 - self.InputData.RO['ts_rem_med']['amount'])
        self.RO_concentrate.mass = self.RO_concentrate.moist + self.RO_concentrate.ts
        self.RO_concentrate.VS = self.RO_concentrate.ts * self.InputData.RO['VS_rem_med']['amount']
        self.RO_concentrate.C = self.RO_concentrate.ts * self.InputData.RO['C_rem_med']['amount']

        # GAC
        # GAC PFAS balance
        self.GAC_effluent = Flow(self.CommonData)
        self.SpentGAC = Flow(self.CommonData)
        self.SpentGAC.set_FlowType('SpentGAC')
        for i in self.Inc_flow._PFAS_Index:
            self.SpentGAC.PFAS[i] = self.Allocted_vol['GAC'].PFAS[i] * self.InputData.GAC_RemEff[i]['amount']
            self.GAC_effluent.PFAS[i] = self.Allocted_vol['GAC'].PFAS[i] * (1 - self.InputData.GAC_RemEff[i]['amount'])

        # Spent GAC
        GAC_mass = self.Allocted_vol['GAC'].vol / self.InputData.GAC['Bed_vol_ratio']['amount'] * self.InputData.GAC['GAC_dens']['amount']
        self.SpentGAC.moist = GAC_mass * (1 - self.InputData.GAC['ts_rem_med']['amount'])
        self.SpentGAC.ts = GAC_mass - self.SpentGAC.moist
        self.SpentGAC.mass = GAC_mass
        self.SpentGAC.C = self.SpentGAC.ts * self.InputData.GAC['C_rem_med']['amount']
        self.SpentGAC.VS = self.SpentGAC.ts * self.InputData.GAC['VS_rem_med']['amount']

        # FlowType, GAC_mass will be used in landfill model
        self.SpentGAC.set_FlowType('SpentGAC')
        self.SpentGAC.GAC_mass = GAC_mass

        # GAC Volume balance
        self.GAC_effluent.vol = self.Allocted_vol['GAC'].vol - self.SpentGAC.moist * 1

        # Icon Exchange Resin
        # Icon Exchange PFAS balance
        self.IonEx_effluent = Flow(self.CommonData)
        self.IonExResin = Flow(self.CommonData)
        for i in self.Inc_flow._PFAS_Index:
            self.IonExResin.PFAS[i] = self.Allocted_vol['IonEx'].PFAS[i] * self.InputData.IonEx_RemEff[i]['amount']
            self.IonEx_effluent.PFAS[i] = self.Allocted_vol['IonEx'].PFAS[i] * (1 - self.InputData.IonEx_RemEff[i]['amount'])

        # Ion Exchange Resin used
        IonEx_mass = self.Allocted_vol['IonEx'].vol / self.InputData.IonEx['Bed_vol_ratio']['amount'] * \
            self.InputData.IonEx['IonExRes_dens']['amount']
        self.IonExResin.moist = IonEx_mass * (1 - self.InputData.IonEx['ts_rem_med']['amount'])
        self.IonExResin.ts = IonEx_mass - self.IonExResin.moist
        self.IonExResin.mass = IonEx_mass
        self.IonExResin.C = self.IonExResin.ts * self.InputData.IonEx['C_rem_med']['amount']
        self.IonExResin.VS = self.IonExResin.ts * self.InputData.IonEx['VS_rem_med']['amount']

        # FlowType, GAC_mass will be used in landfill model
        self.IonExResin.set_FlowType('SpentIER')
        self.IonExResin.IonExchangeResin_mass = IonEx_mass

        # Ion Exchange Resin Volume balance
        self.IonEx_effluent.vol = self.Allocted_vol['IonEx'].vol - self.IonExResin.moist * 1

        # add to Inventory
        self.Inventory.add('RO Effluent', self.Name, 'Water', self.RO_effluent)
        self.Inventory.add('GAC Effluent', self.Name, 'Water', self.GAC_effluent)
        self.Inventory.add('IER Effluent', self.Name, 'Water', self.IonEx_effluent)

    def products(self):
        Products = {}
        Products['ROConcentrate'] = self.RO_concentrate
        Products['SpentGAC'] = self.SpentGAC
        Products['SpentIER'] = self.IonExResin
        return(Products)

    def setup_MC(self, seed=None):
        self.InputData.setup_MC(seed)

    def MC_Next(self):
        input_list = self.InputData.gen_MC()
        return(input_list)

    def report(self, normalized=False):
        report = pd.DataFrame(index=self.Inc_flow._PFAS_Index)
        if not normalized:
            report['Effluent RO'] = self.RO_effluent.PFAS
            report['RO Concentrate'] = self.RO_concentrate.PFAS
            report['Effluent GAC'] = self.GAC_effluent.PFAS
            report['Spent GAC'] = self.SpentGAC.PFAS
            report['Effluent IonExchange'] = self.IonEx_effluent.PFAS
            report['Spent IER'] = self.IonExResin.PFAS
        else:
            report['Effluent RO'] = round(self.RO_effluent.PFAS / self.Inc_flow.PFAS * 100, 2)
            report['RO Concentrate'] = round(self.RO_concentrate.PFAS / self.Inc_flow.PFAS * 100, 2)
            report['Effluent GAC'] = round(self.GAC_effluent.PFAS / self.Inc_flow.PFAS * 100, 2)
            report['Spent GAC'] = round(self.SpentGAC.PFAS / self.Inc_flow.PFAS * 100, 2)
            report['Effluent IonExchange'] = round(self.IonEx_effluent.PFAS / self.Inc_flow.PFAS * 100, 2)
            report['Spent IER'] = round(self.IonExResin.PFAS / self.Inc_flow.PFAS * 100, 2)
            report.fillna(0.0, inplace=True)
        return(report)
