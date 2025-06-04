from fastapi import FastAPI, Request
from fastapi.responses import Response
import httpx

app = FastAPI()
TARGET_BASE = "https://maxit.orange.ma"

@app.api_route("/{full_path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS", "HEAD"])
async def proxy(full_path: str, request: Request):
    method = request.method
    url = f"{TARGET_BASE}/{full_path}"
    headers = dict(request.headers)
    body = await request.body()

    headers.pop("host", None)

    async with httpx.AsyncClient(verify=False) as client:
        try:
            forwarded = await client.request(
                method=method,
                url=url,
                headers=headers,
                content=body,
                timeout=30
            )
            return Response(
                content=forwarded.content,
                status_code=forwarded.status_code,
                headers=dict(forwarded.headers),
                media_type=forwarded.headers.get("content-type")
            )
        except httpx.RequestError as e:
            return Response(content=str(e), status_code=502)
