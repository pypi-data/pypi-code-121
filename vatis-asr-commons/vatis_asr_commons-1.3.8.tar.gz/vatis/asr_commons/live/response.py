import dataclasses


@dataclasses.dataclass
class ReservationResponse:
    token: str
    stream_url: str
    stream_host: str
