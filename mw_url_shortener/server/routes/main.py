from fastapi import FastAPI

from .v0 import api_router as api_router_v0
from .v0.redirect import match_redirect

app = FastAPI()
app.include_router(api_router_v0, prefix="/v0")
app.get("/{short_link:path}")(match_redirect)
