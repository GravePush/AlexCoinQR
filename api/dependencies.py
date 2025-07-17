from sqlalchemy.ext.asyncio import AsyncSession
from database import get_db


async def get_session() -> AsyncSession:
    async with get_db() as session:
        yield session
