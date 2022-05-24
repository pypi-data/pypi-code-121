"""
Dummy task 
"""

import time
import logging
from enrichsdk.tasks import Task

logger = logging.getLogger("app")

__all__ = ["DummyTask"]


class DummyTask(Task):
    """
    Backsup code and data as required
    """

    NAME = "DummyTask"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.name = "Dummy"
        self.testdata = {
            "data": {},
            "conf": {"enable_extra_args": False, "args": {"sleep": 10}},
        }

        self.supported_extra_args = [
            {
                "name": "jobid",
                "description": "Export JobID",
                "type": "str",
                "required": True,
                "default": "22832",
            }
        ]

    def validate_args(self, what, state):
        """
        Validate args.

        Example::

            "args": {
                 "sleep": 10
            }

        """
        args = self.args
        fail = False
        msg = ""
        if "sleep" not in args:
            fail = True
            msg += "Argument passed does not have/is invalid sleep value\n"

        if fail:
            logger.error(
                "Invalid params",
                extra=self.config.get_extra({"transform": self.name, "data": msg}),
            )
            raise Exception("Invalid params")

    def run(self, state):
        """
        Run the backup task
        """

        # Get the number of seconds to sleep for
        sleep_val = self.args["sleep"]

        # Check if the sleep argument is an integer
        assert isinstance(sleep_val, int)

        time.sleep(sleep_val)

        logger.debug(
            "Sleep task complete.",
            extra=self.config.get_extra(
                {
                    "transform": self.name,
                }
            ),
        )
