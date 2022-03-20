from typing import TYPE_CHECKING

from starlette.background import BackgroundTask, BackgroundTasks
from starlette.middleware.base import BaseHTTPMiddleware

from mw_url_shortener.interfaces.database import log

if TYPE_CHECKING:
    from typing import Awaitable, Callable

    from starlette.requests import Request as StarletteRequest
    from starlette.responses import Response as StarletteResponse


class LogMiddleware(BaseHTTPMiddleware):
    async def dispatch(
        self,
        request: "StarletteRequest",
        call_next: "Callable[[StarletteRequest], Awaitable[StarletteResponse]]",
    ) -> "StarletteResponse":
        response = await call_next(request)

        if response.background is None:
            # NOTE:TYPES::mypy mypy complains this statement is unreachable
            response.background = BackgroundTasks()  # type: ignore[unreachable]
        elif isinstance(response.background, BackgroundTask):  # type: ignore
            response.background = BackgroundTasks(tasks=[response.background])
        else:
            raise Exception(
                f"background task is '{type(response.background)} {response.background}', "
                "not BackgroundTask/BackgroundTasks"
            )
        response.background.add_task(log.create_from_response, response=response)  # type: ignore
        return response
