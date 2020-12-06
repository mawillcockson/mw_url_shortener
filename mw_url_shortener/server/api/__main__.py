"""
Contains the methods for the API

All of these require authentication, which is added by the __main__.py file
"""
from fastapi import APIRouter, Depends
from .authentication import authorize
from . import users, redirects

router = APIRouter()


router.include_router(
        users.router,
        prefix="/users",
        tags=["users"],
        dependencies=[Depends(authorize)],
)
router.include_router(
        redirects.router,
        prefix="/redirects",
        tags=["redirects"],
        dependencies=[Depends(authorize)],
)
