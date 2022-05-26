from typing import TypedDict


class Organization(TypedDict):
    slug: str
    client_id: str

    def __init__(self, slug: str, client_id: str):
        # This is necessary instead of @dataclass due to an
        # incompatibility between dataclass + TypedDict in python3.9
        self.slug = slug
        self.client_id = client_id
