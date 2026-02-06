from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db import get_session
from app.services.parser import ProtocolParser
from app.services.items import ItemService
from app.storage.repositories import ItemRepository


router = APIRouter(prefix="/items", tags=["items"])
protocol_items_router = APIRouter(prefix="/protocols", tags=["items"])


class ItemOut(BaseModel):
    id: int
    title: str
    order_index: int


class ItemCreate(BaseModel):
    title: str


class ItemRename(BaseModel):
    title: str


class ReorderRequest(BaseModel):
    ordered_ids: list[int]


class QuickItemsRequest(BaseModel):
    text: str


class QuickItemsResponse(BaseModel):
    items: list[ItemOut]


@protocol_items_router.get("/{protocol_id}/items")
async def list_items(protocol_id: int, session: AsyncSession = Depends(get_session)) -> list[ItemOut]:
    service = ItemService(session)
    items = await service.list(protocol_id)
    return [ItemOut(id=i.id, title=i.title, order_index=i.order_index) for i in items]


@protocol_items_router.post("/{protocol_id}/items")
async def create_item(protocol_id: int, payload: ItemCreate, session: AsyncSession = Depends(get_session)) -> ItemOut:
    service = ItemService(session)
    created = await service.create(protocol_id, payload.title)
    return ItemOut(id=created.id, title=created.title, order_index=created.order_index)


@protocol_items_router.post("/{protocol_id}/items/quick-create")
async def quick_create_items(
    protocol_id: int, payload: QuickItemsRequest, session: AsyncSession = Depends(get_session)
) -> QuickItemsResponse:
    parser = ProtocolParser()
    try:
        parsed = await parser.parse_items(payload.text)
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(status_code=422, detail={"error": str(exc), "text": payload.text}) from exc

    repo = ItemRepository(session)
    existing = await repo.list(protocol_id)
    start_index = len(existing)
    created_items = []
    for offset, title in enumerate(parsed.items):
        item = await repo.create(protocol_id, title, start_index + offset)
        created_items.append(ItemOut(id=item.id, title=item.title, order_index=item.order_index))
    await session.commit()
    return QuickItemsResponse(items=created_items)


@router.patch("/{item_id}")
async def rename_item(item_id: int, payload: ItemRename, session: AsyncSession = Depends(get_session)) -> None:
    service = ItemService(session)
    await service.rename(item_id, payload.title)


@router.delete("/{item_id}")
async def delete_item(item_id: int, session: AsyncSession = Depends(get_session)) -> None:
    service = ItemService(session)
    await service.delete(item_id)


@router.post("/reorder")
async def reorder_items(payload: ReorderRequest, session: AsyncSession = Depends(get_session)) -> None:
    service = ItemService(session)
    await service.reorder(payload.ordered_ids)
