from __future__ import annotations

from collections.abc import Sequence
from datetime import datetime, timezone

from sqlalchemy import delete, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.storage import models


class ProtocolRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def list(self, user_id: int) -> Sequence[models.Protocol]:
        result = await self.session.execute(
            select(models.Protocol).where(models.Protocol.user_id == user_id).order_by(models.Protocol.order_index)
        )
        return result.scalars().all()

    async def create(self, user_id: int, title: str, order_index: int) -> models.Protocol:
        protocol = models.Protocol(user_id=user_id, title=title, order_index=order_index)
        self.session.add(protocol)
        await self.session.flush()
        return protocol

    async def rename(self, protocol_id: int, title: str) -> None:
        await self.session.execute(
            update(models.Protocol).where(models.Protocol.id == protocol_id).values(title=title)
        )

    async def delete(self, protocol_id: int) -> None:
        await self.session.execute(delete(models.Protocol).where(models.Protocol.id == protocol_id))

    async def reorder(self, ordered_ids: list[int]) -> None:
        for index, protocol_id in enumerate(ordered_ids):
            await self.session.execute(
                update(models.Protocol).where(models.Protocol.id == protocol_id).values(order_index=index)
            )


class ItemRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get(self, item_id: int) -> models.Item | None:
        result = await self.session.execute(select(models.Item).where(models.Item.id == item_id))
        return result.scalar_one_or_none()

    async def list(self, protocol_id: int) -> Sequence[models.Item]:
        result = await self.session.execute(
            select(models.Item)
            .where(models.Item.protocol_id == protocol_id)
            .order_by(models.Item.order_index)
        )
        return result.scalars().all()

    async def create(self, protocol_id: int, title: str, order_index: int) -> models.Item:
        item = models.Item(protocol_id=protocol_id, title=title, order_index=order_index)
        self.session.add(item)
        await self.session.flush()
        return item

    async def rename(self, item_id: int, title: str) -> None:
        await self.session.execute(update(models.Item).where(models.Item.id == item_id).values(title=title))

    async def delete(self, item_id: int) -> None:
        await self.session.execute(delete(models.Item).where(models.Item.id == item_id))

    async def reorder(self, ordered_ids: list[int]) -> None:
        for index, item_id in enumerate(ordered_ids):
            await self.session.execute(update(models.Item).where(models.Item.id == item_id).values(order_index=index))


class ItemStatusRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def list_for_protocol(self, user_id: int, protocol_id: int):
        result = await self.session.execute(
            select(models.ItemStatus).where(
                models.ItemStatus.user_id == user_id,
                models.ItemStatus.protocol_id == protocol_id,
            )
        )
        return result.scalars().all()

    async def get(self, user_id: int, protocol_id: int, item_id: int) -> models.ItemStatus | None:
        result = await self.session.execute(
            select(models.ItemStatus).where(
                models.ItemStatus.user_id == user_id,
                models.ItemStatus.protocol_id == protocol_id,
                models.ItemStatus.item_id == item_id,
            )
        )
        return result.scalar_one_or_none()

    async def set_checked(self, user_id: int, protocol_id: int, item_id: int, checked: bool) -> None:
        status = await self.get(user_id, protocol_id, item_id)
        if status is None:
            status = models.ItemStatus(
                user_id=user_id, protocol_id=protocol_id, item_id=item_id, checked=checked
            )
            self.session.add(status)
        else:
            status.checked = checked
            status.updated_at = datetime.now(timezone.utc)

    async def reset_for_protocol(self, user_id: int, protocol_id: int) -> None:
        await self.session.execute(
            update(models.ItemStatus)
            .where(
                models.ItemStatus.user_id == user_id,
                models.ItemStatus.protocol_id == protocol_id,
            )
            .values(checked=False, updated_at=datetime.now(timezone.utc))
        )


class UserRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get(self, tg_id: int) -> models.User | None:
        result = await self.session.execute(
            select(models.User).where(models.User.tg_id == tg_id)
        )
        return result.scalar_one_or_none()

    async def ensure(self, tg_id: int, username: str | None = None) -> models.User:
        user = await self.get(tg_id)
        if user is None:
            user = models.User(tg_id=tg_id, username=username)
            self.session.add(user)
            await self.session.flush()
        return user
