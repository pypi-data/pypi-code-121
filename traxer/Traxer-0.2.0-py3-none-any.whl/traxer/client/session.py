from .experiment import Experiment
import requests
from urllib.parse import urlparse, urljoin
from yaml import load, Loader
from os.path import join, dirname, basename
import json

class Session():

    def __init__(self, url):
        with open(join(dirname(__file__), "api_calls.yaml")) as f:
            self.api_calls = load(f, Loader=Loader)
        self.url = url

        if not self._check_connection():
            raise ConnectionError("Can't connect to the server")
    
    def get_url(self, path):
        return urljoin(self.url, path)
    
    def api_call(self, func_name, data=None, file=None):
        """Carry an API call to the xpipe server.

        Args:
            func_name (str): Function to execute
            data (dict, optional): Argument of the function (can be any jsonizable object, but is proabably a dictionary). Defaults to None.
            file (str, optional): Path to a file to send to the server. Defaults to None.

        Returns:
            response (dict): Server response
        """
        url = self.api_calls[func_name]
        url = self.get_url(url)
        if file is None:
            return requests.post(url, data=json.dumps(data), headers={'Content-Type': 'application/json'}).json()

        with open(file, "rb") as f:
            file = { 
                "file": (basename(file), f, "application/octet-stream"), 
                "json": ("data", json.dumps(data), "application/json")
            }
            return requests.post(url, files=file).json()
            
    def _check_connection(self):
        try:
            return self.api_call("check")["success"] == True
        except:
            return False

    # Handle runs
    def start_run(self, path, name):
        """Begin an experiment

        Args:
            path (str): Path to the directory in which the experiment will be saved
            name (str): Name of the experiment

        Returns:
            experiment (Experiment): An Experiment object
        """
        return Experiment(self, path=path, name=name)

    def get_run(self, id_exp):
        """Get an experiment according to its id

        Args:
            id_exp (str): Experiment id

        Returns:
            experiment (Experiment): The corresponding experiment
        """
        return Experiment(self, id_exp=id_exp)
    
    def delete_run(self, id_exp):
        """Delete an experiment according to its id

        Args:
            id_exp (str): Experiment id
        """
        exp = self.get_run(id_exp)
        if exp is not None:
            exp.delete()
    
    # Handle folders
    def new_folder(self, path):
        """Create a new folder

        Args:
            path (str): Path of the new folder

        Returns:
            response (dict): Server response
        """
        return self.api_call(
            "new_folder", 
            data={
                "path": path
            })
    
    def delete_folder(self, path):
        """Delete a folder

        Args:
            path (str): Path of the folder

        Returns:
            response (dict): Server response
        """
        return self.api_call(
            "delete_folder",
            data={
                "path": path
            })
    
    def rename_folder(self, path, new_name):
        """Rename a folder

        Args:
            path (str): Path of the folder to rename
            new_name (str): New name of the folder

        Returns:
            response (dict): Server response
        """
        return self.api_call(
            "rename_folder", 
            data={
                "path": path,
                "new_name": new_name
            })