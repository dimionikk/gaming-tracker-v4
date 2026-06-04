import asyncio
from contextlib import asynccontextmanager
from fastapi import FastAPI

from app.routers import leaderboard
from app.services.leaderboard import consume_sessions


@asynccontextmanager
async def lifespan(app: FastAPI):
    asyncio.create_task(consume_sessions())
    yield

app = FastAPI(title="Leaderboard Service", lifespan=lifespan)

app.include_router(leaderboard.router, prefix="/api/v1")


@app.get("/health")
async def health():
    return {"status": "ok"}