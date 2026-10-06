from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession

from app.core.config import Settings, settings

engine = create_async_engine(settings.async_database_url, echo=settings.DEBUG, pool_size=10, max_overflow=20, pool_pre_ping=True)

async_session_factory = async_sessionmaker(bind=engine, class_=AsyncSession, autoflush=False, expire_on_commit=False)

async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_factory() as session:
        try:
            yield session
        except Exception:
            await session.rollback()
            raise