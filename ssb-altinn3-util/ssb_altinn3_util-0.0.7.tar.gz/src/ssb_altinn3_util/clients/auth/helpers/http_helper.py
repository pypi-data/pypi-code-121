import requests


def get(url: str, headers: dict) -> str:
    response = requests.get(url, headers=headers)

    response_content: str = response.content.decode("UTF-8")

    if response.status_code != 200:
        raise Exception(
            f"Client failed to fetch.  Response/Error message: {response_content}"
        )

    return response_content


def post(url: str, headers: dict, body) -> str:
    response = requests.post(url, headers=headers, data=body)

    response_content: str = response.content.decode("UTF-8")

    if response.status_code != 200:
        raise Exception(
            f"Client failed to fetch.  Response/Error message: {response_content}"
        )

    return response_content
