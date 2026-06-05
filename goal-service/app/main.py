import asyncio
from contextlib import asynccontextmanager
from fastapi import FastAPI

from app.routers import goal
from app.services.goal import consume_sessions


@asynccontextmanager
async def lifespan(app: FastAPI):
    asyncio.create_task(consume_sessions())
    yield

app = FastAPI(title="Goal Service", lifespan=lifespan)

app.include_router(goal.router, prefix="/api/v1")


@app.get("/health")
async def health():
    return {"status": "ok"}