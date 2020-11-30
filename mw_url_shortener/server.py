"""
Primarily uses https://fastapi.tiangolo.com/tutorial/
"""
import uvicorn
from fastapi import Depends, FastAPI, HTTPException, status, Body
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from pydantic import BaseModel
import secrets
from pony.orm import Database, PrimaryKey, Required, db_session, commit, select
from typing import Optional, Dict, List
from starlette.responses import RedirectResponse, Response
from .random_chars import unsafe_rand_chars
from getpass import getpass
from passlib.context import CryptContext
from tempfile import NamedTemporaryFile
import atexit
from pathlib import Path


API_KEY = unsafe_rand_chars(10)
db = Database()
#db_file_raw = NamedTemporaryFile()
#atexit.register(db_file_raw.close)
#db_file = Path(db_file_raw.name)
db_file = Path("/tmp/shortener.sqlitedb")
db_file.touch()


class Redirect(BaseModel):
    key: str
    url: str


class RedirectInDB(db.Entity):
    key = PrimaryKey(str)
    url = Required(str)


class User(BaseModel):
    username: str
    hashed_password: str


class UserInDB(db.Entity):
    username = PrimaryKey(str)
    hashed_password = Required(str)


db.bind(provider="sqlite", filename=str(db_file), create_db=False)
db.generate_mapping(create_tables=True)


@db_session
def get_redirect(key: str) -> Response:
    redirect = RedirectInDB.get(key=key)
    if redirect is None:
        raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No redirect found",
            )
    return RedirectResponse(url=redirect.url)


@db_session
def add_redirect(redirect: Redirect) -> None:
    RedirectInDB(key=redirect.key, url=redirect.url)


@db_session
def get_user(username: str) -> Optional[User]:
    "Looks up user in the database, and builds a User model"
    user = UserInDB.get(username=username)
    if not user:
        return None

    return User(username=user.username, hashed_password=user.hashed_password)


app = FastAPI()


security = HTTPBasic()
password_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Copied from:
    https://fastapi.tiangolo.com/tutorial/security/oauth2-jwt/#hash-and-verify-the-passwords
    """
    return password_context.verify(plain_password, hashed_password)


def hash_password(plain_password: str) -> str:
    "Hashes a password with the current password context"
    return password_context.hash(plain_password)


async def authorize_user(credentials: HTTPBasicCredentials = Depends(security)) -> str:
    """
    Copied from:
    https://fastapi.tiangolo.com/advanced/security/http-basic-auth/#check-the-username

    # NOTE:FEATURE::SECURITY Apparently needs password hashing with salt
    """
    authentication_error = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Incorrect email or password",
        headers={"WWW-Authenticate": "Basic"},
    )
    user = get_user(credentials.username)
    if not user:
        raise authentication_error

    if not verify_password(plain_password=credentials.password, hashed_password=user.hashed_password):
        raise authentication_error

    return credentials.username


@app.post(f"/{API_KEY}/api/create_redirect", dependencies=[Depends(authorize_user)])
async def create_redirect(new_redirect: Redirect = Body(...)):
    return add_redirect(redirect=new_redirect)


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
