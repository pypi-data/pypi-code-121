# -*- coding: utf-8 -*-
"""
Created on Wed Aug 12 21:04:20 2020

@author: msmsa
"""
import pandas as pd
from PFAS_SAT_InputData import SurfaceWaterReleaseInput
from .ProcessModel import ProcessModel


class SurfaceWaterRelease(ProcessModel):
    ProductsType = []

    def __init__(self, input_data_path=None, CommonDataObject=None, InventoryObject=None, Name=None):
        super().__init__(CommonDataObject, InventoryObject)
        self.InputData = SurfaceWaterReleaseInput(input_data_path)
        self.Name = Name if Name else 'Surface Water Release'

    def calc(self, Inc_flow):
        self.Inc_flow = Inc_flow
        # add to Inventory
        self.Inventory.add('Release', self.Name, 'Water', self.Inc_flow)

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
            report['Release'] = self.Inc_flow.PFAS
        else:
            report['Release'] = round(self.Inc_flow.PFAS / self.Inc_flow.PFAS * 100, 2)
            report.fillna(0.0, inplace=True)
        return(report)
