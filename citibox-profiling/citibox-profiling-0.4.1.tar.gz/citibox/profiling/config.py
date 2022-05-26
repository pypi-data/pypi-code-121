from dataclasses import dataclass


@dataclass
class Config:
    service_name: str
    service_version: str
