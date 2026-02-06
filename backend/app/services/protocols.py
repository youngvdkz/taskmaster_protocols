from __future__ import annotations

from sqlalchemy.ext.asyncio import AsyncSession

from app.storage.repositories import ProtocolRepository, UserRepository


class ProtocolService:
    def __init__(self, session: AsyncSession) -> None:
        self.repo = ProtocolRepository(session)
        self.user_repo = UserRepository(session)
        self.session = session

    async def list(self, user_id: int):
        return await self.repo.list(user_id)

    async def create(self, user_id: int, title: str):
        await self.user_repo.ensure(user_id)
        protocols = await self.repo.list(user_id)
        order_index = len(protocols)
        protocol = await self.repo.create(user_id, title, order_index)
        await self.session.commit()
        return protocol

    async def rename(self, protocol_id: int, title: str):
        await self.repo.rename(protocol_id, title)
        await self.session.commit()

    async def delete(self, protocol_id: int):
        await self.repo.delete(protocol_id)
        await self.session.commit()

    async def reorder(self, ordered_ids: list[int]):
        await self.repo.reorder(ordered_ids)
        await self.session.commit()
