from ..utils import check_response
from .basemodel import BaseModel
from ..models import (
    LessonGetModel, PeriodGetModel, ContingentGetModel,
    TeacherGetModel, ScheduleGetModel, CalendarGetModel,
    InstituteToDisciplineGetModel, DisciplineGetModel,
    DisciplineToPeriodGetModel
)


class DepartmentCategory(BaseModel):
    async def lesson_get(self, departmentid: int, token: str, **kwargs) -> LessonGetModel:
        method = "department.lesson.get"

        query = self.get_set_params(locals())
        status, response = await self._request("get", method, query)

        # logger.debug(f"Got response from {url}: {response}")
        return await check_response(status, response, LessonGetModel)

    async def period_get(self, userid: int, token: str, **kwargs) -> PeriodGetModel:
        method = "department.period.get"

        query = self.get_set_params(locals())
        status, response = await self._request("get", method, query)

        # logger.debug(f"Got response from {url}: {response}")
        return await check_response(status, response, PeriodGetModel)

    async def contingent_get(self, departmentid: int, token: str, **kwargs) -> ContingentGetModel:
        method = "department.contingent.get"

        query = self.get_set_params(locals())
        status, response = await self._request("get", method, query)

        # logger.debug(f"Got response from {url}: {response}")
        return await check_response(status, response, ContingentGetModel)

    async def teacher_get(self, departmentid: int, token: str, **kwargs) -> TeacherGetModel:
        method = "department.teacher.get"

        query = self.get_set_params(locals())
        status, response = await self._request("get", method, query)

        # logger.debug(f"Got response from {url}: {response}")
        return await check_response(status, response, TeacherGetModel)

    async def schedule_get(self, departmentid: int, token: str, **kwargs) -> ScheduleGetModel:
        method = "department.schedule.get"

        query = self.get_set_params(locals())
        status, response = await self._request("get", method, query)

        # logger.debug(f"Got response from {url}: {response}")
        return await check_response(status, response, ScheduleGetModel)

    async def calendar_get(self, departmentid: int, token: str, **kwargs) -> CalendarGetModel:
        method = "department.calendar.get"

        query = self.get_set_params(locals())
        status, response = await self._request("get", method, query)

        # logger.debug(f"Got response from {url}: {response}")
        return await check_response(status, response, CalendarGetModel)

    async def institutetodiscipline_get(self, userid: int, token: str, **kwargs) -> InstituteToDisciplineGetModel:
        method = "department.institutetodiscipline.get"

        query = self.get_set_params(locals())
        status, response = await self._request("get", method, query)

        # logger.debug(f"Got response from {url}: {response}")
        return await check_response(status, response, InstituteToDisciplineGetModel)

    async def discipline_get(self, userid: int, token: str, **kwargs) -> DisciplineGetModel:
        method = "department.discipline.get"

        query = self.get_set_params(locals())
        status, response = await self._request("get", method, query)

        # logger.debug(f"Got response from {url}: {response}")
        return await check_response(status, response, DisciplineGetModel)

    async def disciplinetoperiod_get(self, userid: int, token: str, **kwargs) -> DisciplineToPeriodGetModel:
        method = "department.disciplinetoperiod.get"

        query = self.get_set_params(locals())
        status, response = await self._request("get", method, query)

        # logger.debug(f"Got response from {url}: {response}")
        return await check_response(status, response, DisciplineToPeriodGetModel)