print(f"imported mw_url_shortener.database.user as {__name__}")
"""
This file exists purely to export an organized namespace
"""
from .interface import create_user as create
from .interface import delete_user as delete
from .interface import get_user as get
from .interface import list_users as list
from .interface import update_user as update
from .models import UserModel as Model
