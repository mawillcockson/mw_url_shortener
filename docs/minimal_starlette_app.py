import asyncio
from typing import TYPE_CHECKING

import httpx
from starlette.applications import Starlette
from starlette.responses import Response as StarletteResponse
from starlette.routing import Route

if TYPE_CHECKING:
    from starlette.requests import Request as StarletteRequest


async def root(request: "StarletteRequest") -> "StarletteResponse":
    timeout = request.headers.get("Timeout", None)
    if timeout is not None:
        # For testing out graceful shutdowns
        # for hypercorn, use --graceful-timeout, default is 5 seconds
        for i in range(int(timeout), 0, -1):
            print(i)
            await asyncio.sleep(1)
    return StarletteResponse(content=b"hello")


all_methods = [
    "GET",
    "HEAD",
    "POST",
    "PUT",
    "DELETE",
    "CONNECT",
    "OPTIONS",
    "TRACE",
    "PATCH",
]

routes = [
    Route("/", root, methods=all_methods),
]

app = Starlette(routes=routes)


async def main() -> None:
    async with httpx.AsyncClient(
        app=app,
        base_url="http://does-not-matter",
        headers={
            "Timeout": "0",
        },
    ) as client:
        response = await client.get("/")
        print(response.text)


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
