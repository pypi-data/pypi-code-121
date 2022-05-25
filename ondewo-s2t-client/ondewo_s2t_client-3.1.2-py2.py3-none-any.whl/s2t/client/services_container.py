from dataclasses import dataclass

from ondewo.utils.base_service_container import BaseServicesContainer

from ondewo.s2t.client.services.speech_to_text import Speech2Text


@dataclass
class ServicesContainer(BaseServicesContainer):
    speech_to_text: Speech2Text
