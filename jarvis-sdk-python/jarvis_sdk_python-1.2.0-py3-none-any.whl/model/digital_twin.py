from uuid import UUID
from jarvis_sdk.utils import timestamp_to_date
from jarvis_sdk.model.property import Property


class DigitalTwinCore:
    @classmethod
    def deserialize(cls, message):
        if message is None:
            return None

        return DigitalTwinCore(
            str(UUID(bytes=message.id)),
            str(UUID(bytes=message.tenant_id)),
            message.kind,
            message.state
        )

    def __init__(self, dt_id, tenant_id, kind, state):
        self.id = dt_id
        self.tenantId = tenant_id
        self.kind = kind
        self.state = state

    def __str__(self):
        return (
            "Digital Twin: " + self.id + "\n"
            "Tenant: " + self.tenantId
        )


class DigitalTwin(DigitalTwinCore):
    @classmethod
    def deserialize(cls, message):
        if message is None:
            return None

        create_time = None
        if message.create_time:
            create_time = timestamp_to_date(message.create_time)
        properties = list(
            map(Property.deserialize, message.properties))

        dt_core = DigitalTwinCore.deserialize(message.digital_twin)
        return DigitalTwin(
            dt_core.id,
            dt_core.tenantId,
            dt_core.kind,
            dt_core.state,
            properties,
            create_time
        )

    def __init__(self, dt_id, tenant_id, kind, state, properties, create_time=None):
        super().__init__(dt_id, tenant_id, kind, state)
        self.createTime = create_time
        if properties:
            self.properties = properties
        else:
            self.properties = []

    def __str__(self):
        properties_string = ""
        for prop in self.properties:
            properties_string = properties_string + str(prop) + "\n"

        return (
            super().__str__() + "\n\n"
            "Properties:\n" + properties_string
        ).strip()
