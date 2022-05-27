from requests import Response

from kikyo_api.errors import KikyoClientError


def read_json_data(resp: Response) -> dict:
    try:
        resp.raise_for_status()
    except Exception:
        try:
            data = resp.json()
        except Exception:
            pass
        else:
            if 'msg' in data:
                raise KikyoClientError(resp.status_code, data['msg'])
        raise
    return resp.json()['data']
