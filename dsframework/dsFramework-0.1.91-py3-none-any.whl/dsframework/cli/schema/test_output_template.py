import json
from typing import List, Optional

from pydantic import validator, Extra
from pydantic.main import BaseModel

##
# @file
# @brief Outputs from the DSF -> DSP

class TestOutputResponse(BaseModel):
    """! BaseModel (pydantic.main) the base class for TestOutputResponse.
    @verbatim
    Args:
        truth_id: int
        truth_dataset_id(int): dataset id from the portal
        model_type_id : Model ID as defined by a table held in staging DSP (number per project)
        raw_id(=-1) : int
        pred(str): prediction, take all input data, replace ground truth with actual model prediction, and store as a json string
        target(str): the target, take all the data as a string (from the input dataset)
        text: string
    @endverbatim
    """
    truth_id: int
    truth_dataset_id: int
    model_type_id: int
    raw_id: int = -1
    pred: str
    target: str
    text: str = ''

    @validator('pred')
    def pred_must_be_valid_json(cls, v):
        """! Method that check the data if it's valid json string.

            Args:
                cls : not in use
                v : Data that is going to be checked.
            Raises:
                ValueError
        """
        try:
            json.loads(v)
        except:
            raise ValueError('pred must be a valid json string')
        return v

    @validator('target')
    def target_must_be_valid_json(cls, v):
        """! Method that check the data if it's valid json string.

            Args:
                cls : not in use
                v : Data that is going to be checked.
            Raises:
                ValueError
        """
        try:
            json.loads(v)
        except:
            raise ValueError('target must be a valid json string')
        return v

    class Config:
        extra = Extra.allow
