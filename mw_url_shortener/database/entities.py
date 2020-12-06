from pony.orm import Database, PrimaryKey, Required, db_session, commit, select
from ..server.authentication import HashedPassword

class RedirectEntity(db.Entity):
    key = PrimaryKey(str)
    url = Required(str)

class UserEntity(db.Entity):
    username = PrimaryKey(str)
    hashed_password = Required(HashedPassword)
