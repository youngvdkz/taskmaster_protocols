from aiogram import F, Router
from aiogram.types import CallbackQuery, Message
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db import AsyncSessionLocal
from app.core.config import settings
from app.services.items import ItemService
from app.services.protocols import ProtocolService
from app.services.statuses import ItemStatusService
from app.storage.repositories import UserRepository
from bot.keyboards import items_keyboard, main_menu_keyboard, protocols_keyboard

router = Router()


async def _get_session() -> AsyncSession:
    async with AsyncSessionLocal() as session:
        yield session


@router.message(F.text == "/start")
async def start_handler(message: Message) -> None:
    async with AsyncSessionLocal() as session:
        await UserRepository(session).ensure(message.from_user.id, message.from_user.username)
        await session.commit()
    if not settings.webapp_url:
        await message.answer("Mini App URL is not set. Please configure WEBAPP_URL.")
        return
    await message.answer(
        "Welcome! Open the Mini App to manage protocols or use /protocols to run them.",
        reply_markup=main_menu_keyboard(settings.webapp_url, message.from_user.id),
    )


@router.message(F.text == "/protocols")
async def protocols_handler(message: Message) -> None:
    user_id = message.from_user.id
    async with AsyncSessionLocal() as session:
        await UserRepository(session).ensure(user_id, message.from_user.username)
        await session.commit()
        service = ProtocolService(session)
        protocols = await service.list(user_id)
    data = [(p.id, p.title) for p in protocols]
    await message.answer("Choose a protocol:", reply_markup=protocols_keyboard(data))


@router.message(F.text == "Protocols")
async def protocols_button_handler(message: Message) -> None:
    await protocols_handler(message)


@router.callback_query(F.data.startswith("p:"))
async def protocol_selected(call: CallbackQuery) -> None:
    user_id = call.from_user.id
    protocol_id = int(call.data.split(":")[1])
    async with AsyncSessionLocal() as session:
        status_service = ItemStatusService(session)
        item_service = ItemService(session)
        protocol_service = ProtocolService(session)
        await status_service.reset_protocol(user_id, protocol_id)
        items = await item_service.list(protocol_id)
        protocol = await protocol_service.get(protocol_id)
    data = [(i.id, i.title, False) for i in items]
    await call.message.delete()
    title = protocol.title if protocol else "Checklist"
    await call.message.answer(title, reply_markup=items_keyboard(data, protocol_id))


@router.callback_query(F.data.startswith("t:"))
async def toggle_item(call: CallbackQuery) -> None:
    parts = call.data.split(":")
    protocol_id = int(parts[1])
    item_id = int(parts[2])
    user_id = call.from_user.id

    async with AsyncSessionLocal() as session:
        status_service = ItemStatusService(session)
        item_service = ItemService(session)
        await status_service.toggle(user_id, protocol_id, item_id)
        items = await item_service.list(protocol_id)
        statuses = await status_service.list_for_protocol(user_id, protocol_id)

    status_map = {(s.item_id): s.checked for s in statuses}
    items_with_status = [(i.id, i.title, status_map.get(i.id, False)) for i in items]

    await call.message.edit_reply_markup(reply_markup=items_keyboard(items_with_status, protocol_id))
    await call.answer()
