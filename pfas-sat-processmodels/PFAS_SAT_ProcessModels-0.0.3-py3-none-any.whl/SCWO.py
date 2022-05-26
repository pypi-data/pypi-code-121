# -*- coding: utf-8 -*-
"""
Created on Tue Aug 18 10:44:45 2020

@author: msmsa
"""
import pandas as pd
from .Flow import Flow
from PFAS_SAT_InputData import SCWOInput
from .ProcessModel import ProcessModel


class SCWO(ProcessModel):
    """
**************************************
Supercritical water oxidation (SCWO)
**************************************

=============================
Assumptions and Limitations:
=============================

    """
    ProductsType = ['SCWOSteam', 'SCWOSlurry']

    def __init__(self, input_data_path=None, CommonDataObject=None, InventoryObject=None, Name=None):
        super().__init__(CommonDataObject, InventoryObject)
        self.InputData = SCWOInput(input_data_path)
        self.Name = Name if Name else 'SCWO'

    def calc(self, Inc_flow):
        # Initialize the Incoming flow
        self.Inc_flow = Inc_flow

        # PFAS Balance
        self.Steam = Flow(self.CommonData)
        self.Slurry = Flow(self.CommonData)
        self.Effluent = Flow(self.CommonData)
        self.Mineralized = Flow(self.CommonData)

        for i in self.Inc_flow._PFAS_Index:
            self.Effluent.PFAS[i] = self.Inc_flow.PFAS[i] * (1 - self.InputData.ME[i]['amount'])
            self.Slurry.PFAS[i] = self.Inc_flow.PFAS[i] * self.InputData.ME[i]['amount'] * self.InputData.SCWO['frac_PFAS_to_slurry']['amount']
            self.Steam.PFAS[i] = self.Inc_flow.PFAS[i] * self.InputData.ME[i]['amount'] * self.InputData.SCWO['frac_PFAS_to_steam']['amount']
        self.Mineralized.PFAS = self.Inc_flow.PFAS - self.Effluent.PFAS - self.Slurry.PFAS - self.Steam.PFAS

        # Volume balance
        self.Slurry.vol = self.Inc_flow.vol * self.InputData.SCWO['frac_water_to_slurry']['amount']
        self.Steam.vol = self.Inc_flow.vol * self.InputData.SCWO['frac_water_to_steam']['amount']
        self.Effluent.vol = self.Inc_flow.vol - self.Slurry.vol - self.Steam.vol

        # add to Inventory
        self.Inventory.add('Effluent', self.Name, 'Water', self.Effluent)
        self.Inventory.add('Mineralized', self.Name, 'Mineralized', self.Mineralized)

    def products(self):
        Products = {}
        Products['SCWOSteam'] = self.Steam
        Products['SCWOSlurry'] = self.Slurry
        return(Products)

    def setup_MC(self, seed=None):
        self.InputData.setup_MC(seed)

    def MC_Next(self):
        input_list = self.InputData.gen_MC()
        return(input_list)

    def report(self, normalized=False):
        report = pd.DataFrame(index=self.Inc_flow._PFAS_Index)
        if not normalized:
            report['Effluent'] = self.Effluent.PFAS
            report['Slurry'] = self.Slurry.PFAS
            report['Steam'] = self.Steam.PFAS
            report['Mineralized'] = self.Mineralized.PFAS
        else:
            report['Effluent'] = round(self.Effluent.PFAS / self.Inc_flow.PFAS * 100, 2)
            report['Slurry'] = round(self.Slurry.PFAS / self.Inc_flow.PFAS * 100, 2)
            report['Steam'] = round(self.Steam.PFAS / self.Inc_flow.PFAS * 100, 2)
            report['Mineralized'] = round(self.Mineralized.PFAS / self.Inc_flow.PFAS * 100, 2)
            report.fillna(0.0, inplace=True)
        return(report)
