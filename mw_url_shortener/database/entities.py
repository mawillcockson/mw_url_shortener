print(f"imported mw_url_shortener.database.entities as {__name__}")
from pony.orm import Database, PrimaryKey, Required
from . import db
from .. import Uri, Key, Username, HashedPassword


class RedirectEntity(db.Entity):
    key = PrimaryKey(Key)
    url = Required(Uri)

class UserEntity(db.Entity):
    username = PrimaryKey(Username)
    hashed_password = Required(HashedPassword)
