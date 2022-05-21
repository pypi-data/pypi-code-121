from dataclasses import dataclass


@dataclass
class FunctionToRunMqMsg:
    FunctionRunRecordID: str
    ClientName: str
