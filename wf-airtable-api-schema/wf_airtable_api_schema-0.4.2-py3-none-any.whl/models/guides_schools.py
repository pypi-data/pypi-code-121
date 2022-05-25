from datetime import date
from typing import Optional

from pydantic import BaseModel

MODEL_TYPE = "guides_school"


class APIGuidesSchoolsFields(BaseModel):
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    type: Optional[str] = None
    active: Optional[str] = None
    school_id: Optional[str] = None
    guide_id: Optional[str] = None
