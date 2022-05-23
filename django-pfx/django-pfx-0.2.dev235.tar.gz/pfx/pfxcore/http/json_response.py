from django.core.exceptions import ValidationError
from django.http import JsonResponse as DjangoJsonResponse

from pfx.pfxcore.serializers.json import PFXJSONEncoder


class JsonResponse(DjangoJsonResponse):
    def __init__(self, data, encoder=PFXJSONEncoder, **kwargs):
        if isinstance(data, ValidationError):
            kwargs['safe'] = False
        super().__init__(data, encoder=encoder, **kwargs)
