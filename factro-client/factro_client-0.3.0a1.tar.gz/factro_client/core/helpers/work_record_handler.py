from typing import List, Optional

from dataclasses import dataclass
from dataclasses_json import dataclass_json, LetterCase, Undefined

from .base_handler import BaseHandler

@dataclass_json(letter_case=LetterCase.CAMEL, undefined=Undefined.EXCLUDE)
@dataclass
class WorkRecord:
    booked_on_reference_id: str
    creator_employee_id: str
    description: str
    end_date: str
    end_time: str
    id: str
    is_billable: bool
    is_billed: bool
    mandant_id: str
    minutes_worked: float
    start_date: str
    start_time: str
    title: str
    work_employee_id: str
    external_booking_details: Optional[str] = ''
    travelled_distance_km: Optional[float] = 0.0
    internal_booking_details: Optional[str] = ''
    created_in_context_of_reference_id: Optional[str] = ''


class WorkRecordHandler(BaseHandler):

    def __init__(self, url: str, api_key: str):
        super(WorkRecordHandler, self).__init__(url, api_key)

    def get_work_records(self, from_date:str, to_date:str) -> List[WorkRecord]:
        query = f"?startDate={from_date}&endDate={to_date}"
        path = f"/api/core/work-records{query}"

        json_data = self.do_get(path)

        work_records = WorkRecord.schema().load(json_data, many=True)

        return work_records