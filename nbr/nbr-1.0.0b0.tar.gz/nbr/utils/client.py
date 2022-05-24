from typing import Any, Dict

from httpx import AsyncClient


def create_client(base_url: str, headers: Dict[Any, Any]) -> AsyncClient:
    """Create AsyncClient."""
    return AsyncClient(base_url=base_url, headers=headers)


def prepare_headers(token: str) -> Dict:
    """Prepare headers for client."""
    if token:
        return {"Authorization": f"token {token}"}
    return {}
