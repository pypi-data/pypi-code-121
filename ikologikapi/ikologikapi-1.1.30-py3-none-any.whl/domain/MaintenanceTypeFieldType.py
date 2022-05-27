from ikologikapi.domain.AbstractIkologikCustomerFieldType import AbstractIkologikCustomerFieldType


class MaintenanceTypeFielType(AbstractIkologikCustomerFieldType):
    def __init__(self, customer: str):
        super().__init__(customer)

        self.maintenanceType = None
