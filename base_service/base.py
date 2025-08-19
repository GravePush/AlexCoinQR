from sqlalchemy import select, insert, update, delete, desc
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_db


class BaseService:
    model = None

    @classmethod
    async def get_all(cls, session: AsyncSession, **data):
        query = select(cls.model).filter_by(**data).order_by(desc(cls.model.created_at))
        result = await session.execute(query)
        return result.scalars().all()

    @classmethod
    async def get_one_by_id(cls, session: AsyncSession, item_id):
        query = select(cls.model).filter_by(id=item_id)
        result = await session.execute(query)
        return result.scalar_one_or_none()

    @classmethod
    async def get_one_or_none(cls, session: AsyncSession, **data):
        query = select(cls.model).filter_by(**data)
        result = await session.execute(query)
        return result.scalar_one_or_none()

    @classmethod
    async def create(cls, session: AsyncSession, **data):
        stmt = insert(cls.model).values(**data).returning(cls.model)
        result = await session.execute(stmt)
        await session.commit()
        return result.scalar_one_or_none()

    @classmethod
    async def update(cls, session: AsyncSession, item_id, **data):
        exists_item = await cls.get_one_or_none(id=item_id, session=session)
        if exists_item is None:
            return None
        stmt = (
            update(cls.model)
            .where(cls.model.id == item_id)
            .values(**data)
            .returning(cls.model)
        )
        result = await session.execute(stmt)
        await session.commit()
        return result.scalar_one_or_none()

    @classmethod
    async def delete(cls, session: AsyncSession, item_id):

        exists_item = await cls.get_one_or_none(session=session, id=item_id)
        if exists_item is None:
            return None
        stmt = delete(cls.model).filter_by(id=item_id)
        await session.execute(stmt)
        await session.commit()
        return exists_item
