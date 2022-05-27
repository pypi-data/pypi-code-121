# from utils import get_uuid
from .utils import get_uuid
import requests


class TrickleSendFailed(Exception):
    pass


def generateBlock(text: str):
    return {
        "id": get_uuid(),
        "type": "rich_texts",
        "blocks": [],
        "indent": 0,
        "display": "block",
        "isFirst": True,
        "elements": [{
            "id": get_uuid(),
            "text": text,
            "type": "text",
            "elements": [],
            "isCurrent": True
        }],
        "isCurrent": False
    }


def newline():
    return generateBlock(text="")


def content2Blocks(content: str):
    blocks = []

    paragraphs = content.split("\\n")
    for idx, para in enumerate(paragraphs):
        blocks.append(generateBlock(text=para.strip()))
        if idx != len(paragraphs)-1:
            blocks.append(newline())

    return blocks


def shell2Trickle(content: str, endpoint: str, token: str):
    blocks = content2Blocks(content)
    resp = requests.post(
        url=endpoint, 
        json={"blocks": blocks}, 
        headers={"Authorization": token}
    )

    if resp.status_code != 201:
        raise TrickleSendFailed("Something wrong, Your trickle send failed!")
    
    print("Sended Successfully!")


if __name__ == "__main__":
    content = "hello world \\n   123123"

    blocks = content2Blocks(content)
    print(blocks)