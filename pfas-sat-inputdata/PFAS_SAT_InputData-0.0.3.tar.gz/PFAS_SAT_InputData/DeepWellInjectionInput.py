# -*- coding: utf-8 -*-
"""
Created on Wed Aug 12 21:04:38 2020

@author: msmsa
"""
from .InputData import InputData
from pathlib import Path


class DeepWellInjectionInput(InputData):
    def __init__(self, input_data_path=None):
        if input_data_path:
            self.input_data_path = input_data_path
        else:
            self.input_data_path = Path(__file__).parent / 'Data/DeepWellInjectionInput.csv'
        # Initialize the superclass
        super().__init__(self.input_data_path)
