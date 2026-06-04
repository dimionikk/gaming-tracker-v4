import asyncio
from contextlib import asynccontextmanager
from fastapi import FastAPI

from app.routers import activity
from app.services.activity import consume_events


@asynccontextmanager
async def lifespan(app: FastAPI):
    asyncio.create_task(consume_events())
    yield

app = FastAPI(title="Activity Service", lifespan=lifespan)

app.include_router(activity.router, prefix="/api/v1")


@app.get("/health")
async def health():
    return {"status": "ok"}