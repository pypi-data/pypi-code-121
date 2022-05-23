import requests
from urllib.parse import urljoin
import json

ANALYTICS = "ANALYTICS"


def update_analytics(base_url, api_key, action):
    payload = json.dumps({
        "action": action
    })

    url = urljoin("https://" + base_url, ANALYTICS)

    response = requests.post(
        url=url,
        data=payload,
        headers={
            "Content-Type": "application/json",
            "x-api-key": api_key,
        },
    )

    print("Analytics: ", response)
