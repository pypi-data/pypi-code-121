# -*- coding: utf-8 -*-
"""
Created on Wed Aug 12 21:04:20 2020

@author: msmsa
"""
import pandas as pd
from PFAS_SAT_InputData import DeepWellInjectionInput
from .ProcessModel import ProcessModel


class DeepWellInjection(ProcessModel):
    ProductsType = []

    def __init__(self, input_data_path=None, CommonDataObject=None, InventoryObject=None, Name=None):
        super().__init__(CommonDataObject, InventoryObject)
        self.InputData = DeepWellInjectionInput(input_data_path)
        self.Name = Name if Name else 'Deep Well Injection'

    def calc(self, Inc_flow):
        self.Inc_flow = Inc_flow
        # add to Inventory
        self.Inventory.add('Deep Well Injection', self.Name, 'Injection Well', self.Inc_flow)

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
            report['Deep Well Injection'] = self.Inc_flow.PFAS
        else:
            report['Deep Well Injection'] = round(self.Inc_flow.PFAS / self.Inc_flow.PFAS * 100, 2)
            report.fillna(0.0, inplace=True)
        return(report)
