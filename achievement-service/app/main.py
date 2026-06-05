import asyncio
from contextlib import asynccontextmanager
from fastapi import FastAPI

from app.routers import achievement
from app.services.achievement import consume_events


@asynccontextmanager
async def lifespan(app: FastAPI):
    asyncio.create_task(consume_events())
    yield

app = FastAPI(title="Achievement Service", lifespan=lifespan)

app.include_router(achievement.router, prefix="/api/v1")


@app.get("/health")
async def health():
    return {"status": "ok"}