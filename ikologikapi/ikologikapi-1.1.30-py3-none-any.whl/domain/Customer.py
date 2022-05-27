from ikologikapi.domain.AbstractIkologikObject import AbstractIkologikObject


class Customer(AbstractIkologikObject):

    def __init__(self):
        super().__init__()

        self.name = None

        self.address1 = None
        self.address2 = None
        self.address3 = None
        self.address4 = None
        self.address5 = None
        self.vat = None

        self.portalSettings = CustomerPortalSettings()
        self.securitySettings = CustomerSecuritySettings()
        self.storageSettings = CustomerStorageSettings()
        self.defaultFieldSettings = CustomerDefaultFieldSettings()
        self.newsSettings = CustomerNewsSettings()
        self.moduleSettings = CustomerModuleSettings()


class CustomerPortalSettings(object):

    def __init__(self):
        super().__init__()

        self.domain = None
        self.contactEmail = None
        self.invoiceEmail = None
        self.supportEmail = None
        self.supportUrl = 'https://support.ikologik.com'

        self.termsActive = False
        self.termsUrl = None


class CustomerSecuritySettings(object):

    def __init__(self):
        super().__init__()

        self.emailAsUsername = True
        self.passwordLevel = 'MEDIUM'
        self.passwordLength = 8

        self.passwordResetRequired = True
        self.passwordExpiration = False
        self.passwordExpirationDays = 180
        self.passwordHistory = 5

        self.mfaActive = False
        self.mfaRequired = False


class CustomerStorageSettings(object):

    def __init__(self):
        super().__init__()

        self.database = None
        self.retentionPolicy = 'PROD_5YEAR'


class CustomerDefaultFieldSettings(object):

    def __init__(self):
        super().__init__()

        self.nameActive = True
        self.distributorActive = False
        self.descriptionActive = False
        self.address1Active = False
        self.address2Active = False
        self.address3Active = False
        self.address4Active = True
        self.address5Active = True

        self.installationFieldTypeSelection = {}

        self.availabilityAlertsActive = True
        self.operationalAlertsActive = True
        self.connectivityAlertsActive = True
        self.maintenanceAlertsActive = True


class CustomerNewsSettings(object):

    def __init__(self):
        super().__init__()

        self.enabled = False
        self.newsUrl = None


class CustomerModuleSettings(object):

    def __init__(self):
        super().__init__()

        self.allowAdvancedStatus = False
        self.allowNews = False
        self.allowTicketing = False
        self.allowAcademy = False
        self.allowDistributors = False
        self.allowCertifications = False
        self.allowBatches = False
        self.allowDataImport = False
