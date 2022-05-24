from typing import Dict

from httpx import AsyncClient, codes

from nbr.exceptions import InvalidPathException


async def get_contents(path: str, client: AsyncClient) -> Dict:
    """Get content by path."""
    url = f"/contents/{path}"

    response = await client.get(url)

    if response.status_code == codes.NOT_FOUND.value:
        raise InvalidPathException(f"No such file or directory: {path}")

    return response.json()
