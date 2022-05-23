# -*- coding:utf-8 -*- 
# author = 'denishuang'
from __future__ import unicode_literals
import json, base64
from django.core.signing import TimestampSigner

def gen_appoint_token(context, salt=''):
    signer = TimestampSigner(salt=salt)
    return signer.sign(base64.b64encode(json.dumps(context).encode('utf8')).decode())


def check_appoint_token(token, salt='', max_age=None):
    signer = TimestampSigner(salt=salt)
    try:
        s = signer.unsign(token, max_age=max_age)
        s = base64.b64decode(s)
        return json.loads(s)
    except:
        import traceback
        print(traceback.format_exc())
