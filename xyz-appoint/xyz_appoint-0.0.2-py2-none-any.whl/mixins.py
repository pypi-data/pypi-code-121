# -*- coding:utf-8 -*- 
# author = 'denishuang'
from __future__ import unicode_literals

from rest_framework import decorators, response


class AppointModelMixin(object):

    @decorators.action(['GET'], detail=False)
    def appoint(self, request):
        from django.core.signing import TimestampSigner
        signer = TimestampSigner(salt='')
        from datetime import datetime, timedelta
        import json, base64
        expire_time = datetime.now() + timedelta(days=7)
        obj = self.get_object()
        d = dict(pk=obj.pk, model=obj._meta.label_lower, user=self.request.user.pk, expire=expire_time.isoformat())
        token = signer.sign(base64.b64encode(json.dumps(d).encode('utf8')).decode())
        return response.Response(dict(token=token))