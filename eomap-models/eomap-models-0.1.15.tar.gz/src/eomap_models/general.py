from enum import Enum 


class RequestStatusEnum(str, Enum):
    concluded = "concluded"
    in_process = "processing"
    failed = "failed"
