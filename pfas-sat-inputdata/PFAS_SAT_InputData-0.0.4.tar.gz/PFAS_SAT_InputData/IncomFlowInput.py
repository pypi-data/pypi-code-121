# -*- coding: utf-8 -*-
"""
Created on Fri Nov 22 11:56:34 2019

@author: msardar2
"""
from .InputData import InputData
from pathlib import Path


class IncomFlowInput(InputData):
    def __init__(self, input_data_path=None):
        if input_data_path:
            self.input_data_path = input_data_path
        else:
            self.input_data_path = Path(__file__).parent / 'Data/IncomFlowInput.csv'
        # Initialize the superclass
        super().__init__(self.input_data_path)
