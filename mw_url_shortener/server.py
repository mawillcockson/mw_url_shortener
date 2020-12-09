print(f"imported mw_url_shortener.server as {__name__}")
"""
Primarily uses https://fastapi.tiangolo.com/tutorial/
"""
from fastapi import Depends, FastAPI, APIRouter, status, HTTPException
from starlette.responses import Response, RedirectResponse
from .database.interface import get_redirect
from typing import Union
from . import Key


ResponseOrException = Union[Response, HTTPException]


app = FastAPI()


@app.get("/{key:path}")
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

