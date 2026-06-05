from fastapi import FastAPI

from app.routers import chat

app = FastAPI(title="Chat Service")

app.include_router(chat.router, prefix="/api/v1")


@app.get("/health")
async def health():
    return {"status": "ok"}