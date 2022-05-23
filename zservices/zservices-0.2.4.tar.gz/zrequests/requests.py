# todo put in module z-requests
import requests
from zrequests import logger
from zrequests.setting import Setting
import time
import json as f_json
from requests import Response


# todo if text contains in verify success
def verify_success_text(s_text, response: Response):
    if isinstance(s_text, dict):
        r_json = f_json.loads(response.text)
        for k, v in s_text.items():
            if k in r_json and v == r_json[k]:
                continue
            else:
                return False, response
        return True, response
    return False, response


# todo remove sensitive info from url
def send_request(method, url, s_codes: list, params, headers, tag='N', json=None, data=None, count=0, sleep=False,
                 s_text=None):
    response = None
    if count < Setting.MAX_RETRY:
        try:
            response = requests.request(method, url=url, params=params, data=data, headers=headers, json=json)
            if response.status_code in s_codes:
                if not s_text:
                    return True, response
                return verify_success_text(s_text, response)
            else:
                raise requests.exceptions.RequestException('Forced Exception Invalid Status Code')
        except Exception as e:
            logger.warning(f'[ZREQUEST] [{tag}][{count}]. {url}, e={e}, r={response}', exc_info=True)
            count += 1
            if sleep:
                time.sleep(2 ** count)
            send_request(method, url, s_codes, params, headers, tag, json, count, sleep, s_text)

        logger.error(f'[ZREQUEST] [{tag}] {url}, r={response},', exc_info=True)
        return False, response
