from typing import Optional, List, Dict, Any
import requests


PANDORABOTS_ENDPOINT = "https://api.pandorabots.com/talk"
PANDORABOTS_RESPONSE_KEY = "responses"
RESPONSE_OK = 200


def sraix_pandorabots(botid: str, input_: str) -> Optional[List[str]]:
    """Perform request, return a list of responses or None if failed."""
    payload = {"botkey": botid, "input": input_}
    try:
        r = requests.get(PANDORABOTS_ENDPOINT, params=payload)
        data: Dict[str, Any] = r.json()
        if r.status_code != RESPONSE_OK or data.get("status") != "ok":
            return None
        if PANDORABOTS_RESPONSE_KEY not in data:
            return None
        res: List[str] = data[PANDORABOTS_RESPONSE_KEY]
        return res
    except Exception:
        return None
