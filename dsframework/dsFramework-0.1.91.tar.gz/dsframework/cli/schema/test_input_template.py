import json
from typing import List, Optional
from pydantic import validator
from pydantic.main import BaseModel

##
# @file
# @brief Test the input row data from the DSP.
#        Data row from the DSP -> DSF.

class TestInputRow(BaseModel):
    """! BaseModel (pydantic.main) the base class for TestInputRow.
    @verbatim
    Args:
        data(str) : The data of a specific row, formatted into a json string
        id(int) : Dataset ID from the portal
        raw_id: Optional[int] = -1
    @endverbatim
    """
    data: str
    id: int
    raw_id: Optional[int] = -1

    @validator('data')
    def data_must_be_valid_json(cls, v):
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
            raise ValueError('data must be a valid json string')
        return v


class TestInputRequest(BaseModel):
    """! BaseModel (pydantic.main) the base class for TestInputRequest.
    @verbatim
    Args:
        truth_dataset_id: int = -1 : ID of the truth dataset
        model_type_id(=-1) : Model ID as defined by a table held in staging DSP (number per project)
        rows: List[TestInputRow] : List of TestInputRow
    @endverbatim
    """
    truth_dataset_id: int = -1
    model_type_id: int = -1
    rows: List[TestInputRow]
