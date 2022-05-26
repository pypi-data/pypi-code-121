from datetime import date
from pydantic import BaseModel
from typing import Optional,List

class Status(BaseModel):
    current_country:str
    current_country_status:str
    current_workpermit_type:Optional[str]
    has_vr:Optional[bool]
    current_status_start_date:date
    current_status_end_date:date
    other_status_explaination:Optional[str]
    last_entry_date:Optional[date]
    last_entry_place:Optional[date]