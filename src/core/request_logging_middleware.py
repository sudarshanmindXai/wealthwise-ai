import time
import uuid
import logging
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

logger = logging.getLogger("wealthwise.request")

class RequestLoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        request_id = request.headers.get("x-request-id") or str(uuid.uuid4())
        request.state.request_id = request_id

        start = time.time()
        try:
            response: Response = await call_next(request)
            duration_ms = int((time.time() - start) * 1000)

            logger.info(
                f"request_id={request_id} "
                f"method={request.method} "
                f"path={request.url.path} "
                f"status={response.status_code} "
                f"duration_ms={duration_ms}"
            )

            response.headers["x-request-id"] = request_id
            return response

        except Exception as e:
            duration_ms = int((time.time() - start) * 1000)
            logger.exception(
                f"request_id={request_id} "
                f"method={request.method} "
                f"path={request.url.path} "
                f"status=500 "
                f"duration_ms={duration_ms} "
                f"error={str(e)}"
            )
            raise