from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.orm import sessionmaker
from jwtserver import settings

settings = settings.get_settings()
pg_dsn = settings.postgres.pg_dsn

async_engine = create_async_engine(pg_dsn)
AsyncSessionLocal = sessionmaker(async_engine, expire_on_commit=False, class_=AsyncSession)

Base = declarative_base()
