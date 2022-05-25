#!/usr/bin/env python
# coding: utf-8

from pydantic.main import BaseModel

##
# @file
# @brief Setting the schema inputs, which is the basic structure that the pipeline/service would receive.
#        What data variables you need as an input? it could be a dataset or part of it and additional required variables, such as threshold etc.
#        Using Pydantic's base class that can validate their input class.

class generatedClass(BaseModel):
    """! For example :
    @code
    class <my-new-project>Inputs(BaseModel):
       email: str = ""
       threshold: Optional[float]
       hints: Optional[List[EmailHint]]
    @endcode
    Another example:
    @code
    class <my-new-project>Inputs(BaseModel):
        html_content: str
        source: str
        queue_name: str
        title: str
    @endcode
    """
    pass
