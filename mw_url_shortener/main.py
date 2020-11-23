from pony.orm import Database, PrimaryKey, Required, db_session, commit
from typing import Optional, Dict, List

from fastapi import FastAPI
from pydantic import BaseModel
from starlette.responses import RedirectResponse, Response


db = Database()


class Redirect(db.Entity):
    short_link = PrimaryKey(str)
    url = Required(str)


db.bind(provider='sqlite', filename=':memory:')
db.generate_mapping(create_tables=True)

with db_session:
    redirect1 = Redirect(short_link="fJ3", url="https://google.com")
    redirect1 = Redirect(short_link="a", url="https://mw.je")
    commit()


@db_session()
def get_redirect(short_link: str) -> Response:
    redirect = Redirect.get(short_link=short_link)
    if redirect is None:
        return Response(content="<html><head></head><body>no redirect found</body></html>", status_code=404, media_type="text/html")
    return RedirectResponse(url=redirect.url)


app = FastAPI()


@app.get("/{short_link}")
async def redirect(short_link: str):
    return get_redirect(short_link=short_link)
