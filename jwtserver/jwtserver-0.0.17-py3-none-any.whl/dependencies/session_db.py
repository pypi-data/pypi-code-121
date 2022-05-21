from jwtserver.database import AsyncSessionLocal


# async def async_db_session():
#     """Databases pool fabric connection, auto close connection"""
#     async with AsyncSessionLocal() as session:
#         yield session
async def async_db_session():
    """Databases pool fabric connection, auto close connection"""
    try:
        db = AsyncSessionLocal()
        yield db
    finally:
        await db.close()
