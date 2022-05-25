from typing import Any, Dict

import requests


def validate_rich_menu_object(token: str, obj: Dict[str, Any]) -> bool:
    resp = requests.post(
        "https://api.line.me/v2/bot/richmenu/validate",
        json=obj,
        headers={"Authorization": f"Bearer {token}"},
    )
    return resp.status_code == 200
