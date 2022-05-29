import dataclasses

from edos.api.swarmpit.models.memory_response import MemoryResponse
from edos.api.swarmpit.services import ServiceSwarmpitAPI


@dataclasses.dataclass
class MemoryServiceStats:
    service_name: str
    memory_reservation: int
    actual_memory_usage: int


class SwarmpitService:
    def __init__(self):
        self.api = ServiceSwarmpitAPI()

    def get_service_memory_stats(self) -> list[MemoryServiceStats]:
        timeseries: list[MemoryResponse] = self.api.get_memory_timeseries()

        service_stats = []
        for item in timeseries:
            memory_usage = int(item.actual_memory_usage / 1000000)  # MiB
            service_stats.append(
                MemoryServiceStats(
                    service_name=item.service_name,
                    memory_reservation=item.memory_reservation,
                    actual_memory_usage=memory_usage,
                )
            )
        return service_stats
