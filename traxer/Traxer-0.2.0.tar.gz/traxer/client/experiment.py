from os.path import dirname
import sys
import os
import subprocess

from bokeh.embed import json_item
import json
import getpass
import psutil

class Experiment():

    def __init__(self, session, id_exp=None, path=None, name=None):
        self.session = session

        if id_exp is None and (path is None or name is None):
            raise ValueError("Please specify one of 'id_exp' or 'name' and 'path' for this experiment.")

        if id_exp is None:
            self.id = self.create(path, name)
        else:
            self.load(id_exp)
        
    def create(self, path, name):
        """Create a new experiment

        Args:
            path (str): Path of the directory in which the experiment will be stored
            name (str): Name of the experiment

        Raises:
            ValueError: If the experiment cannot be created (more details in the error message)

        Returns:
            str: The id of the created experiment
        """
        tmp_folder = os.getcwd()

        try:
            script_name = psutil.Process().cmdline()[1]
        except:
            script_name = ""
            
        folder = dirname(script_name)
        if folder != "":
            os.chdir(folder)
        try:
            commit_hash = subprocess.check_output(["git", "rev-parse", "HEAD"]).decode("ascii").strip("\n")
        except:
            commit_hash = "None"

        os.chdir(tmp_folder)
        
        r = self.session.api_call(
            "new_run", 
            data={
                "folder": path,
                "name": name,
                "user": getpass.getuser(),
                "script": script_name,
                "commit_hash": commit_hash
            })

        if not r["success"]:
            raise ValueError(f"Can't create new run ({r['message']})")
        return r["id"]

    def delete(self):
        """Delete the current run

        Raises:
            ValueError: If the run cannot be deleted (more details in the error message)
        """
        r = self.session.api_call(
            "delete_run",
            data={
                "ids": self.id
            })
        
        if not r["success"]:
            raise ValueError(f"Can't delete run {self.id} ({r['message']})")
    
    def load(self, id_exp):
        """Load an experiment according to its id in the current object

        Args:
            id_exp (str): Experiment id

        Raises:
            ValueError: If the experiment cannot be loaded (more details in the error message)
        """
        r = self.session.api_call(
            "get_run",
            data={
                "id": id_exp
            })

        if not r["success"]:
            raise ValueError(f"Can't load experiment {id_exp} ({r['message']})")

        self.id = id_exp
        self.name = r["name"]
    
    def log_params(self, params):
        """Log a yaml configuration file to the experiment

        Args:
            params (dict): Dictionary of parameters

        Returns:
            dict: Server response
        """
        return self.session.api_call(
            "log_param",
            data={
                "id": self.id,
                "params_dict": json.dumps(params)
            }
        )

    def log_metric(self, metric_name, metric_value):
        """Log a metric. Each call to this function will add the metric value to the list of the older one.

        Args:
            metric_name (str): The name of the metric
            metric_value (foat): Value of the metric

        Returns:
            dict: Server response
        """
        return self.session.api_call(
            "log_metric", 
            data={
                "id": self.id,
                "metric_name": metric_name,
                "metric_value": metric_value
            })
    
    def log_artifact(self, file):
        """Log a file to the current experiment.

        Args:
            file (str): Path to the artefact

        Returns:
            dict: Server response
        """

        return self.session.api_call(
            "log_artifact", 
            data={
                "id": self.id
            },
            file=file
        )
    
    def log_graph(self, name, graph):
        """Log a graph to the experiment

        Args:
            name (str): Name of the graph
            graph (Figure): A bokeh graph

        Returns:
            dict: Server response
        """
        
        return self.session.api_call(
            "log_graph", 
            data={
                "id": self.id,
                "name": name, 
                "graph": json.dumps(json_item(graph))
            }
        )