from ikologikapi.domain.AbstractIkologikCustomerObject import AbstractIkologikCustomerObject


class AbstractIkologikCustomerFieldType(AbstractIkologikCustomerObject):
    def __init__(self, customer):
        super().__init__(customer)

        self.code = None
        self.name = None
        self.order = 0
        self.type = None
        self.lookupList = None

        self.defaultStringValue = None
        self.defaultBooleanValue = None
        self.defaultNumberValue = None
        self.defaultDateValue = None
        self.defaultTimeValue = None
        self.defaultDateTimeValue = None
        self.defaultLookupListValue = None

        self.required = None
        self.unique = None
