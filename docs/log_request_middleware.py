"""
I want to be able to log the request body, especially for non-matching
requests.

One easy way I can think of doing this so that ALL requests are handled, is by
adding a middleware that logs every request.

Unfortunately, the request body can't be read multiple times. This makes sense:
the request body is only sent by the client when an endpoing or middleware
tries to read it, and it's streamed directly to the part of the code that needs
it. This means even large request bodies can be handled without using a lot of
memory.

This also means the request body isn't stored by Starlette, so can't be
automatically read multiple times.

The middleware could keep a list of which endpoints use the request body in
which contexts, but I don't think that'd be maintainable.

Also, it looks like the BaseHTTPMiddleware can't be used without making
background tasks hang in some specific circumstances, and while I neither
encounter those circumstances, nor use background tasks, it's another reason to
not use a middleware, or at least not the one Starlette provides and describes
in their docs.
https://github.com/encode/starlette/issues/919
"""
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

        # hangs
        # print(f"---body: {await request.body()}---")

        print(f"response: {pformat(vars(response))}")
        print_methods(response)
        return response


async def root(request: "StarletteRequest") -> "StarletteResponse":
    print(f"---body: {await request.body()}---")
    return StarletteResponse(content=b"hello")


middleware = [
    Middleware(LogMiddleware),
]

all_methods = {
    "GET",
    "HEAD",
    "POST",
    "PUT",
    "DELETE",
    "CONNECT",
    "OPTIONS",
    "TRACE",
    "PATCH",
    "CUSTOM",
}

routes = [
    Route("/", root, methods=all_methods),
]

app = Starlette(routes=routes, middleware=middleware)


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
