from datetime import date
from pydantic import BaseModel, EmailStr
from typing import List, Union


class COR(BaseModel):
    start_date: date
    end_date: Union[date, None]
    country: str
    status: str


class CORs(object):
    # Frist row must be current residence
    def __init__(self, cors: List[COR]):
        self.cors = cors

    @property
    def current(self):
        ccor = [country for country in self.cors if country.end_date == None]
        if len(ccor) == 1:
            return ccor[0]
        elif len(ccor) == 0 and len(self.cors) > 0:
            return self.cors[0]
        else:
            raise ValueError("No residence data, please check")

    @property
    def previous(self):
        if len(self.cors) == 0:
            print("There is no residence data, please check")
            return
        return self.cors[1:]
