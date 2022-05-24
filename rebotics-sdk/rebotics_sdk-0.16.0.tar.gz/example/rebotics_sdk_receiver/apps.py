from django.apps import AppConfig


class ReboticsSdkReceiverConfig(AppConfig):
    name = 'rebotics_sdk_receiver'

    def ready(self):
        from . import signals
