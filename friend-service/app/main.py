from fastapi import FastAPI

from app.routers import friend

app = FastAPI(title="Friend Service")

app.include_router(friend.router, prefix="/api/v1")


@app.get("/health")
async def health():
    return {"status": "ok"}