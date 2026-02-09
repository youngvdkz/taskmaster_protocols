from fastapi import FastAPI

from app.api.routers import audio, items, protocols
from app.core.db import Base, engine

app = FastAPI(title="Personal Protocol Manager API", redirect_slashes=False)

app.include_router(protocols.router, prefix="/api")
app.include_router(items.router, prefix="/api")
app.include_router(items.protocol_items_router, prefix="/api")
app.include_router(audio.router, prefix="/api")


@app.on_event("startup")
async def on_startup() -> None:
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}
