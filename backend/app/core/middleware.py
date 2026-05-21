import uuid
import time
import logging
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from app.core.logger import request_id_ctx_var

logger = logging.getLogger(__name__)

class RequestContextMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # Allow correlation ID from incoming request headers
        request_id = request.headers.get("X-Request-ID") or request.headers.get("X-Correlation-ID") or str(uuid.uuid4())

        # Set the request ID in context
        token = request_id_ctx_var.set(request_id)

        start_time = time.time()

        try:
            response = await call_next(request)
            process_time = time.time() - start_time

            logger.info(
                "Request completed",
                extra={
                    "http_method": request.method,
                    "path": request.url.path,
                    "status_code": response.status_code,
                    "process_time_ms": round(process_time * 1000, 2),
                }
            )

            # Optionally add request ID to headers
            response.headers["X-Request-ID"] = request_id
            return response
        except Exception as e:
            process_time = time.time() - start_time
            logger.error(
                f"Request failed: {str(e)}",
                exc_info=True,
                extra={
                    "http_method": request.method,
                    "path": request.url.path,
                    "process_time_ms": round(process_time * 1000, 2),
                }
            )
            raise
        finally:
            request_id_ctx_var.reset(token)
