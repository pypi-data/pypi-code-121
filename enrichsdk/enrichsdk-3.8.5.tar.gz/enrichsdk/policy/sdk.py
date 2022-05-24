import os
import sys
from enrichsdk.policy import *


class PipelineRunResource(BaseResource):
    """
    Resource that implements access to pipeline output
    """

    def __init__(self, run, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.run = run

    def name(self):
        return "PipelineRun::{}::{}".format(self.run.config.name, self.run.name)


class SimpleFilterEngine(BasePolicyEngine):
    """
    This applies the policy on a collection of dataframes
    """

    NAME = "SimpleFilterPolicy"

    def __init__(self, *args, **kwargs):
        self.config = kwargs.pop("config")
        super().__init__(*args, **kwargs)
        self.name = "SingleApplicationPolicy"
        self.filter_handlers = {
            "by_column_value": self.filter_by_column_value,
            "by_column_range": self.filter_by_column_range,
        }

    def filter_by_column_value(self, principal, resource, params):
        """
        Filter the data by value of a particular column. The
        column and the value is specified in policy

        Args:
          principal (obj): Principal object
          resource (obj): Resource object
          params (dict): Filter parameters
        """
        pass

    def filter_by_column_range(self, principal, resource, params):
        """
        Filter the data by the range of values of a particular
        column. The column and the value is specified in policy.

        Args:
          principal (obj): Principal object
          resource (obj): Resource object
          params (dict): Filter parameters
        """
        pass
