from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class Protocol:
    id: int
    user_id: int
    title: str
    order_index: int


@dataclass(frozen=True)
class Item:
    id: int
    protocol_id: int
    title: str
    order_index: int


@dataclass(frozen=True)
class ItemStatus:
    user_id: int
    protocol_id: int
    item_id: int
    checked: bool
    updated_at: datetime
