#!/usr/bin/env python
# coding: utf-8

##
# @file
# @brief ZIDS_Postprocessor base class for Postprocess class.

from typing import List, Any
from dsframework.base.common.component import ZIDS_Component
from dsframework.base.pipeline.predictables.predictable import ZIDS_Predictable
from dsframework.base.pipeline.artifacts.shared_artifacts import ZIDS_SharedArtifacts

class ZIDS_Postprocessor(ZIDS_Component):
    """! ZIDS_Postprocessor the base class for Postprocess class."""

    def __init__(self, artifacts:ZIDS_SharedArtifacts=None) -> None:
        """! ZIDS_Postprocessor initializer

        Args:
            artifacts(ZIDS_SharedArtifacts): Shared artifacts instance.
        """

        ##
        # @hidecallgraph @hidecallergraph
        super().__init__(artifacts)

    def normalize_output(self, predictables:List[ZIDS_Predictable]) -> Any:
        """! ZIDS_Postprocessor.normalize_output base method.

        Not implemented, override in generatedProjectNamePostprocess class.

        This method should return final results output as a generatedProjectNameOutputs datatype object.

        Raises:
            NotImplementedError
        """
        raise NotImplementedError

    def execute(self,  predictables:List[Any]) -> Any:
        """! Executes postprocess step.

        Args:
            predictables:List[Any]: List of predictables received from the model and/or forcer.
        Returns:
            List[Outputs]: List of results after post-processing.
        """
        return self.normalize_output(super().execute(predictables))
