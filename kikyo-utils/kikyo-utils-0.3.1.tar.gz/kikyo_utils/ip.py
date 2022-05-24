import requests

from kikyo_utils.constants import IPSEARCH_HOST
from kikyo_utils.retry import retry_rest_api


@retry_rest_api
def get_ip_info(ip: str, timeout: int = 20):
    resp = requests.post(
        f'{IPSEARCH_HOST}/api/ipsearch',
        json={'ip': ip},
        timeout=timeout,
    )
    resp.raise_for_status()
    return resp.json()['res']
