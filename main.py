from fastapi import FastAPI, Request
from fastapi.responses import Response
import requests
import logging

app = FastAPI()
TARGET_BASE = "https://maxit.orange.ma"

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger("proxy")

@app.api_route("/{full_path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS", "HEAD"])
async def proxy(full_path: str, request: Request):
    method = request.method
    body = await request.body()
    headers = dict(request.headers)

    # Prepare target URL
    url = f"{TARGET_BASE}/{full_path}"
    headers["host"] = "maxit.orange.ma"  # ensure host is correct

    # Log incoming request
    logger.debug(f"Incoming {method} request to /{full_path}")
    logger.debug(f"Headers: {headers}")
    logger.debug(f"Body: {body[:1000]}")

    try:
        # Forward request using requests
        response = requests.request(
            method=method,
            url=url,
            headers=headers,
            data=body,
            verify=False
        )

        # Log response info
        logger.debug(f"Received response with status {response.status_code}")
        logger.debug(f"Response headers: {response.headers}")
        logger.debug(f"Response body: {response.content[:1000]}")

        # Return response with same headers and body
        return Response(
            content=response.content,
            status_code=response.status_code,
            headers=dict(response.headers),
            media_type=response.headers.get("content-type")
        )

    except requests.RequestException as e:
        logger.error(f"Error forwarding request: {e}")
        return Response(content=f"Proxy error: {e}", status_code=502)
