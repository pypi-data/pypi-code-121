from enum import Enum 


class Sentinel3ProductTypeEnum(str, Enum):
    lan = "LAN"
    wat = "WAT" 
    sra = "SRA"
    sra_a = "SRA_A"
    sra_vs = "SRA_BS"
    cal = "CAL"
