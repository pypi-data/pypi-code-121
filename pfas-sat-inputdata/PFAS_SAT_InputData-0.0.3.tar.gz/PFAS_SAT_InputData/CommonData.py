# -*- coding: utf-8 -*-
"""
Created on Thu Jul 23 18:27:22 2020

@author: Mojtaba Sardarmehni
"""
from .InputData import InputData
from pathlib import Path


class CommonData(InputData):
    # waste Materials
    WasteMaterials = ['FoodWaste', 'Compost', 'ADLiquids', 'ADSolids',
                      'MSW', 'CombustionResiduals', 'CompostResiduals',
                      'ContaminatedSoil', 'C_DWaste',
                      'AFFF_Sulfonate', 'AFFF_Fluorotelomer',
                      'LFLeachate', 'ContaminatedWater', 'ContactWater', 'WWTEffluent',
                      'RawWWTSolids', 'DewateredWWTSolids', 'DriedWWTSolids', 'WWTScreenRejects',
                      'SCWOSteam', 'SCWOSlurry',
                      'SpentGAC', 'ROConcentrate', 'StabilizedSoil',
                      'SpentIER']

    # PFAS Index
    PFAS_Index = ['PFOA', 'PFOS', 'PFBA', 'PFPeA', 'PFHxA', 'PFHpA',
                  'PFNA', 'PFDA', 'PFBS', 'PFHxS', '5:3FTCA',
                  '6:2FTCA', '7:3FTCA', '6:2FTS', 'MeFBSAA',
                  'nMeFOSAA', 'PFBSA', 'PFPeS']

    def __init__(self, input_data_path=None):
        if input_data_path:
            self.input_data_path = input_data_path
        else:
            self.input_data_path = Path(__file__).parent / 'Data/CommonData.csv'

        # Initialize the superclass
        super().__init__(self.input_data_path)
