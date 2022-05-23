import requests as sync_req
from zrequests import logger
from zrequests.setting import Setting
import time
import json as f_json


# todo if text contains in verify success
def verify_success_text(s_text, response: sync_req.Response):
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
            response = sync_req.request(method, url=url, params=params, data=data, headers=headers, json=json)
            if response.status_code in s_codes:
                if not s_text:
                    return True, response
                return verify_success_text(s_text, response)
            else:
                raise sync_req.exceptions.RequestException('Forced Exception Invalid Status Code')
        except Exception as e:
            logger.warning(f'[ZREQUEST] [{tag}][{count}]. {url}, e={e}, r={response}', exc_info=True)
            count += 1
            if sleep:
                time.sleep(2 ** count)
            return send_request(method, url, s_codes, params, headers, tag, json, data, count, sleep, s_text)

    logger.error(f'[ZREQUEST] [{tag}] {url}, r={response},', exc_info=True)
    return False, response
