from fastapi import FastAPI

from .v0 import api_router as api_router_v0
from .v0.redirect import match_redirect
from .v0.security import login_for_access_token

app = FastAPI()
app.include_router(api_router_v0, prefix="/v0")
app.post("/token")(login_for_access_token)
app.get("/{short_link:path}")(match_redirect)
