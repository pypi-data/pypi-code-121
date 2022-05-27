pyrasgo_api_key: str = None

# Set max polling time to an hour
MAX_POLL_ATTEMPTS = 900
POLL_RETRY_RATE = 4


def get_session_api_key():
    global pyrasgo_api_key
    return pyrasgo_api_key


def set_session_api_key(api_key: str):
    global pyrasgo_api_key
    clear_session_api_key()
    pyrasgo_api_key = api_key


def clear_session_api_key():
    global pyrasgo_api_key
    pyrasgo_api_key = None
