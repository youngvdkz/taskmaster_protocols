from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db import get_session
from app.services.parser import ProtocolParser
from app.services.protocols import ProtocolService
from app.storage.repositories import ItemRepository, ProtocolRepository, UserRepository
from app.api.routers.items import ItemOut


router = APIRouter(prefix="/protocols", tags=["protocols"])


class ProtocolOut(BaseModel):
    id: int
    title: str
    order_index: int


class ProtocolCreate(BaseModel):
    user_id: int
    title: str


class ProtocolRename(BaseModel):
    title: str


class ReorderRequest(BaseModel):
    ordered_ids: list[int]


class QuickCreateRequest(BaseModel):
    user_id: int
    text: str


class QuickCreateResponse(BaseModel):
    protocol: ProtocolOut
    items: list[ItemOut]


@router.get("/")
async def list_protocols(user_id: int, session: AsyncSession = Depends(get_session)) -> list[ProtocolOut]:
    service = ProtocolService(session)
    items = await service.list(user_id)
    return [ProtocolOut(id=p.id, title=p.title, order_index=p.order_index) for p in items]


@router.post("/")
async def create_protocol(payload: ProtocolCreate, session: AsyncSession = Depends(get_session)) -> ProtocolOut:
    service = ProtocolService(session)
    created = await service.create(payload.user_id, payload.title)
    return ProtocolOut(id=created.id, title=created.title, order_index=created.order_index)


@router.post("/quick-create")
async def quick_create(payload: QuickCreateRequest, session: AsyncSession = Depends(get_session)) -> QuickCreateResponse:
    try:
        parser = ProtocolParser()
        parsed = await parser.parse_protocol(payload.text)
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(status_code=422, detail={"error": str(exc), "text": payload.text}) from exc

    protocol_repo = ProtocolRepository(session)
    user_repo = UserRepository(session)
    item_repo = ItemRepository(session)

    await user_repo.ensure(payload.user_id)
    protocols = await protocol_repo.list(payload.user_id)
    protocol = await protocol_repo.create(payload.user_id, parsed.title, len(protocols))

    created_items = []
    for index, title in enumerate(parsed.items):
        item = await item_repo.create(protocol.id, title, index)
        created_items.append(ItemOut(id=item.id, title=item.title, order_index=item.order_index))

    await session.commit()
    return QuickCreateResponse(
        protocol=ProtocolOut(id=protocol.id, title=protocol.title, order_index=protocol.order_index),
        items=created_items,
    )


@router.patch("/{protocol_id}")
async def rename_protocol(protocol_id: int, payload: ProtocolRename, session: AsyncSession = Depends(get_session)) -> None:
    service = ProtocolService(session)
    await service.rename(protocol_id, payload.title)


@router.delete("/{protocol_id}")
async def delete_protocol(protocol_id: int, session: AsyncSession = Depends(get_session)) -> None:
    service = ProtocolService(session)
    await service.delete(protocol_id)


@router.post("/reorder")
async def reorder_protocols(payload: ReorderRequest, session: AsyncSession = Depends(get_session)) -> None:
    service = ProtocolService(session)
    await service.reorder(payload.ordered_ids)
