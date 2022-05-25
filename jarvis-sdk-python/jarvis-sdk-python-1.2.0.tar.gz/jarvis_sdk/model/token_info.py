from uuid import UUID
from jarvis_sdk.model.digital_twin import DigitalTwinCore
from jarvis_sdk.model.provider_info import ProviderInfo
from jarvis_sdk.utils import timestamp_to_date


class TokenInfo:
    @classmethod
    def deserialize(cls, message):
        if message is None:
            return None

        token_info = TokenInfo(
            str(UUID(bytes=message.customer_id)),
            str(UUID(bytes=message.app_space_id)),
            str(UUID(bytes=message.application_id)),
            list(map(ProviderInfo.deserialize, message.provider_info))
        )

        if message.HasField('subject'):
            token_info.subject = DigitalTwinCore.deserialize(message.subject)

        if message.HasField('impersonated'):
            token_info.impersonated = DigitalTwinCore.deserialize(
                message.impersonated)

        if message.HasField('issue_time'):
            token_info.issueTime = timestamp_to_date(message.issue_time)

        if message.HasField('expire_time'):
            token_info.expireTime = timestamp_to_date(message.expire_time)

        if message.HasField('authentication_time'):
            token_info.authenticationTime = timestamp_to_date(
                message.authentication_time)

        return token_info

    def __init__(self, customer_id, app_space_id, application_id, provider_info):
        self.customerId = customer_id
        self.appSpaceId = app_space_id
        self.applicationId = application_id
        self.providerInfo = provider_info
        self.subject = None
        self.impersonated = None
        self.issueTime = None
        self.expireTime = None
        self.authenticationTime = None

    def __str__(self):
        string = (
            "Customer ID: " + self.customerId + "\n"
            "Application Space ID: " + self.appSpaceId + "\n"
            "Application ID: " + self.applicationId
        )

        if hasattr(self, "subject"):
            string = (
                string + "\n"
                "Subject ID: " + self.subject.id + "\n"
                "Subject tenant ID: " + self.subject.tenantId
            )

        if hasattr(self, "issueTime"):
            string = (
                string + "\n"
                "Issue time: " + str(self.issueTime)
            )

        if hasattr(self, "expireTime"):
            string = (
                string + "\n"
                "Expire time: " + str(self.expireTime)
            )

        if hasattr(self, "authenticationTime"):
            string = (
                string + "\n"
                "Authentication time: " + str(self.authenticationTime)
            )

        providers_string = ""
        for provider in self.providerInfo:
            providers_string = providers_string + str(provider) + "\n"

        string = (
            string + "\n"
            "Provider info:\n" + providers_string.strip()
        )

        return string
