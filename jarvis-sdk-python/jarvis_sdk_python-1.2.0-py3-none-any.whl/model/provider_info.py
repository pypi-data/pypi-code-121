from jarvis_sdk.indykite.identity.v1beta1.model_pb2 import ProviderType


class ProviderInfo:
    @classmethod
    def deserialize(cls, message):
        return ProviderInfo(message.type, message.issuer)

    def __init__(self, provider_type, issuer):
        self.type = ProviderType.Name(provider_type)
        self.issuer = issuer

    def __str__(self):
        return (
            "Type: " + self.type + "\n"
            "Issuer: " + self.issuer
        )
