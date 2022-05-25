import json

import requests


def complete_instance(
    token: str,
    base_url: str,
    org: str,
    app: str,
    instance_owner_party_id: int,
    instance_guid: str,
) -> str:
    headers = {"Authorization": f"Bearer {token}"}
    url = f"{base_url}{org}/{app}/instances/{instance_owner_party_id}/{instance_guid}/complete"
    body = "{}"

    response = requests.post(url, json=body, headers=headers)

    content = response.content.decode("UTF-8")

    return json.dumps(json.loads(content))
