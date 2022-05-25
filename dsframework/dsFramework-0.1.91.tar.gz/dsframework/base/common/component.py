#!/usr/bin/env python
# coding: utf-8

##
# @file
# @brief ZIDS_Component base class for all pipeline components.

from typing import List, Any


class ZIDS_Component:
    """! ZIDS_Component is the base class for the pipeline components:

    ZIDS_Preprocessor, Predictor, Forcer and ZIDS_Postprocessor.

    It declares phases based on UVM (Universal Verification Methodology) and by this gives us a structured
    way to work in each one of the main components by overriding and implementing those phases.


    **Important note:**

    Those methods are divided into **two groups**, the ones that run from the **@ref __init__()** and those
    that run from the **execute()** method, use them based on the required execution order.
    """

    def __init__(self, artifacts=None) -> None:
        """ZIDS_Component class initializer, runs during __init__.

        It runs the following UVM based phases:
        - build
        - config
        - config_from_json
        - connect
        """

        ## Shared artifacts instance.
        self.artifacts = artifacts
        self.build()
        self.config()
        self.config_from_json()
        self.connect()

    def __call__(self, predictables: List[Any], **kwargs):
        """Runs the execute method."""
        return self.execute(predictables, **kwargs)

    def execute(self, predictables: List[Any], **kwargs) -> List[Any]:
        """Executes additional UVM phases.

        Includes:
        - reset
        - pre_run
        - run
        - post_run
        - evaluate
        """
        self.reset(predictables)
        self.pre_run(predictables)
        self.run(predictables)
        self.post_run(predictables)
        self.evaluate(predictables)
        return predictables

    def build(self):
        """Called from __init__,  not implemented, override to implement."""
        pass

    def config(self):
        """Called from __init__,  not implemented, override to implement."""
        pass

    def config_from_json(self):
        """Called from __init__,  not implemented, override to implement."""
        pass

    def connect(self):
        """Called from __init__,  not implemented, override to implement."""
        pass

    def reset(self, predictables: List[Any]):
        """Called from execute,  not implemented, override to implement.

        Args:
            predictables: List[Any] - List of predictable objects.
        """
        pass

    def pre_run(self, predictables: List[Any]):
        """Called from execute,  not implemented, override to implement.

        Args:
            predictables: List[Any] - List of predictable objects.
        """
        pass

    def run(self, predictables: List[Any]):
        """Called from execute,  not implemented, override to implement.

        Args:
            predictables: List[Any] - List of predictable objects.
        """
        pass

    def post_run(self, predictables: List[Any]):
        """Called from execute,  not implemented, override to implement.

        Args:
            predictables: List[Any] - List of predictable objects.
        """
        pass

    def evaluate(self, predictables: List[Any]):
        """Called from execute,  not implemented, override to implement.

        Args:
            predictables: List[Any] - List of predictable objects.
        """
        pass
