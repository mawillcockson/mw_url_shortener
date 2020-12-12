print(f"imported mw_url_shortener.database.redirect as {__name__}")
"""
This file exists purely to export an organized namespace
"""
from .errors import RedirectNotFoundError
from .interface import create_redirect as create
from .interface import delete_redirect as delete
from .interface import get_redirect as get
from .interface import list_redirects as list
from .interface import new_redirect_key as new_key
from .interface import update_redirect as update
from .models import RedirectModel as Model
from ..types import Key, Uri
