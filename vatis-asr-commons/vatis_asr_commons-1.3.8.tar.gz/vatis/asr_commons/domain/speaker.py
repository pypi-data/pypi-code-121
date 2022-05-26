import dataclasses


@dataclasses.dataclass
class SpeakerDiarization:
    start_millis: float
    end_millis: float
    label: str
