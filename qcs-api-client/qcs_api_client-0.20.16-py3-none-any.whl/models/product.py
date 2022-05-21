from enum import Enum


class Product(str, Enum):
    RESERVATIONCREATION = "reservationCreation"
    QPUJOBCOMPLETION = "qpuJobCompletion"
    QPUJOBTIME = "qpuJobTime"

    def __str__(self) -> str:
        return str(self.value)
