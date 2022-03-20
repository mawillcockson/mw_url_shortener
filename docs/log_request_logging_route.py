# mypy: allow_any_expr
"""
I want to be able to log the request body, especially for non-matching
requests.

This is an adaptation of the recipe from the FastAPI docs:
https://fastapi.tiangolo.com/tutorial/handling-errors/#re-use-fastapis-exception-handlers

Since this only logs errors, this would either have to be combined with a
logging route class that's called when nothing about the request is invalid, or
each endpoint would have to do the logging.

Here, the first option is demonstrated.
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

NUMBER_OF_LOGS: int = 0


async def root() -> str:
    return "hello"


async def exception() -> str:
    raise Exception("uh oh!")


class LoggingAPIRoute(APIRoute):
    def get_route_handler(
        self,
    ) -> "Callable[[Request], Coroutine[None, None, Response]]":
        original_route_handler = super().get_route_handler()

        async def log_request_handler(request: Request) -> Response:
            # contrary to the recipe in FastAPI,
            # starlette.requests.Request.body() already caches the request body
            body = await request.body()
            global NUMBER_OF_LOGS
            NUMBER_OF_LOGS += 1
            try:
                return await original_route_handler(request)
            except:
                print("ENDPOINT EXCEPTION")
                raise

        return log_request_handler


app = FastAPI()
# Setting the route class must come before adding any routes in  order for the
# custom route class to be used
app.router.route_class = LoggingAPIRoute
app.get("/")(root)
app.get("/exception")(exception)


async def logging_http_exception_handler(
    request: Request, exc: StarletteHTTPException
) -> Response:
    global NUMBER_OF_LOGS
    NUMBER_OF_LOGS += 1
    print("HTTP EXCEPTION")
    pprint(request.scope)
    return await http_exception_handler(request, exc)


async def custom_request_validation_exception_handler(
    request: Request, exc: RequestValidationError
) -> Response:
    global NUMBER_OF_LOGS
    NUMBER_OF_LOGS += 1
    print("REQUEST VALIDATION ERROR")
    pprint(request.scope)
    return await request_validation_exception_handler(request, exc)


app.exception_handler(StarletteHTTPException)(logging_http_exception_handler)
app.exception_handler(RequestValidationError)(
    custom_request_validation_exception_handler
)


async def main() -> None:
    async with httpx.AsyncClient(app=app, base_url="http://does-not-matter") as client:
        response = await client.get("/")  # 1
        with open(__file__, "rb") as file:
            response = await client.post("/", files={"upload-file": file})  # 2
        non_http_verb_request = client.build_request("NONHTTP", client.base_url)
        response = await client.send(non_http_verb_request)  # 3
        response = await client.head("/")  # 4
        response = await client.post("/")  # 5
        try:
            response = await client.get("/exception")  # 6
        except Exception as error:
            pass
        global NUMBER_OF_LOGS
        print(f"NUMBER_OF_LOGS: {NUMBER_OF_LOGS} == 6 -> {NUMBER_OF_LOGS == 6}")


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
