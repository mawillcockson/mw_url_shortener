print(f"imported mw_url_shortener.api.redirects as {__name__}")
"""
Manages the redirects portion of the API
"""
from fastapi import APIRouter, Body

from ..database.entities import RedirectEntity
from ..database.interface import add_redirect
from ..database.models import Redirect

router_v1 = APIRouter()


@router_v1.post("/", response_model=Redirect)
async def create(new_redirect: Redirect = Body(...)) -> RedirectEntity:
    return add_redirect(redirect=new_redirect)


@router_v1.get("/")
async def read() -> None:
    raise NotImplementedError()


@router_v1.patch("/")
async def update() -> None:
    raise NotImplementedError()


@router_v1.delete("/")
async def delete() -> None:
    raise NotImplementedError()
