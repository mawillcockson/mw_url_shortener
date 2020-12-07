print(f"imported mw_url_shortener.api.redirects as {__name__}")
"""
Manages the redirects portion of the API
"""
from fastapi import APIRouter
from ..database.interface import add_redirect
from ..database.models import Redirect
from ..database.entities import RedirectEntity


router = APIRouter()


@router.post("/", response_model=Redirect)
async def create(new_redirect: Redirect = Body(...)) -> RedirectEntity:
    return add_redirect(redirect=new_redirect)


@router.get("/")
async def read() -> None:
    raise NotImplementedError()


@router.patch("/")
async def update() -> None:
    raise NotImplementedError()


@router.delete("/")
async def delete() -> None:
    raise NotImplementedError()
