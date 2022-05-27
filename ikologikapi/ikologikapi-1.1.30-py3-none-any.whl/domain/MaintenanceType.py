from ikologikapi.domain.AbstractIkologikCustomerObject import AbstractIkologikCustomerObject


class MaintenanceType(AbstractIkologikCustomerObject):
    def __init__(self, customer: str):
        super().__init__(customer)

        self.name = None
        self.description = None
        self.planningPeriodValue = 0
        self.planningPeriodUnit = 'MINUTE'
        self.durationUnit = 0
        self.durationUnit = 'MINUTE'
