import asyncio
from fastapi import FastAPI
from contextlib import asynccontextmanager
from app.routers import stats
from app.services.stats import consume_sessions



@asynccontextmanager
async def lifespan(app: FastAPI):
    asyncio.create_task(consume_sessions())
    yield

app = FastAPI(title="Stats Service", lifespan=lifespan)
app.include_router(stats.router, prefix="/api/v1")

@app.get("/health")
async def health():
    return {"status": "ok"}