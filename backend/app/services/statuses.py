from __future__ import annotations

from sqlalchemy.ext.asyncio import AsyncSession

from app.storage.repositories import ItemRepository, ItemStatusRepository


class ItemStatusService:
    def __init__(self, session: AsyncSession) -> None:
        self.repo = ItemStatusRepository(session)
        self.item_repo = ItemRepository(session)
        self.session = session


    async def list_for_protocol(self, user_id: int, protocol_id: int):
        return await self.repo.list_for_protocol(user_id, protocol_id)

    async def toggle(self, user_id: int, protocol_id: int, item_id: int) -> bool:
        item = await self.item_repo.get(item_id)
        if item is None:
            return False
        status = await self.repo.get(user_id, protocol_id, item_id)
        new_value = not status.checked if status else True
        await self.repo.set_checked(user_id, protocol_id, item_id, new_value)
        await self.session.commit()
        return new_value

    async def reset_protocol(self, user_id: int, protocol_id: int) -> None:
        await self.repo.reset_for_protocol(user_id, protocol_id)
        await self.session.commit()
