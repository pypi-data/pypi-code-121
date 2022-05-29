from . import _AbstractAsyncClient
from . import _AbstractClient
from ..schemas import Report
from ..schemas import ReportIn


class _ReportsClient(_AbstractClient):
    def create(self, report: ReportIn) -> Report:
        """Create a repport"""
        response = self._http_post(data=report.dict())
        return Report(**response.json())

    def list(self):
        """gets reports and yields them as a generator"""
        response = self._http_get()
        for report in response.json():
            yield Report(**report)


class _ReportsAsyncClient(_AbstractAsyncClient):
    async def create(self, report: ReportIn) -> Report:
        """Create a repport"""
        response = await self._http_post(data=report.dict())
        return Report(**response.json())

    async def list(self):
        """gets reports and yields them as a generator"""
        response = await self._http_get()
        for report in response.json():
            yield Report(**report)
