from __future__ import annotations

import json
from dataclasses import dataclass
import re

import httpx

from app.core.config import settings


@dataclass(frozen=True)
class ProtocolParseResult:
    title: str
    items: list[str]


@dataclass(frozen=True)
class ItemsParseResult:
    items: list[str]


class ProtocolParser:
    def __init__(self) -> None:
        if not settings.openai_api_key:
            raise RuntimeError("OPENAI_API_KEY is not set")
        self.api_key = settings.openai_api_key
        self.model = settings.openai_model

    async def _call_llm(self, system: str, user: str) -> dict:
        payload = {
            "model": self.model,
            "temperature": 0.2,
            "response_format": {"type": "json_object"},
            "messages": [
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
        }
        headers = {"Authorization": f"Bearer {self.api_key}"}
        async with httpx.AsyncClient(timeout=20) as client:
            resp = await client.post("https://api.openai.com/v1/chat/completions", json=payload, headers=headers)
            resp.raise_for_status()
            data = resp.json()
        content = data["choices"][0]["message"]["content"]
        return json.loads(content)

    async def parse_protocol(self, text: str) -> ProtocolParseResult:
        system = (
            "You are a parsing assistant. Return JSON only with keys: title (string), items (array of strings), "
            "fallback (boolean), reason (string). If you cannot infer a protocol, set fallback=true and explain reason. "
            "Rules: (1) If input is a short single phrase, treat it as PROTOCOL TITLE ONLY and return items=[]. "
            "(2) If input looks like a list of items without an explicit title, infer a concise title (1-3 words) "
            "that is not just the full list. (3) If input contains an explicit title delimiter like ':' or '—' or '- ', "
            "use the left part as title and parse the rest as items."
        )
        user = f"Parse this into a protocol:\n{text}"
        data = await self._call_llm(system, user)
        if data.get("fallback"):
            cleaned = text.strip()
            if cleaned and len(cleaned) <= 40 and len(cleaned.split()) <= 3:
                return ProtocolParseResult(title=cleaned, items=[])
            raise ValueError(data.get("reason", "Unable to parse"))
        title = (data.get("title") or "").strip()
        items = [i.strip() for i in (data.get("items") or []) if isinstance(i, str) and i.strip()]
        if not title and not items:
            raise ValueError("Unable to parse")
        # If short phrase and no items, keep title only.
        if not items and title:
            return ProtocolParseResult(title=title, items=[])
        # If items exist but title is empty or too long, infer a simple title.
        if items and (not title or _title_too_long(title, items)):
            title = _infer_title_from_items(items)
        return ProtocolParseResult(title=title, items=items)

    async def parse_items(self, text: str) -> ItemsParseResult:
        system = (
            "You are a parsing assistant. Return JSON only with keys: items (array of strings), "
            "fallback (boolean), reason (string). If you cannot infer items, set fallback=true and explain reason. "
            "If input is a single short phrase, return it as the only item."
        )
        user = f"Parse this into items:\n{text}"
        data = await self._call_llm(system, user)
        if data.get("fallback"):
            cleaned = text.strip()
            if cleaned and len(cleaned) <= 40 and len(cleaned.split()) <= 3:
                return ItemsParseResult(items=[cleaned])
            raise ValueError(data.get("reason", "Unable to parse"))
        items = [i.strip() for i in (data.get("items") or []) if isinstance(i, str) and i.strip()]
        if not items:
            raise ValueError("Unable to parse")
        return ItemsParseResult(items=items)


def _title_too_long(title: str, items: list[str]) -> bool:
    if len(title) > 40:
        return True
    if len(title.split()) > 4:
        return True
    # If title seems to contain multiple item words, treat as too long.
    words = set(re.findall(r"\\w+", title.lower()))
    overlap = sum(1 for item in items for w in re.findall(r"\\w+", item.lower()) if w in words)
    return overlap >= max(3, len(items))


def _infer_title_from_items(items: list[str]) -> str:
    first = items[0].strip()
    if len(items) == 1:
        return first[:40]
    return first if len(first.split()) <= 3 else "Checklist"
