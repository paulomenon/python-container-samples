"""FastAPI gateway: forwards /api/users/* and /api/products/* to backends."""
import os

import httpx
from fastapi import FastAPI, Request, Response

app = FastAPI(title="API Gateway")

USERS_BASE = os.environ.get("BACKEND_USERS_URL", "http://127.0.0.1:8001").rstrip("/")
PRODUCTS_BASE = os.environ.get("BACKEND_PRODUCTS_URL", "http://127.0.0.1:8002").rstrip("/")


async def _proxy(request: Request, backend_base: str, backend_path: str) -> Response:
    url = f"{backend_base}{backend_path}"
    if request.url.query:
        url = f"{url}?{request.url.query}"
    body = await request.body()
    headers = {k: v for k, v in request.headers.items() if k.lower() not in {"host", "content-length"}}
    async with httpx.AsyncClient(timeout=60.0) as client:
        r = await client.request(request.method, url, headers=headers, content=body)
    hop = {"content-encoding", "transfer-encoding", "content-length"}
    out_headers = {k: v for k, v in r.headers.items() if k.lower() not in hop}
    return Response(
        content=r.content,
        status_code=r.status_code,
        headers=out_headers,
        media_type=r.headers.get("content-type"),
    )


@app.api_route("/api/users", methods=["GET", "POST", "PUT", "PATCH", "DELETE"])
async def users_root(request: Request):
    return await _proxy(request, USERS_BASE, "/users")


@app.api_route("/api/users/{path:path}", methods=["GET", "POST", "PUT", "PATCH", "DELETE"])
async def users_sub(path: str, request: Request):
    return await _proxy(request, USERS_BASE, f"/users/{path}")


@app.api_route("/api/products", methods=["GET", "POST", "PUT", "PATCH", "DELETE"])
async def products_root(request: Request):
    return await _proxy(request, PRODUCTS_BASE, "/products")


@app.api_route("/api/products/{path:path}", methods=["GET", "POST", "PUT", "PATCH", "DELETE"])
async def products_sub(path: str, request: Request):
    return await _proxy(request, PRODUCTS_BASE, f"/products/{path}")
