from fastapi import APIRouter, Depends, FastAPI
from .authentication import authorize
from . import users, redirects

api_router_v1 = APIRouter()


api_router_v1.include_router(
        users.router_v1,
        prefix="/users",
        tags=["users"],
)
api_router_v1.include_router(
        redirects.router_v1,
        prefix="/redirects",
        tags=["redirects"],
)


api_app_v1 = FastAPI(
        title="URL Shortener API",
        description="API for interacting with the URL shortener",
        version="1.0.0",
)


# NOTE:DOCS Should include help and description information for tags:
# https://fastapi.tiangolo.com/tutorial/metadata/#metadata-for-tags


api_app_v1.include_router(
        api_router_v1,
        prefix="/v1",
        dependencies=[Depends(authorize)],
)
