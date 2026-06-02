from fastapi import FastAPI

from app.routers import users

app = FastAPI(title="User Service")

app.include_router(users.router, prefix="/api/v1")


@app.get("/health")
async def health():
    return {"status": "ok"}