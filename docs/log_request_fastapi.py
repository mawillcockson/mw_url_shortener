# mypy: allow_any_expr
"""
I want to be able to log the request body, especially for non-matching
requests.

This is an adaptation of the recipe from the FastAPI docs:
https://fastapi.tiangolo.com/advanced/custom-request-and-route/#use-cases

The route handler isn't even requested when a request comes in that the router cannot match:
https://github.com/tiangolo/fastapi/blob/0.71.0/fastapi/routing.py#L186-L228
line 226-228 isn't run if the request doesn't match anything, or is invalid
"""
import asyncio
import inspect
from pprint import pformat, pprint
from typing import TYPE_CHECKING

import httpx
from fastapi import Body, FastAPI, Request, Response
from fastapi.exception_handlers import (
    http_exception_handler,
    request_validation_exception_handler,
)
from fastapi.exceptions import RequestValidationError
from fastapi.routing import APIRoute
from starlette.exceptions import HTTPException as StarletteHTTPException

if TYPE_CHECKING:
    from typing import Callable, Coroutine


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


async def root() -> str:
    return "hello"


class LoggingAPIRoute(APIRoute):
    def get_route_handler(
        self,
    ) -> "Callable[[Request], Coroutine[None, None, Response]]":
        original_route_handler = super().get_route_handler()

        async def log_request_handler(request: Request) -> Response:
            # contrary to the recipe in FastAPI,
            # starlette.requests.Request.body() already caches the request body
            body = await request.body()
            print(f"---body: {body!r}---")
            return await original_route_handler(request)

        return log_request_handler


app = FastAPI()
app.router.route_class = LoggingAPIRoute
app.get("/")(root)


async def main() -> None:
    async with httpx.AsyncClient(app=app, base_url="http://does-not-matter") as client:
        with open(__file__, "rb") as file:
            response = await client.post("/", files={"upload-file": file})
    print("something should have been printed before this line")


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
