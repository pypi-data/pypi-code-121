"""
Main interface for voice-id service.

Usage::

    ```python
    from boto3.session import Session
    from mypy_boto3_voice_id import (
        Client,
        ListDomainsPaginator,
        ListFraudsterRegistrationJobsPaginator,
        ListSpeakerEnrollmentJobsPaginator,
        ListSpeakersPaginator,
        VoiceIDClient,
    )

    session = Session()
    client: VoiceIDClient = session.client("voice-id")

    list_domains_paginator: ListDomainsPaginator = client.get_paginator("list_domains")
    list_fraudster_registration_jobs_paginator: ListFraudsterRegistrationJobsPaginator = client.get_paginator("list_fraudster_registration_jobs")
    list_speaker_enrollment_jobs_paginator: ListSpeakerEnrollmentJobsPaginator = client.get_paginator("list_speaker_enrollment_jobs")
    list_speakers_paginator: ListSpeakersPaginator = client.get_paginator("list_speakers")
    ```
"""
from .client import VoiceIDClient
from .paginator import (
    ListDomainsPaginator,
    ListFraudsterRegistrationJobsPaginator,
    ListSpeakerEnrollmentJobsPaginator,
    ListSpeakersPaginator,
)

Client = VoiceIDClient


__all__ = (
    "Client",
    "ListDomainsPaginator",
    "ListFraudsterRegistrationJobsPaginator",
    "ListSpeakerEnrollmentJobsPaginator",
    "ListSpeakersPaginator",
    "VoiceIDClient",
)
