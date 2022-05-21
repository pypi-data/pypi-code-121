from sqlalchemy.exc import NoResultFound

from jwtserver.database import AsyncSessionLocal
from jwtserver.functions.session_db import async_db_session
from jwtserver.models import User
from sqlalchemy.future import select


async def get_user(telephone: str):
    session = async_db_session()
    session.next()
    session.execute()
    async with AsyncSessionLocal() as session:
        stmt = select(User).where(User.telephone == telephone)
        result = await session.execute(stmt)
        try:
            return result.scalars().one()
        except NoResultFound:
            return None
