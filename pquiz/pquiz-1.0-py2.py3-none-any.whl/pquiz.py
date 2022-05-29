
import requests
import sys

TEST_HOST = "portquiz.net"
MAX_PORT = 2**16



def test_port(port=80, timeout=None, ignore_errors=True):
    try:
        res = requests.head(f'http://{TEST_HOST}:{port}/',timeout=timeout)
    except requests.exceptions.ConnectTimeout:
        if ignore_errors:
            return False
        raise  sys.exc_info()
    except requests.exceptions.ConnectionError:
        if ignore_errors:
            return False
        raise  sys.exc_info()
    except requests.exceptions.ReadTimeout:
        return False


    return res.status_code == 200
