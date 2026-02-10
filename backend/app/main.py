from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routers import audio, items, protocols
from app.core.db import Base, engine

app = FastAPI(title="Personal Protocol Manager API", redirect_slashes=False)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://taskmasterprotocols-production-fb71.up.railway.app",
        "https://taskmasterprotocols-production.up.railway.app",
        "http://localhost:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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
