#!/usr/bin/env python
# coding: utf-8

"""! @brief ZIDS_Pipeline base class for the pipeline."""

from typing import List
from dsframework.base.common.component import ZIDS_Component
from dsframework.base.pipeline.predictables.predictable import ZIDS_Predictable
from dsframework.base.pipeline.artifacts.shared_artifacts import ZIDS_SharedArtifacts


class ZIDS_Pipeline():
    """! ZIDS_Pipeline base class for the pipeline.

    Its main job is the base for building pipeline components.
    """

    def __init__(self):
        """! ZIDS_Pipeline class initializer."""
        self.components:List[ZIDS_Component] = []
        self.predictables:List[ZIDS_Predictable] = []
        self.artifacts = self.get_artifacts()
        self.build_pipeline()
        self.configure_pipeline()
        self.connect_pipeline()

    def get_artifacts(self):
        """! Loads and returns the artifacts and vocabs,

        Overridden by its parent in generatedProjectNamePipeline.get_artifacts() method."""
        return ZIDS_SharedArtifacts()
    
    def build_pipeline(self):
        """! Main place where the pipeline gets built with all of its components.

        Overridden by default implementation in generatedProjectNamePipeline.build_pipeline(), where its
        four main components gets instantiated:

        - generatedProjectNamePreprocess
        - generatedProjectNamePredictor
        - generatedProjectNameForcer
        - generatedProjectNamePostprocess.
        """
        raise NotImplementedError

    def configure_pipeline(self, **kwargs):
        """! Add configurations that need to take place after the build_pipeline() method.

        Override method in generatedProjectNamePipeline.configure_pipeline()
        """
        pass

    def connect_pipeline(self):
        """! Method distributes Artifacts instance to all pipeline components."""
        for c in self.components:
            c.artifacts = self.artifacts

    def preprocess(self, **kwargs) -> List[ZIDS_Predictable]:
        """! Runs preprocess step in the beginning of the pipeline

        Override method in generatedProjectNamePipeline.preprocess(), it needs to include all required steps
        before the Predictor (model) step.

        Args:
            **kwargs: Dataset loaded initially.
        Returns:
            List[ZIDS_Predictable]: List of predictable objects."""
        raise NotImplementedError

    def postprocess(self, predictables):
        """! Runs postprocess step at the end of the pipeline.

        Override method in generatedProjectNamePipeline.postprocess(), it needs to return the list of results.

        Returns:
            List[generatedProjectNameOutputs]: List of results.
        """
        raise NotImplementedError


    def add_component(self, component:ZIDS_Component):
        """! Adds component to pipeline.

        There are two components added by default: Predictor, Forcer and this is in addition to the pre-existing ones
        the preprocessor and postprocessor.

        Args:
            component: ZIDS_Component, component to add.
        """
        self.components.append(component)

    def __call__(self,  **kwargs):
        """! ZIDS_Pipeline __call__() method, runs execute() method of this class with specified args.

        Args:
            **kwargs: Initially loaded dataset.
        """
        return self.execute( **kwargs)

    def execute(self, **kwargs):
        """! Executes the pipeline,

        Runs the execute method for all registered components one after the other,

        Args:
            **kwargs: Initially loaded dataset.
        """
        self.predictables = self.preprocess(**kwargs)
        for c in self.components:
            self.predictables = c.execute(self.predictables)
        return self.postprocess(self.predictables)
