import random


def _random_user_agent() -> str:
    """
    Returns a random user agent string

    taken from: https://github.com/yt-dlp/yt-dlp/blob/master/yt_dlp/utils.py
    Returns:
        str: random user agent string
    """
    _USER_AGENT_TPL = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/%s Safari/537.36"
    _CHROME_VERSIONS = (
        "90.0.4430.212",
        "90.0.4430.24",
        "90.0.4430.70",
        "90.0.4430.72",
        "90.0.4430.85",
        "90.0.4430.93",
        "91.0.4472.101",
        "91.0.4472.106",
        "91.0.4472.114",
        "91.0.4472.124",
        "91.0.4472.164",
        "91.0.4472.19",
        "91.0.4472.77",
        "92.0.4515.107",
        "92.0.4515.115",
        "92.0.4515.131",
        "92.0.4515.159",
        "92.0.4515.43",
        "93.0.4556.0",
        "93.0.4577.15",
        "93.0.4577.63",
        "93.0.4577.82",
        "94.0.4606.41",
        "94.0.4606.54",
        "94.0.4606.61",
        "94.0.4606.71",
        "94.0.4606.81",
        "94.0.4606.85",
        "95.0.4638.17",
        "95.0.4638.50",
        "95.0.4638.54",
        "95.0.4638.69",
        "95.0.4638.74",
        "96.0.4664.18",
        "96.0.4664.45",
        "96.0.4664.55",
        "96.0.4664.93",
        "97.0.4692.20",
    )
    return _USER_AGENT_TPL % random.choice(_CHROME_VERSIONS)


def get_headers() -> dict[str, str]:
    """
    Returns a dictionary of headers to be used for HTTP requests

    taken from: https://github.com/yt-dlp/yt-dlp/blob/master/yt_dlp/utils.py
    """
    return {
        "User-Agent": _random_user_agent(),
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
        "Accept-Language": "en-us,en;q=0.5",
        "Sec-Fetch-Dest": "document",
        "Sec-Fetch-Mode": "navigate",
        "Accept-Encoding": "gzip, deflate",
    }
