from pydantic import BaseModel
from typing import Optional
from pydantic.class_validators import root_validator

class Position(BaseModel):
    why_hire:str
    who_current_fill:str
    how_did_you_find:str
    how_when_offer:str
    worked_working:bool
    worked_working_details:Optional[str]
    has_same:bool
    lowest:Optional[float]
    highest:Optional[float]
    under_cba:bool
    which_union:Optional[str]
    lmia_refused:bool
    lmia_refused_reason:Optional[str]
    
    @root_validator
    def checkAnswers(cls,values):
        questions=['worked_working','under_cba','lmia_refused']
        explanations=['worked_working_details','which_union','lmia_refused_reason']
        qas=dict(zip(questions,explanations))
        for k,v in qas.items():  
            if values.get(k) and not values.get(v):
                    raise ValueError(f"Since {k} is true, but you did not answer the question {v} in info-position sheet")
        return values
    
    @root_validator
    def checkRange(cls,values):
        if values.get('has_same')==True:
            if not values['lowest'] or not values['highest']:
                raise ValueError(f'Since you indicated in info-position sheet has same employee in this position, you have to input lowest and highest wage.')
            elif values['lowest']>values['highest']:
                raise ValueError("range must have two number ,and the first is lower, the second is higher")
            else:
                return values 
        return values

    