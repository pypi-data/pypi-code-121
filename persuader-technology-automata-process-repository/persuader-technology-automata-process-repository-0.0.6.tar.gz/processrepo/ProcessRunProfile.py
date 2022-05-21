from dataclasses import dataclass


@dataclass
class ProcessRunProfile:
    market: str
    name: str
    run_profile: str
