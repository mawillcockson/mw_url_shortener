from pony.orm import Database


db_file = Path("/tmp/shortener.sqlitedb")
db_file.touch()


db = Database()
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
