# !/usr/bin/env python
# coding: utf-8

from typing import List, Any

from dsframework.base.pipeline.preprocessor import ZIDS_Preprocessor
from ..schema.inputs import generatedProjectNameInputs
from ..schema.outputs import generatedProjectNameOutputs
from ..artifacts.shared_artifacts import generatedProjectNameSharedArtifacts

##
# @file
# @brief generatedClass (Preprocess) class, implements ZIDS_Preprocessor base class.
class generatedClass(ZIDS_Preprocessor):
    """! generatedClass (Preprocessor) class implements ZIDS_Preprocessor base class.

    First step of the pipeline, its main goal is to format the dataset format to the model requirements.

    Its base class ZIDS_Preprocessor declares phases based on UVM (Universal Verification Methodology) and by this it
    gives us a structured way to work in each one of the main components by overriding and implementing those phases
    in this class.

    Important note:
    Those methods are divided into two groups, the ones that run from the ZIDS_Component.__init__() and
    those that run from ZIDS_Component.execute() method, use them based on the required execution order.

    In the __init__() we have the following called:
    - build
    - config
    - config_from_json
    - connect

    In the execute(), we call the following:
    - reset
    - pre_run
    - run
    - post_run
    - evaluate
    """

    def __init__(self, artifacts: generatedProjectNameSharedArtifacts = None):
        """! generatedClass (Preprocess) initializer

        Args:
            artifacts(generatedProjectNameSharedArtifacts): Shared artifacts instance.
        """

        ##
        # @hidecallgraph @hidecallergraph
        super().__init__(artifacts)

    def normalize_input(self, **kwargs: Any) -> generatedProjectNameInputs:
        """! Converts dataset to generatedProjectNameInputs

        Args:
            **kwargs: Loaded dataset.
        Returns:
            The loaded dataset in generatedProjectNameInputs datatype.
        """
        return generatedProjectNameInputs(**kwargs)

    def config(self):
        """! Config method called from ZIDS_Component.__init__()

        Method not implemented, ready for your implementation, see more information in class description.
        """
        pass

    def connect(self):
        """! Connect method, called from ZIDS_Component.__init__().

        Method not implemented, ready for your implementation, see more information in class description.
        """

        ##
        #@hidecallgraph @hidecallergraph

        super().connect()

    def reset(self, text: str = '', hints: List[Any] = []):
        """! Reset data members, called from ZIDS_Component.execute() method.

        Method not implemented, see more information in class description.

        Args:
            text: str
            hints: List[Any]
        """

        ##
        # For example:
        # @code {.py}
        # def reset(self, text: str, raw_input: Any):
        #
        #     self.text = ""
        #     self.hints = raw_input.hints
        #
        # @endcode

        pass

    def get_from_regex(self):
        """! Get a predefined key from common/regex_handler.py

        Method not implemented, ready for your implementation.
        """
        ##
        # For example:
        # @code{.py}
        # from dsframework.base.common import RegexHandler
        #
        # def get_from_regex(self):
        #    return RegexHandler.url.findall("www.zoominfo.com")
        # @endcode

        pass

    def preprocess(self, raw_input: Any):
        """! Implement method to return a list of predictable objects.

        Args:
            raw_input: input to the pipeline, after normalization.

        Returns:
            List[ZIDS_Predictable] - Not implemented yet.

        Raises:
            NotImplementedError
        """

        ##
        # For example, minimum return as-is:
        # @code{.py}
        # def preprocess(self, raw_input: Any):
        #
        #     return raw_input
        # @endcode

        raise NotImplementedError
