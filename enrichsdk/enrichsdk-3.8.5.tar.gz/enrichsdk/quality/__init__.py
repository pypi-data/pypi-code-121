"""Module to set and implement `expectations` on dataframes. Note
that this is development mode and meant to be a preview.

As systems are getting automated, and processing more data everyday,
it is hard to keep track of correctness of the entire system. We use
expectations to make sure that decision modules such as ML/statistics
code is being correctly fed.

An expectation is a set of structural rules that datasets should
satisfy. It could be superficial such as names or order of columns. It
could go deeper and specify the statistical attributes of the input.

This module help implement a specification. An example is shown
below::

        expectations = [
            {
                'expectation': 'table_columns_exist',
                'params': {
                    'columns': ['Make', 'YEAR', 'Model', 'hello']
                }
            },
            {
                'expectation': 'table_columns_exist_with_position',
                'params': {
                    'columns': {
                        'Make': 1
                    }
                }
            }
        ]


Each expectation has a name, and arbitrary parameters. The first
expectation shown above will for example, check if the specified
columns exist in the dataframe being evaluated. The result will be as
shown below::

        {
            "expectation": "table_columns_exist_with_position",
            "passed": true,
            "description": "Check whether columns exist (in particular order)",
            "version": "v1",
            "timestamp": "2020-01-04T11:43:03+05:30",
            "frame": "v2scoring",
            "meta": {
                "node": "data.acmeinc.com",
                "pipeline": "AcmeLending",
                "transform": "ScoringModule",
                "runid": "scoring-20200104-114137",
                "start_time": "2020-01-04T11:41:37+05:30"
            }
        }


This is stored as part of the state and dumped in the metadata for
each run.

The expectations are used as follows::

        expectationsfile=os.path.join(thisdir, "expectations.py")
        checker = TransformExpectation(self,
                                       mode='validation',
                                       filename=expectationsfile)

        result = checker.validate(df,selector=selector)
        state.add_expectations(self, name, result)

"""

from .base import *
from .expectations import *
from .exceptions import *
from .transforms import *
