"""
Manages the users portion of the API
"""
from fastapi import APIRouter


router = APIRouter()


@router.post("/")
async def create() -> None:
    raise NotImplementedError()


@router.get("/")
async def read() -> None:
    raise NotImplementedError()


@router.patch("/")
async def update() -> None:
    raise NotImplementedError()


@router.delete("/")
async def delete() -> None:
    raise NotImplementedError()
