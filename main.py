from fastapi import FastAPI, Request
from fastapi.responses import Response
import httpx
import logging

app = FastAPI()
TARGET_BASE = "https://maxit.orange.ma"

# Set up basic logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger("proxy")

@app.api_route("/{full_path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS", "HEAD"])
async def proxy(full_path: str, request: Request):
    method = request.method
    url = f"{TARGET_BASE}/{full_path}"
    headers = dict(request.headers)
    body = await request.body()

    # Log incoming request
    logger.debug(f"Incoming request:")
    logger.debug(f"  Method: {method}")
    logger.debug(f"  Path: /{full_path}")
    logger.debug(f"  Headers: {headers}")
    logger.debug(f"  Body: {body[:1000]}")  # limit log to 1000 bytes

    # Remove host header to avoid issues with target
    #headers.pop("host", None)

    async with httpx.AsyncClient(verify=False) as client:
        try:
            logger.debug(f"Forwarding to: {url}")
            forwarded = await client.request(
                method=method,
                url=url,
                headers=headers,
                content=body,
                timeout=30
            )

            logger.debug(f"Received response:")
            logger.debug(f"  Status Code: {forwarded.status_code}")
            logger.debug(f"  Headers: {dict(forwarded.headers)}")
            logger.debug(f"  Body: {forwarded.content[:1000]}")  # truncate for logging

            return Response(
                content=forwarded.content,
                status_code=forwarded.status_code,
                headers=dict(forwarded.headers),
                media_type=forwarded.headers.get("content-type")
            )
        except httpx.RequestError as e:
            logger.error(f"Request to {url} failed: {e}")
            return Response(content=f"Upstream request failed: {e}", status_code=502)
