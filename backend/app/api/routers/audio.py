from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from pydantic import BaseModel

from app.core.config import settings
from app.services.transcribe import transcribe_audio


router = APIRouter(prefix="/audio", tags=["audio"])


class TranscriptionResponse(BaseModel):
    text: str


@router.post("/transcribe")
async def transcribe(file: UploadFile = File(...)) -> TranscriptionResponse:
    if not settings.openai_api_key:
        raise HTTPException(status_code=500, detail="OPENAI_API_KEY is not set")
    if not file.filename:
        raise HTTPException(status_code=400, detail="No file provided")
    try:
        text = await transcribe_audio(file)
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(status_code=500, detail=str(exc)) from exc
    return TranscriptionResponse(text=text)
