import requests

from kikyo_utils.constants import YURI_API_HOST
from kikyo_utils.retry import retry_rest_api


@retry_rest_api
def predict_bm_domain(content: str, timeout: int = 20) -> list:
    resp = requests.post(
        f'{YURI_API_HOST}/bm-domain/api/predict-bm-domain',
        json={'text': content},
        timeout=timeout,
    )
    resp.raise_for_status()
    return resp.json()['result']


@retry_rest_api
def extract_keywords(content: str, timeout: int = 20) -> list:
    resp = requests.post(
        f'{YURI_API_HOST}/keywords/api/tag/keywords',
        json={'content': content},
        timeout=timeout,
    )
    resp.raise_for_status()
    return resp.json()['keywords']


@retry_rest_api
def predict_themes(content: str, timeout: int = 20) -> list:
    resp = requests.post(
        f'{YURI_API_HOST}/theme/api/tag/themes',
        json={'content': content},
        timeout=timeout,
    )
    resp.raise_for_status()
    return resp.json()['result']


@retry_rest_api
def content_ner(content: str, timeout: int = 20) -> dict:
    resp = requests.post(
        f'{YURI_API_HOST}/content-ner/api/ner',
        json={'text': content},
        timeout=timeout,
    )
    resp.raise_for_status()
    return resp.json()['data']
