import os
from modelify.utils.constants import MODELIFY_TOKEN_VALIDATION_URL
import requests
import json
from modelify.utils.credential import Credential
from modelify.utils import message
from pyngrok import ngrok
import nest_asyncio
import uvicorn

from modelify.utils.constants import APP_FOLDER, ModelifyFile
from modelify.core.frameworks import Frameworks
from modelify.core.client import ModelifyClient
import modelify.version as __version__
from modelify.core.inference import ModelInference
from modelify.app import create_fastapi
import shutil
from modelify.utils import find_free_port, create_folder, save_config, save_requirements_file
import warnings
warnings.filterwarnings("ignore")

client = ModelifyClient()


def connect(api_key):
    """ Function to connect with Modelify Cloud
    Args:
        api_key (str): API Token Key (provided by Modelify Cloud)
    """
    client.credential.api_key = api_key
    headers = {"api-token": f"{client.credential.api_key}", "Content-Type": "application/json"}
    req = requests.get(MODELIFY_TOKEN_VALIDATION_URL, headers =headers)
    if req.status_code == 200:
        print("Connection established. ")
    else:
        print("Token is not valid.")



def deploy( inference: ModelInference, app_uid,  title:str="Modelify Application", requirements:list=[], external_file:bool =False):
    message("Model is converting...")
    inference.export_model()
    # zip_folder()
       # seriliaze functions

    configs = inference.get_model_config()
    upload_types = inference.get_base_upload_types()
    configs["title"] = title

    if len(requirements) > 0 :
        configs["requirements"] = requirements
        upload_types["REQUIREMENTS"] = True
        save_requirements_file(requirements)

    if external_file:
        shutil.copyfile(ModelifyFile.EXTERNAL_FILE.file_name, os.path.join(APP_FOLDER, ModelifyFile.EXTERNAL_FILE.file_name))
        configs["external_file"] = True
        upload_types["EXTERNAL_FILE"] = True

    save_config(configs)
    message("Model converted successfully!")
    message("Uploading process is starting..")
    client.upload_pipeline(upload_types=upload_types, app_uid=app_uid, configs=configs)
    message("Done")
        

def run(inference: ModelInference,  title:str="Modelify Application", requirements=[], port:int=8080, tunnel = True, host="127.0.0.1", proxy_headers=True):
    """ This function creates an application on your local environment
    Args:
        inference (ModelInference): Model Inference
        tittle (str): Title of Application
    """
    message("Model is converting...")    
    inference.export_model() 
    
    configs = inference.get_model_config()
    configs["title"] = title

    if len(requirements) > 0 :
        configs["requirements"] = requirements
        save_requirements_file(requirements)

    save_config(configs)
    message("Modelify API is creating...") 
    run_server(port, tunnel, host, proxy_headers)  


def run_server(port:int=8080, tunnel = True, host="127.0.0.1", proxy_headers=True):
    app = create_fastapi()
    if port is None:
        port = find_free_port()
    if tunnel:
        ngrok_tunnel = ngrok.connect(port)
        nest_asyncio.apply()
    uvicorn.run(app, port=port, host=host, proxy_headers=proxy_headers)

def pull(app_uid:str, version=None):
    message("Download process is starting..") 
    create_folder() 
    client.pull_model(app_uid=app_uid, version=version )
    message("Download process completed.")
    

__all__ = [
    "connect",
    "deploy",
    "run",
    "run_server",
    "pull",
    "Frameworks",
    "ModelInference",
    "__version__"
]







