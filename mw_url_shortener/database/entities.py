print(f"imported mw_url_shortener.database.entities as {__name__}")
from pony.orm import Database, PrimaryKey, Required

def get_db() -> Database:
    db = Database()


    class RedirectEntity(db.Entity):
        key = PrimaryKey(str)
        uri = Required(str)

    class UserEntity(db.Entity):
        username = PrimaryKey(str)
        hashed_password = Required(str)

    class ConfigEntity(db.Entity):
        version = PrimaryKey(str)
        json = Required(str)


    return db
