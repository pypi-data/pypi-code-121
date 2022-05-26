from ..utils import check_response
from .basemodel import BaseModel
from ..models import (
    AbsencesByPeriodGetModel, AvgMarksByPeriodGetModel, AbsencesByDisciplinGetModel,
    TeacherGetModel, ScheduleGetModel, CalendarGetModel,
    InstituteToDisciplineGetModel, DisciplineGetModel,
    DisciplineToPeriodGetModel
)


class ChartCategory(BaseModel):
    async def absencesbyperiod_get(self, userid: int, token: str, startdate: str, enddate: str, **kwargs) -> AbsencesByPeriodGetModel:
        method = "chart.absencesbyperiod.get"

        query = self.get_set_params(locals())
        status, response = await self._request("get", method, query)

        # logger.debug(f"Got response from {url}: {response}")
        return await check_response(status, response, AbsencesByPeriodGetModel)

    async def avgmarksbyperiod_get(self, userid: int, token: str, startdate: str, enddate: str, stepdays: int = 5, **kwargs) -> AvgMarksByPeriodGetModel:
        method = "chart.avgmarksbyperiod.get"

        query = self.get_set_params(locals())
        status, response = await self._request("get", method, query)

        # logger.debug(f"Got response from {url}: {response}")
        return await check_response(status, response, AvgMarksByPeriodGetModel)

    async def absencesbydisciplin_get(self, userid: int, token: str, startdate: str, enddate: str, **kwargs) -> AbsencesByDisciplinGetModel:
        method = "chart.absencesbydisciplin.get"

        query = self.get_set_params(locals())
        status, response = await self._request("get", method, query)

        # logger.debug(f"Got response from {url}: {response}")
        return await check_response(status, response, AbsencesByDisciplinGetModel)
