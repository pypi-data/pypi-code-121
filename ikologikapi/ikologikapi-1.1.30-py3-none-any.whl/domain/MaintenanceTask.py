from ikologikapi.domain.AbstractIkologikInstallationsObject import AbstractIkologikInstallationsObject


class MaintenanceTask(AbstractIkologikInstallationsObject):

    def __init__(self, customer: str, installation: str):
        super().__init__(customer, installation)

        self.maintenanceType = None
        self.asset = None

        self.status = 'STATUS_2_PLANNED'
        self.startDate = None
        self.endDate = None
        self.description = None

        self.fields = {}
