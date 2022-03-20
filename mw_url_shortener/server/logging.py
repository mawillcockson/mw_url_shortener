from fastapi import Request, Response
from fastapi.exception_handlers import http_exception_handler as http_exception_handler
from fastapi.exception_handlers import (
    request_validation_exception_handler as request_validation_exception_handler,
)
from fastapi.exceptions import RequestValidationError as RequestValidationError
from fastapi.routing import APIRoute
from starlette.exceptions import HTTPException as HTTPException

from mw_url_shortener.interfaces.database import log

if TYPE_CHECKING:
    from typing import Callable, Coroutine


class LoggingAPIRoute(APIRoute):
    def get_route_handler(
        self,
    ) -> "Callable[[Request], Coroutine[None, None, Response]]":
        original_route_handler = super().get_route_handler()

        async def log_request_handler(request: Request) -> Response:
            "logs successfully matched requests"
            try:
                response = await original_route_handler(request)
            except Exception as error:
                await log.create_from_api_exception(request=request, exception=error)
                raise error

            await log.create_from_api_success(request=request, response=response)
            return response

        return log_request_handler


async def logging_http_exception_handler(
    request: Request, exc: HTTPException
) -> Response:
    await log.create_from_api_exception(request=request, exception=exc)
    return await http_exception_handler(request, exc)


async def custom_request_validation_exception_handler(
    request: Request, exc: RequestValidationError
) -> Response:
    await log.create_from_api_exception(request=request, exception=exc)
    return await request_validation_exception_handler(request, exc)
