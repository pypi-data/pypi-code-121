from pydantic import BaseModel
from typing import Optional, List
from collections import namedtuple
from model.common.mixins import EqMixin


class Phone(BaseModel, EqMixin):
    variable_type: str
    display_type: str
    country_code: Optional[str]
    number: Optional[str]
    ext: Optional[str]

    class Config:
        anystr_lower = True

    @property
    def international_format_full(self):
        return "+" + self.country_code + " " + self.number

    @property
    def isCanadaUs(self):
        return self.country_code and self.country_code == "1"

    @property
    def is_fax(self):
        return self.v_type == "fax"

    @property
    def NA_format_number(self):
        if len(self.number) != 10:
            raise ValueError(f"{self.number} is not a valid North America phone number")
        return "(" + self.number[:3] + ") " + self.number[3:6] + "-" + self.number[6:]

    # Return a list including area code, first part and second part of number
    @property
    def NA_format_list(self):
        if len(self.number) != 10:
            raise ValueError(f"{self.number} is not a valid North America phone number")
        return [self.number[:3], self.number[3:6], self.number[6:]]

    # Return a list including area code, first part and second part of number
    @property
    def NA_format_namedtuple(self):
        if len(str(self.number)) != 10:
            raise ValueError(f"{self.number} is not a valid North America phone number")
        NA_Number = namedtuple("NA_Number", ["area_code", "part1", "part2"])
        number = NA_Number(self.number[:3], self.number[3:6], self.number[6:])
        return number

    def __str__(self):
        return self.international_format_full


class Phones(object):
    def __init__(self, phone_list: List[Phone]) -> None:
        self.phonees = phone_list

    def _specific_phone(self, v_type):
        phone = [phone for phone in self.phonees if phone.variable_type == v_type]
        return phone[0] if phone else None

    @property
    def cellular(self):
        return self._specific_phone("cellular")

    @property
    def residential(self):
        return self._specific_phone("residential")

    @property
    def business(self):
        return self._specific_phone("business")

    @property
    def working(self):
        return self._specific_phone("working")

    @property
    def PreferredPhone(self):
        for Phone_type in ["cellular", "residential", "business", "working"]:
            phone = self._specific_phone(Phone_type)
            if phone:
                return phone

    def getPreferredPhoneFromList(self, type_list):
        for Phone_type in type_list:
            phone = self._specific_phone(Phone_type)
            if phone:
                return phone
