from fastapi import FastAPI

from app.routers import auth

app = FastAPI(title="Auth Service")

app.include_router(auth.router, prefix="/api/v1")


@app.get("/health")
async def health():
    return {"status": "ok"}