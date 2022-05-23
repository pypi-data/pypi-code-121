from distutils.command.config import config
import logging
import os
import socket
import traceback
from typing import Any, Dict

from .backend import NoBackend, SqlServerBackend
from .params import ParameterCollection
from .function import FunctionExecution
from .powershell import PowershellExecution
from .r import RExecution
from .sql import StoredProcedureExecution
from .email import EmailExecution
from .task_execution import TaskExecution

class JobException(Exception): pass

class UserExitException(JobException):
    def __init__(self, status):
        self.status = status

class JobExecution:
    """
    Context manager for logging job executions.
    """
    def __init__(self, job_name):
        
        self.job_name = job_name
        self.backend = NoBackend()
        self.environment_name = socket.gethostname()
        self.id = None
        self.status = "Started"
        self.error_message = ""
        self.global_parameters = dict()
        self.on_error = None
        
        self.configure()

    def configure(self):
        if os.path.exists("robojob.yml"):
            import yaml
            with open("robojob.yml", 'rb') as doc:
                config = yaml.safe_load(doc)
        else:
            config = dict()

        if "environment" in config:
            self.environment_name = config["environment"]

        if "path" in config:
            os.environ["PATH"] += os.pathsep + os.pathsep.join(config["path"])

        if "backend" in config:
            if "connection string" in config["backend"]:
                import pyodbc
                connection = pyodbc.connect(config["backend"]["connection string"], autocommit=True)
                self.backend = SqlServerBackend(connection)

        if "parameters" in config:
            for key, value in config["parameters"].items():
                self[key] = value

        self["job_name"] = self.job_name

    def __enter__(self):
        self.backend.before_job_execution(self)
        if self.id is None:
            logging.error(f"[job {self.id}] No job execution id assigned")
            raise JobException("No job execution id assigned")
        logging.info(f"[job {self.id}] Job started")
        self["job_execution_id"] = self.id
        return self

    def __exit__(self, exc_type, exc_value, exc_tb):
        return_value = None
        if exc_value:
            if exc_type == UserExitException:
                self.status = exc_value.status
                return_value = True
            else:
                self.status = "Failed"
                self.error_message = str(exc_value) + "\r\n" + "\r\n".join(traceback.format_tb(exc_tb))
                if self.on_error:
                    try:
                        self.process_task_execution(self.on_error)
                    except:
                        logging.warn(f"[job {self.id}] Suppressing exception from task execution {self.on_error.id}")                
        else:
            self.status = "Completed"
        logging.info(f"[job {self.id}] Job ended with status '{self.status}'")
        self.backend.after_job_execution(self) 
        self.backend.close()
        return return_value

    def __setitem__(self, key, value):
        logging.debug(f"Setting parameter {key} = {repr(value)}")
        self.global_parameters[key] = value

    def __getitem__(self, key):
        return self.global_parameters[key]

    def exit(self, status="Completed"):
        raise UserExitException(status)

    def process_task_execution(self, task_execution : TaskExecution, local_parameters : Dict = {}):
        "Process a task execution in the context of the job execution."
        self.bind(task_execution, local_parameters)
        self.backend.before_task_execution(self, task_execution)
        logging.info(f"[task {task_execution.id}] Task starting: {task_execution}")
        try:
            task_execution.execute()
        except Exception as e:
            task_execution.error_message = str(e)
            task_execution.status = "Failed"
            logging.error(f"[{task_execution.id}] Task failed: {task_execution.error_message}")
            self.backend.after_task_execution(self, task_execution)
            raise
        task_execution.status = "Completed"
        logging.info(f"[task {task_execution.id}] Task completed")
        self.backend.after_task_execution(self, task_execution)
        return self
        
    def bind(self, task_execution : TaskExecution, local_parameters : Dict):
        "Collect all parameter values and bind the parameters of the task"
        parameters = ParameterCollection()
        parameters.update(self.global_parameters)
        parameters.update(local_parameters)
        parameters["job_execution_id"] = self.id
        parameters["status"] = self.status
        parameters["error_message"] = self.error_message
        parameters["task_execution_id"] = task_execution.id
        task_execution.bind_parameters(parameters)

    def add_error_email(self, sender, recipients, subject, content, recipients_cc=[],):
        self.on_error = EmailExecution(sender=sender,
                                      recipients=recipients,
                                      subject=subject,
                                      content=content,
                                      recipients_cc=recipients_cc)
                                      
    def execute(self, function, **local_parameters):
        "Execute a function in the context of the job"
        self.process_task_execution(FunctionExecution(function), local_parameters)

    def execute_procedure(self, connection, schema_name, *procedure_names, **local_parameters):
        "Execute a stored procedure in the context of the job"
        for procedure_name in procedure_names:
            self.process_task_execution(StoredProcedureExecution(connection, schema_name, procedure_name), local_parameters)

    def execute_r(self, *script_names, **local_parameters):
        "Execute an R script in the context of the job"
        for script_name in script_names:
            self.process_task_execution(RExecution(script_name), local_parameters)

    def execute_powershell(self, *script_names, **local_parameters):
        "Execute a powershell script in the context of the job"
        for script_name in script_names:
            self.process_task_execution(PowershellExecution(script_name), local_parameters)

    def send_email(self,
                   sender,
                   recipients,
                   subject,
                   content,
                   recipients_cc=[],):
        "Execute a powershell script in the context of the job"
        self.process_task_execution(EmailExecution(sender=sender,
                                                  recipients=recipients,
                                                  subject=subject,
                                                  content=content,
                                                  recipients_cc=recipients_cc),
                                                  )
