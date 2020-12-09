print(f"imported mw_url_shortener.database.entities as {__name__}")
from pony.orm import Database, PrimaryKey, Required
from . import db


class RedirectEntity(db.Entity):
    key = PrimaryKey(str)
    url = Required(str)

class UserEntity(db.Entity):
    username = PrimaryKey(str)
    hashed_password = Required(str)
