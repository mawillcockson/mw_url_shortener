print(f"imported mw_url_shortener.server as {__name__}")
"""
Primarily uses https://fastapi.tiangolo.com/tutorial/
"""
import uvicorn
from fastapi import Depends, FastAPI, HTTPException, status, Body
from pydantic import BaseModel
import secrets
from typing import Optional, Dict, List
from starlette.responses import RedirectResponse, Response
from .random_chars import unsafe_random_chars
from getpass import getpass
from pathlib import Path

from fastapi import APIRouter, Depends
from .api.authentication import authorize
from .api import users, redirects

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

API_KEY = unsafe_random_chars(10)


app = FastAPI()


app.include_router(
        router,
        prefix=API_KEY,
        dependencies=[Depends(authentication.authenticate)],
)


@app.get("/{key:path}")
async def redirect(key: str):
    return get_redirect(key=key)


def run(reload: bool = False) -> None:
    """
    This needs to be updated to programmatically find the appropriate name of
    the module and function to run, istead of harcoding it to
    mw_url_shortener.server:app

    Also, this could be run behind an NGiNX proxy, or with gunicorn if there's no proxy:
    https://www.uvicorn.org/deployment/
    """
    username = input("Uername: ")
    hashed_password = hash_password(plain_password=getpass())
    with db_session:
        user = UserInDB.get(username=username)
        if not user:
            user = UserInDB(username=username, hashed_password=hashed_password)
        else:
            user.set(hashed_password=hashed_password)

    print(f"API key is:\n{API_KEY}")
    uvicorn.run("mw_url_shortener.server:app", reload=reload)
