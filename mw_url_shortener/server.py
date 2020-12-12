print(f"imported mw_url_shortener.server as {__name__}")
"""
Primarily uses https://fastapi.tiangolo.com/tutorial/
"""
from typing import Union

from fastapi import APIRouter, Depends, FastAPI, HTTPException, status
from starlette.responses import RedirectResponse, Response

from . import Key
from .database.interface import get_redirect

ResponseOrException = Union[Response, HTTPException]


app_router = APIRouter()


@app_router.get("/{key:path}")
def redirect(key: Key) -> ResponseOrException:
    "returns a 30x redirect or 4xx error based on the given key"
    try:
        redirect = get_redirect(key)
    except KeyError as err:
        return HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No redirect found",
        )

    return RedirectResponse(url=redirect.url)


app = FastAPI()
