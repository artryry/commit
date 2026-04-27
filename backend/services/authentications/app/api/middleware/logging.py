import time

from fastapi import Request

from app.utils import Logger


async def logging_middleware(
    request: Request,
    call_next,
):

    start_time = time.time()

    Logger.info(
        f"Request started: "
        f"{request.method} {request.url.path}"
    )

    response = await call_next(request)

    process_time = (
        time.time() - start_time
    )

    Logger.info(
        f"Request ended: "
        f"{request.method} {request.url.path} "
        f"status={response.status_code} "
        f"time={process_time:.3f}s"
    )

    return response
