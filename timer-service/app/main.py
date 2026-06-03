from fastapi import FastAPI

from app.routers import timer

app = FastAPI(title="Timer Service")

app.include_router(timer.router, prefix="/api/v1")


@app.get("/health")
async def health():
    return {"status": "ok"}