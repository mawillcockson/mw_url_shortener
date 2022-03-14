import asyncio
import inspect
from pprint import pformat
from typing import TYPE_CHECKING

import httpx
from starlette.applications import Starlette
from starlette.middleware import Middleware
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response as StarletteResponse
from starlette.routing import Route

if TYPE_CHECKING:
    from typing import Awaitable, Callable

    from starlette.requests import Request as StarletteRequest


def print_methods(obj: object) -> None:
    for attribute_name in dir(obj):
        if attribute_name in {"user", "auth", "session", "__dict__"}:
            continue
        attribute = getattr(obj, attribute_name)
        if inspect.ismethod(attribute):
            definition = "def"
            if inspect.iscoroutinefunction(attribute):
                definition = "async def"
            try:
                signature = str(inspect.signature(attribute)) + ":"
            except:
                signature = "():"
            print(f"  {definition} {attribute_name}{signature}")
            if attribute.__doc__:
                print(f'    """{attribute.__doc__}"""')


class LogMiddleware(BaseHTTPMiddleware):
    async def dispatch(
        self,
        request: "StarletteRequest",
        call_next: "Callable[[StarletteRequest], Awaitable[StarletteResponse]]",
    ) -> "StarletteResponse":
        print(f"request: {pformat(vars(request))}")
        print_methods(request)

        response = await call_next(request)

        print(f"response: {pformat(vars(response))}")
        print_methods(response)
        return response


async def root(request: "StarletteRequest") -> "StarletteResponse":
    print(f"body: {request.body()}")
    return StarletteResponse(content=b"hello")


middleware = [
    Middleware(LogMiddleware),
]

app = Starlette(routes=[Route("/", root)], middleware=middleware)


async def main() -> None:
    async with httpx.AsyncClient(app=app, base_url="http://does-not-matter") as client:
        response = await client.get("/")


if __name__ == "__main__":
    # alternatively, run
    # hypercorn \
    #     --access-logfile=- \
    #     --error-logfile=- \
    #     --debug \
    #     request_and_response:app
    #
    # then make a request with a browser or cli client
    asyncio.run(main())
