import httpx
from fastapi import APIRouter, Request, Depends, HTTPException, status
from fastapi.responses import Response

from app.middleware.auth import verify_token
from app.core.config import settings

router = APIRouter()

http_client = httpx.AsyncClient()


async def proxy_request(request: Request, url: str, user_id: int = None) -> Response:
    headers = dict(request.headers)
    if user_id:
        headers["X-User-Id"] = str(user_id)

    body = await request.body()

    response = await http_client.request(
        method=request.method,
        url=url,
        headers=headers,
        content=body,
        params=request.query_params,
    )

    return Response(
        content=response.content,
        status_code=response.status_code,
        media_type=response.headers.get("content-type"),
    )


@router.api_route("/api/v1/auth/{path:path}", methods=["GET", "POST", "PUT", "DELETE"])
async def auth_proxy(request: Request, path: str):
    url = f"{settings.AUTH_SERVICE_URL}/api/v1/auth/{path}"
    return await proxy_request(request, url)

@router.api_route("/api/v1/users/{path:path}", methods=["GET", "POST", "PUT", "DELETE"])
async def users_proxy(request: Request, path: str, user_id: int = Depends(verify_token)):
    url = f"{settings.USER_SERVICE_URL}/api/v1/users/{path}"
    return await proxy_request(request, url, user_id)

@router.api_route("/api/v1/steam/{path:path}", methods=["GET", "POST", "PUT", "DELETE"])
async def steam_proxy(request: Request, path: str, user_id: int = Depends(verify_token)):
    url = f"{settings.STEAM_SERVICE_URL}/api/v1/steam/{path}"
    return await proxy_request(request, url, user_id)

@router.api_route("/api/v1/timer/{path:path}", methods=["GET", "POST", "PUT", "DELETE"])
async def timer_proxy(request: Request, path: str, user_id: int = Depends(verify_token)):
    url = f"{settings.TIMER_SERVICE_URL}/api/v1/timer/{path}"
    return await proxy_request(request, url, user_id)

@router.api_route("/api/v1/stats/{path:path}", methods=["GET", "POST", "PUT", "DELETE"])
async def stats_proxy(request: Request, path: str, user_id: int = Depends(verify_token)):
    url = f"{settings.STATS_SERVICE_URL}/api/v1/stats/{path}"
    return await proxy_request(request, url, user_id)