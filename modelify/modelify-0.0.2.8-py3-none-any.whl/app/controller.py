from genericpath import isfile
from pathlib import Path
import json
import os
import onnxruntime as rt
import builtins
from pydantic import BaseModel, create_model
from pydantic.schema import schema
from re import sub
import logging
import yaml
from modelify.utils.constants import ModelifyFile, APP_FOLDER


def snake_case(s):
  return '_'.join(
    sub('([A-Z][a-z]+)', r' \1',
    sub('([A-Z]+)', r' \1',
    s.replace('-', ' '))).split()).lower()

BASE_DIR = os.getcwd()


class ModelifyController:
    def __init__(self):
        self.config = None
        self.model_path = None
        self.model_folder_path = APP_FOLDER
        self.allowed_type = ["integer", "long", "float", "string", "boolean"]
        self.initialize()
        
    
    def initialize(self):
        files = os.listdir(self.model_folder_path)
        if ModelifyFile.MODEL.file_name not in  files:
            raise Exception("Model file does not exist")
        if ModelifyFile.CONFIG.file_name not in files:
            raise Exception("Model config file does not exist")   

        self.model_path = os.path.join(self.model_folder_path, ModelifyFile.MODEL.file_name)
        ## configs 
        config_file_path = os.path.join(self.model_folder_path, ModelifyFile.CONFIG.file_name)

        with open(config_file_path, "r") as yamlfile:
            self.config = yaml.load(yamlfile, Loader=yaml.Loader)

    @property
    def title(self):
        return self.config["title"] 

    @property
    def model_inputs(self):
        return self.config["inputs"]

    @property
    def model_input_type(self):
        return self.config["input_type"]

    @property
    def model_preprocess(self):
        return self.config["preprocess"]

    @property
    def model_postprocess(self):
        return self.config["postprocess"]

    @property
    def external_file(self):
        return self.config["external_file"]


    @staticmethod
    def gettype(name):
        t = getattr(builtins, name)
        if isinstance(t, type):
            return t
        raise ValueError(name)

    def inputs_to_pydantic(self):
        if self.model_input_type != "TABULAR":
            raise Exception("Input type should be TABULAR")
        fields = self.inputs_to_dict()
        return create_model('Inputs', __base__= BaseModel, **fields)

    def inputs_to_dict(self):
        result= dict()
        for inp in self.model_inputs:
            if inp["type"] not in self.allowed_type:
                raise Exception(f"Excepted ({self.allowed_type}), got {inp['type']}")
            if inp["type"] == "integer" or inp["type"] == "long":
                input_type = "int"
            elif inp["type"] == "string":
                input_type = "str"
            else:
                input_type = inp["type"]

            result[snake_case(inp["name"])] = (self.gettype(input_type), None)
        return result




