"""
PyRasgo Custom Errors
"""
from typing import List


### BASELINE RASGO EXCEPTION
class PyRasgoException(Exception):
    """
    Base error attributable to PyRasgo code
    """

    def __init__(self, message: any):
        super().__init__(message)
        self.message = message

    def __str__(self):
        return f"{self.__class__.__name__}: {self.message}"


### API & PACKAGE EXCEPTIONS
class APIError(PyRasgoException):
    """
    Error message returned from Rasgo API
    """


class APITimeoutWarning(APIError):
    """
    API Request Timed Out :(
    """


class PackageDependencyWarning(PyRasgoException):
    """
    Problem importing a required package dependency
    """


class ParameterValueError(PyRasgoException):
    """
    Incorrect parameter passed into a pyrasgo function
    """

    def __init__(self, param: str = None, values: List[str] = None, message: str = None):
        if not message:
            message = f"Please pass a valid value for {param}. Values are {values}"
        super().__init__(message=message)
        self.message = message


### RASGO LOGICAL EXCEPTIONS
class RasgoResourceException(PyRasgoException):
    """
    Cannot access this resource
    """


class RasgoRuleViolation(PyRasgoException):
    """
    Cannot access this resource
    """


class TransformRenderingException(PyRasgoException):
    """
    Error from Transform rendering activity
    """


### DATAWAREHOUSE EXCEPTIONS
class DWCredentialsWarning(PyRasgoException):
    """
    Missing DataWarehouse credentials
    """


class DWQueryException(PyRasgoException):
    """
    Error from DataWarehouse query activity
    """


class DWResourceException(PyRasgoException):
    """
    Error accessing Table
    """
