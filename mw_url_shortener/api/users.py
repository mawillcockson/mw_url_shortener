print(f"imported mw_url_shortener.api.users as {__name__}")
"""
Manages the users portion of the API
"""
from fastapi import APIRouter

router_v1 = APIRouter()


@router_v1.post("/")
async def create() -> None:
    raise NotImplementedError()


@router_v1.get("/")
async def read() -> None:
    raise NotImplementedError()


@router_v1.patch("/")
async def update() -> None:
    raise NotImplementedError()


@router_v1.delete("/")
async def delete() -> None:
    raise NotImplementedError()
