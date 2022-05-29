import dataclasses


@dataclasses.dataclass
class MemoryResponse:
    service_name: str
    memory_reservation: int
    actual_memory_usage: int
