import httpx
from random import randint
from pydantic import BaseModel, PyObject

__all__ = ['SMSC']


def string_to_dict(text: str):
    return {
        k.strip(): v.strip()
        for k, v in [b.split(' - ', 1) for b in text.split(',')]
    }


class SMSModel(BaseModel):
    debug: bool = True  # imitation of sending SMS messages.
    ignore_attempts: bool = False
    try_call: int = 2
    try_sms: int = 2
    block_time_minutes: int = 180
    sms_fabric: PyObject = 'jwtserver.internal.SMSC.SMSC'
    login: str = None
    password: str = None
    time_sms: int = 120
    time_call: int = 90


class SMSC:
    url = 'https://smsc.ru/sys/send.php?'

    def __init__(self, _config):
        self.config: SMSModel = _config
        self.param_url = {
            'login': self.config.login,
            'psw': self.config.password
        }

    async def calling(self, telephone) -> tuple[str | None, str | None]:
        param_url = {
            **self.param_url,
            **{'phones': telephone, 'mes': 'code', 'call': 1}}

        if self.config.debug:
            code = '{:0>4d}'.format(randint(0, 9999))
        else:
            async with httpx.AsyncClient() as client:
                resp: httpx.Response = await client.get(self.url, param_url)
                if resp.status_code == httpx.codes.OK:
                    text = resp.text
                    if "ERROR" in text:
                        return None, 'Wait1min'
                    data = string_to_dict(text)
                else:
                    return None, 'response status not 200 OK'

            code = data['CODE'][-4:]
        return code, None

    async def send_sms(self, telephone, code) -> [bool, str | None]:
        param_url = {
            **self.param_url,
            **{'phones': telephone, 'mes': code}
        }
        if self.config.debug:
            return True, None

        async with httpx.AsyncClient() as client:
            resp: httpx.Response = await client.get(self.url, param_url)
            if resp.status_code == httpx.codes.OK:
                text = resp.text
                if "ERROR" in text:
                    return False, 'Wait1min'
            else:
                return False, 'response status not 200 OK'
            return True, None
