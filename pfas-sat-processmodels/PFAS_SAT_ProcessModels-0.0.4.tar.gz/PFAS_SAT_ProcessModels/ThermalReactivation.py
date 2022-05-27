# -*- coding: utf-8 -*-
"""
Created on Tue Aug 18 10:44:45 2020

@author: msmsa
"""
import pandas as pd
from .Flow import Flow
from PFAS_SAT_InputData import ThermalReactivationInput
from .ProcessModel import ProcessModel


class ThermalReactivation(ProcessModel):
    """
***********************
Thermal Reactivation
***********************


=============================
Assumptions and Limitations:
=============================

    """
    ProductsType = []

    def __init__(self, input_data_path=None, CommonDataObject=None, InventoryObject=None, Name=None):
        super().__init__(CommonDataObject, InventoryObject)
        self.InputData = ThermalReactivationInput(input_data_path)
        self.Name = Name if Name else 'Thermal Treatment'

    def calc(self, Inc_flow):
        # Initialize the Incoming flow
        self.Inc_flow = Inc_flow

        # PFAS Balance
        self.ReactivatedGAC = Flow(self.CommonData)
        self.Exhaust = Flow(self.CommonData)
        self.Mineralized = Flow(self.CommonData)
        for i in self.Inc_flow._PFAS_Index:
            self.Exhaust.PFAS[i] = self.Inc_flow.PFAS[i] * (1 - self.InputData.ME[i]['amount']) * (1 - self.InputData.Frac_to_GAC[i]['amount'])
            self.Mineralized.PFAS[i] = self.Inc_flow.PFAS[i] * self.InputData.ME[i]['amount']
            self.ReactivatedGAC.PFAS[i] = self.Inc_flow.PFAS[i] - self.Mineralized.PFAS[i] - self.Exhaust.PFAS[i]

        # Combustion Residual
        self.ReactivatedGAC.ts = self.Inc_flow.VS * self.InputData.Reac_param['frac_vs_to_GAC']['amount'] + (self.Inc_flow.ts - self.Inc_flow.VS)
        self.ReactivatedGAC.VS = self.Inc_flow.VS * self.InputData.Reac_param['frac_vs_to_GAC']['amount']
        self.ReactivatedGAC.C = self.Inc_flow.C * self.InputData.Reac_param['frac_vs_to_GAC']['amount']
        self.ReactivatedGAC.mass = self.ReactivatedGAC.ts / self.InputData.Reac_param['GAC_ts_cont']['amount']
        self.ReactivatedGAC.moist = self.ReactivatedGAC.mass - self.ReactivatedGAC.ts

        # add to Inventory
        self.Inventory.add('Exhaust', self.Name, 'Air', self.Exhaust)
        self.Inventory.add('Mineralized', self.Name, 'Mineralized', self.Mineralized)
        self.Inventory.add('Reactivated GAC', self.Name, 'Reactivated GAC', self.ReactivatedGAC)

    def products(self):
        Products = {}
        return(Products)

    def setup_MC(self, seed=None):
        self.InputData.setup_MC(seed)

    def MC_Next(self):
        input_list = self.InputData.gen_MC()
        return(input_list)

    def report(self, normalized=False):
        report = pd.DataFrame(index=self.Inc_flow._PFAS_Index)
        if not normalized:
            report['Air Emission'] = self.Exhaust.PFAS
            report['Reactivated GAC'] = self.ReactivatedGAC.PFAS
            report['Mineralized'] = self.Mineralized.PFAS
        else:
            report['Air Emission'] = round(self.Exhaust.PFAS / self.Inc_flow.PFAS * 100, 2)
            report['Reactivated GAC'] = round(self.ReactivatedGAC.PFAS / self.Inc_flow.PFAS * 100, 2)
            report['Mineralized'] = round(self.Mineralized.PFAS / self.Inc_flow.PFAS * 100, 2)
            report.fillna(0.0, inplace=True)
        return(report)
