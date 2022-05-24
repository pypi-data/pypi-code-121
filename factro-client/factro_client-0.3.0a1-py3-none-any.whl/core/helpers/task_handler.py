from typing import Optional
import logging


from dataclasses import dataclass
from dataclasses_json import dataclass_json, LetterCase, Undefined

from .base_handler import BaseHandler

logger = logging.getLogger('factro_client')

@dataclass_json(letter_case=LetterCase.CAMEL, undefined=Undefined.EXCLUDE)
@dataclass
class Task:
    id: str
    mandant_id: str
    number: int
    change_date: str
    creator_id: str
    title: str
    officer_id: str
    planned_effort: float
    project_id: str
    realized_effort: float
    remaining_effort: float
    executor_id: str
    is_milestone: bool
    task_state: str
    custom_fields: Optional[dict]
    parent_package_id: str = None
    company_contact_id: Optional[str] = ''
    description: Optional[str] = ''
    end_date: Optional[str] = ''
    start_date: Optional[str] = ''
    company_id: Optional[str] = ''
    paused_until: Optional[str] = ''
    task_priority: Optional[int] = 0


class TaskHandler(BaseHandler):

    def __init__(self, url: str, api_key: str):
        super(TaskHandler, self).__init__(url, api_key)

    def get_task_by_id(self, task_id) -> Task:
        path = f"/api/core/tasks/{task_id}"

        json_data = self.do_get(path)

        logger.debug(f"TaskHandler.get_task_by_id({task_id} -> {json_data}")
        try:
            task = Task.schema().load(json_data)
        except Exception as e:
            logger.error(f"TaskHandler.get_task_by_id({task_id} -> {json_data})")
            raise e

        return task