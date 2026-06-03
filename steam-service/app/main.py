from fastapi import FastAPI

from app.routers import steam

app = FastAPI(title="Steam Service")

app.include_router(steam.router, prefix="/api/v1")


@app.get("/health")
async def health():
    return {"status": "ok"}