from __future__ import annotations

import httpx

from app.core.config import settings


async def transcribe_audio(file) -> str:
    if not settings.openai_api_key:
        raise RuntimeError("OPENAI_API_KEY is not set")

    headers = {"Authorization": f"Bearer {settings.openai_api_key}"}
    files = {"file": (file.filename, await file.read(), file.content_type or "application/octet-stream")}
    data = {"model": settings.openai_stt_model}

    async with httpx.AsyncClient(timeout=30) as client:
        resp = await client.post(
            "https://api.openai.com/v1/audio/transcriptions",
            headers=headers,
            files=files,
            data=data,
        )
        resp.raise_for_status()
        payload = resp.json()

    text = (payload.get("text") or "").strip()
    if not text:
        raise RuntimeError("Empty transcription")
    return text
