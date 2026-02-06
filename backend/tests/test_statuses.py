import pytest

from app.services.items import ItemService
from app.services.protocols import ProtocolService
from app.services.statuses import ItemStatusService
from app.storage.repositories import UserRepository


@pytest.mark.asyncio
async def test_toggle_and_reset(db_session):
    await UserRepository(db_session).ensure(123, "tester")
    await db_session.commit()

    protocol = await ProtocolService(db_session).create(123, "Morning")
    item_service = ItemService(db_session)
    item1 = await item_service.create(protocol.id, "Water")
    item2 = await item_service.create(protocol.id, "Vitamins")

    status_service = ItemStatusService(db_session)
    checked = await status_service.toggle(123, protocol.id, item1.id)
    assert checked is True

    statuses = await status_service.list_for_protocol(123, protocol.id)
    status_map = {s.item_id: s.checked for s in statuses}
    assert status_map.get(item1.id) is True
    assert status_map.get(item2.id, False) is False

    await status_service.reset_protocol(123, protocol.id)
    statuses = await status_service.list_for_protocol(123, protocol.id)
    status_map = {s.item_id: s.checked for s in statuses}
    assert status_map.get(item1.id) is False
