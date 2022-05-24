from typing import List

from httpx import AsyncClient

from nbr.schemas.session import CreateSession, Session


async def get_sessions(*, client: AsyncClient) -> List[Session]:
    """Get all sessions."""
    response = await client.get("/sessions")
    all_sessions = [Session(**data) for data in response.json()]

    return all_sessions


async def create_session(
    *, session_data: CreateSession, client: AsyncClient
) -> Session:
    """Create a new session."""
    response = await client.post("/sessions", json=session_data.dict())
    return Session(**response.json())


async def delete_session(*, session_id: str, client: AsyncClient) -> None:
    """Delete session by id."""
    url = f"/sessions/{session_id}"
    await client.delete(url)
