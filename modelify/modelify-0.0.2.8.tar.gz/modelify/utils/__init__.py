
import socket
import os
import sys
from contextlib import closing
from modelify.inputs import Image
import yaml
import os
from modelify.utils.constants import APP_FOLDER, ModelifyFile
from modelify.utils.types import SeriliazeType
from modelify.core.frameworks import Frameworks
import cloudpickle
import uuid

def message(text):
    print(text,  end='\n', flush=True)

def get_env(variable_name):
    return os.environ.get(variable_name)

def find_free_port():
    with closing(socket.socket(socket.AF_INET, socket.SOCK_STREAM)) as s:
        s.bind(('', 0))
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        return s.getsockname()[1]

def create_folder():
    os.makedirs(APP_FOLDER, exist_ok=True)


def save_requirements_file( packages):
    requirements_file = os.path.join(APP_FOLDER, "requirements.txt")
    with open(requirements_file, 'w') as f:
        f.write('\n'.join(packages))

def save_config(config_metadata):
    model_file = os.path.join(APP_FOLDER, ModelifyFile.CONFIG.file_name)
    with open(model_file, 'w') as outfile:
        yaml.dump(config_metadata, outfile)

def save_onnx_model(onnx_model):

    output_file = os.path.join(APP_FOLDER, ModelifyFile.MODEL.file_name)

    with open(output_file, "wb") as f:
        f.write(onnx_model.SerializeToString())

    return output_file 

def save_onnx_model_catboost(model):
    output_file = os.path.join(APP_FOLDER, ModelifyFile.MODEL.file_name)
    model.save_model(output_file, format="onnx")

def save_onnx_model_pytorch(model, inputs):
    if not isinstance(inputs, Image):
        raise Exception("Currently, we support computer vision model in pytorch")

    import torch.onnx 
    output_file = os.path.join(APP_FOLDER, ModelifyFile.MODEL.file_name)
    initial_input = torch.randn(1, inputs.channel, inputs.width ,inputs.height, requires_grad=True)  
   
    torch.onnx.export(model,         
         initial_input,      
         output_file,       
         export_params=True,  
         opset_version=11,    
         do_constant_folding=True,  
         input_names = ['modelInput'],   
         output_names = ['modelOutput'], 
         dynamic_axes={'modelInput' : {0 : 'batch_size'}, 'modelOutput' : {0 : 'batch_size'}}) 

def serialize(function_name, seriliaze_type):
    """_summary_

    Args:
        function_name (function): the function you implemented
        seriliaze_type (SeriliazeType): postprocess or preprocess

    Raises:
        Exception: _description_
    """
    if not SeriliazeType.has_value(seriliaze_type):
        raise Exception("Avaiable types: 'preprocess' and 'postprocess'  ")
    pickle_name = f"{seriliaze_type}.pkl"
    object_path = os.path.join(APP_FOLDER , pickle_name)
    with open(object_path, mode='wb') as file:
        cloudpickle.dump(function_name, file)

def get_supported_frameworks():
    return list(Frameworks.__members__.keys())
    