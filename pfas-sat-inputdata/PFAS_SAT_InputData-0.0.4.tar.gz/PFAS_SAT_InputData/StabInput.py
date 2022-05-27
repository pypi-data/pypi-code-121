# -*- coding: utf-8 -*-
"""
Created on Tue Aug 18 16:29:49 2020

@author: msmsa
"""
from .InputData import InputData
from pathlib import Path


class StabInput(InputData):
    def __init__(self, input_data_path=None):
        if input_data_path:
            self.input_data_path = input_data_path
        else:
            self.input_data_path = Path(__file__).parent / 'Data/StabInput.csv'
        # Initialize the superclass
        super().__init__(self.input_data_path)
