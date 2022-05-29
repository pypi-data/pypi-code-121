from edos.api.swarmpit.base_api import SwarmpitAPI
from edos.api.swarmpit.models.memory_response import MemoryResponse


class ServiceSwarmpitAPI(SwarmpitAPI):

    path = "/api/tasks"

    def get_memory_timeseries(self) -> list[MemoryResponse]:
        url = self.build_url()
        resp = self.get_request(url)
        memory_timeseries = []
        for item in resp:
            if item["desiredState"] == "running" and "redis" not in item["serviceName"]:
                memory_timeseries.append(
                    MemoryResponse(
                        item["serviceName"],
                        item["resources"]["reservation"]["memory"],
                        item["stats"]["memory"],
                    )
                )
        return memory_timeseries
