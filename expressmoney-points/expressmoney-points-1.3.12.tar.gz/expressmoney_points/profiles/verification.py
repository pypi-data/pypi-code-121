__all__ = ('RequestPhotoVerificationPoint', 'RequestVideoVerificationPoint',
           'AutoVerificationTaskPoint', 'VideoVerificationProcessPoint', 'PhotoVerificationProcessPoint',
           )

from expressmoney.api import *
from expressmoney.viewflow import result

SERVICE = 'profiles'


class RequestPhotoVerificationCreateContract(Contract):
    file = serializers.CharField(max_length=256)


class RequestVideoVerificationCreateContract(Contract):
    TELEGRAM = 'TELEGRAM'
    WHATSAPP = 'WHATSAPP'

    MESSENGER_CHOICE = (
        (TELEGRAM, 'Telegram'),
        (WHATSAPP, 'WhatsApp'),
    )
    user_message = serializers.CharField(max_length=256, allow_blank=True)
    messenger = serializers.ChoiceField(choices=MESSENGER_CHOICE)


class AutoVerificationTaskReadContract(Contract):
    id = serializers.IntegerField(min_value=1)
    created = serializers.DateTimeField()
    result = serializers.ChoiceField(choices=result.RESULT_CHOICES)
    comment = serializers.CharField(max_length=1024, allow_blank=True)


class VideoVerificationProcessReadContract(Contract):
    WAIT_10M = 'WAIT_10M'
    WAIT_30M = 'WAIT_30M'
    WAIT_1H = 'WAIT_1H'
    WAIT_1D = 'WAIT_1D'

    RECALL_CHOICES = (
        (WAIT_10M, '10 minutes'),
        (WAIT_30M, '30 minutes'),
        (WAIT_1H, '1 hour'),
        (WAIT_1D, 'Tomorrow'),
    )

    id = serializers.IntegerField(min_value=1)
    updated = serializers.DateTimeField()
    status = serializers.CharField(max_length=50)
    user_id = serializers.IntegerField(min_value=1)
    profile = serializers.IntegerField(min_value=1)
    result = serializers.ChoiceField(choices=result.RESULT_CHOICES)
    recall = serializers.ChoiceField(choices=RECALL_CHOICES, allow_blank=True)
    attempts = serializers.IntegerField(min_value=0)
    message = serializers.CharField(max_length=64, allow_blank=True)
    messenger = serializers.CharField(max_length=16, allow_blank=True)
    user_message = serializers.CharField(max_length=256, allow_blank=True)


class PhotoVerificationProcessReadContract(Contract):
    id = serializers.IntegerField(min_value=1)
    updated = serializers.DateTimeField()
    status = serializers.CharField(max_length=50)

    user_id = serializers.IntegerField(min_value=1)
    profile = serializers.IntegerField(min_value=1)
    result = serializers.ChoiceField(choices=result.RESULT_CHOICES)
    file = serializers.CharField(max_length=256)
    message = serializers.CharField(max_length=64, allow_blank=True)


class RequestPhotoVerificationID(ID):
    _service = SERVICE
    _app = 'verification'
    _view_set = 'request_photo_verification'


class RequestVideoVerificationID(ID):
    _service = SERVICE
    _app = 'verification'
    _view_set = 'request_video_verification'


class AutoVerificationTaskID(ID):
    _service = SERVICE
    _app = 'verification'
    _view_set = 'auto_verification_task'


class VideoVerificationProcessID(ID):
    _service = SERVICE
    _app = 'verification'
    _view_set = 'video_verification_process'


class PhotoVerificationProcessID(ID):
    _service = SERVICE
    _app = 'verification'
    _view_set = 'photo_verification_process'


class RequestPhotoVerificationPoint(CreatePointMixin, ContractPoint):
    _point_id = RequestPhotoVerificationID()
    _create_contract = RequestPhotoVerificationCreateContract


class RequestVideoVerificationPoint(CreatePointMixin, ContractPoint):
    _point_id = RequestVideoVerificationID()
    _create_contract = RequestVideoVerificationCreateContract


class AutoVerificationTaskPoint(ListPointMixin, ContractPoint):
    _point_id = AutoVerificationTaskID()
    _read_contract = AutoVerificationTaskReadContract


class VideoVerificationProcessPoint(ListPointMixin, ContractPoint):
    _point_id = VideoVerificationProcessID()
    _read_contract = VideoVerificationProcessReadContract


class PhotoVerificationProcessPoint(ListPointMixin, ContractPoint):
    _point_id = PhotoVerificationProcessID()
    _read_contract = PhotoVerificationProcessReadContract
