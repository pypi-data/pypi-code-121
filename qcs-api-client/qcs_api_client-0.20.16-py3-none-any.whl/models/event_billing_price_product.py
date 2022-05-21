from enum import Enum


class EventBillingPriceProduct(str, Enum):
    QPUJOBCOMPLETION = "qpuJobCompletion"
    QPUJOBTIME = "qpuJobTime"
    RESERVATIONCREATION = "reservationCreation"

    def __str__(self) -> str:
        return str(self.value)
