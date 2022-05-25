#!/usr/bin/env python
# coding: utf-8

from pydantic.main import BaseModel
##
# @file
# @brief Setting the output schema of the pipeline / service.
#        What are the expected variables to output?

class generatedClass(BaseModel):
    """! Examples:
    @code
    class <my-new-project>Outputs(BaseModel):
        is_valid: int = 0
        prob: float = 0.5
        version: str
    @endcode
    @code
    class <my-new-project>Outputs(BaseModel):
        pred: bool
        prob: float
        version: str = ''
    @endcode
    """
    pass
