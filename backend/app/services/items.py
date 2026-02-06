from __future__ import annotations

from sqlalchemy.ext.asyncio import AsyncSession

from app.storage.repositories import ItemRepository


class ItemService:
    def __init__(self, session: AsyncSession) -> None:
        self.repo = ItemRepository(session)
        self.session = session

    async def list(self, protocol_id: int):
        return await self.repo.list(protocol_id)

    async def create(self, protocol_id: int, title: str):
        items = await self.repo.list(protocol_id)
        order_index = len(items)
        item = await self.repo.create(protocol_id, title, order_index)
        await self.session.commit()
        return item

    async def rename(self, item_id: int, title: str):
        await self.repo.rename(item_id, title)
        await self.session.commit()

    async def delete(self, item_id: int):
        await self.repo.delete(item_id)
        await self.session.commit()

    async def reorder(self, ordered_ids: list[int]):
        await self.repo.reorder(ordered_ids)
        await self.session.commit()
