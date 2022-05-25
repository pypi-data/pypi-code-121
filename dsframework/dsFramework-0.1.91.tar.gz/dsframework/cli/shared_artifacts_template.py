#!/usr/bin/env python
# coding: utf-8

import json
from dsframework.base.pipeline.artifacts.shared_artifacts import ZIDS_SharedArtifacts

"""! @brief generatedClass (SharedArtifacts) class."""
class generatedClass(ZIDS_SharedArtifacts):

    def __init__(self) -> None:
        """! @brief generatedClass (SharedArtifacts) class.

        Override ZIDS_SharedArtifacts methods here, such as extend_load_file_type() for loading new file types.
        """

        ##
        # @hidecallgraph @hidecallergraph
        super().__init__()

    def extend_load_file_type(self, file_type, path, absolute_path, name):
        if absolute_path:
            if file_type == 'your-file-type':
                with open(absolute_path) as json_file:
                    setattr(self, name, json.load(json_file))
