 # !/usr/bin/env python
# coding: utf-8

##
# @file
# @brief Postprocessor class, implemented ZIDS_Postprocessor base.

from dsframework.base.pipeline.predictables.predictable import ZIDS_Predictable
from typing import List, Union

from dsframework.base.pipeline.postprocessor import ZIDS_Postprocessor
from ..artifacts.shared_artifacts import generatedProjectNameSharedArtifacts
from ..schema.outputs import generatedProjectNameOutputs


class generatedClass(ZIDS_Postprocessor):
    """generatedClass class (Postprocessor) implements ZIDS_Postprocessor base class.
    Last step of the pipeline, its main focus is to return the results in the required format.
    """

    def __init__(self, artifacts: generatedProjectNameSharedArtifacts = None) -> None:
        """! generatedClass class (Postprocessor) initializer

        Args:
            artifacts(generatedProjectNameSharedArtifacts): Shared artifacts instance.
        """

        ##
        # @hidecallgraph @hidecallergraph
        super().__init__(artifacts)

    def config(self):
        """Implement here configurations required on Preprocess step. Overrides ZIDS_Component.config()"""
        pass

    def normalize_output(self, predictables: Union[ZIDS_Predictable, List[ZIDS_Predictable]]) -> Union[generatedProjectNameOutputs, List[generatedProjectNameOutputs]]:
        """! Converts received predictable objects to generatedProjectNameOutputs datatype.

        Args:
            predictables: List[ZIDS_Predictable] - Predictable objects, the results from the model.

        Returns:
            generatedProjectNameOutputs: List[generatedProjectNameOutputs] - Results converted to Outputs format.
        """

        output: generatedProjectNameOutputs = ''
        isList = isinstance(predictables, list)
        if isList:
            output: List[generatedProjectNameOutputs] = []
        if isList:
            if predictables and len(predictables):
                for item in predictables:
                    output.append(self.get_output_object(item))
        else:
            output = self.get_output_object(predictables)
        return output

    def get_output_object(self, predictable):
        """! Parse a single predictable item, needs to be implemented.

        Args:
            predictable: ZIDS_Predictable - Single predictable object.

        Returns:
            generatedProjectNameOutputs: generatedProjectNameOutputs - Parsed results

        Raises:
            NotImplementedError

        """

        ##
        # Implementation example:
        # @code{.py}
        # prob = predictable[-1]
        # pred = False
        #
        # if prob > self.artifacts.threshold:
        #     pred = True
        #
        # return generatedProjectNameOutputs(pred=pred, prob=prob)
        # @endcode

        raise NotImplementedError

