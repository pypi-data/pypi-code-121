#!/usr/bin/env python3

################################################
#
#   MetaWorkflow ff
#
################################################

################################################
#   Libraries
################################################
import sys, os
import copy

# magma
from magma.metawfl import MetaWorkflow as MetaWorkflowFromMagma
from magma_ff.parser import ParserFF

################################################
#   MetaWorkflow
################################################
class MetaWorkflow(MetaWorkflowFromMagma):

    def __init__(self, input_json):
        """
        """
        input_json_ = copy.deepcopy(input_json)
        ParserFF(input_json_).arguments_to_json()

        super().__init__(input_json_)
    #end def

#end class
